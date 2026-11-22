"""Affinage court du modèle `ink_9um` sur les tuiles du banc (`scripts/build_bench.py`), et notation.

Recette abrégée, calée sur celle de l'équipe (`configs/aligned21_hybrid_3d2d.json` de ScrollPrize/villa, MIT) :
SGD de Nesterov (momentum 0,99, décroissance 3e-5), cosinus avec échauffement, BCE lissée (0,5) plus Dice,
toutes deux limitées au masque de supervision, écrêtage du gradient à 1, fenêtre de 17 couches décalée de ±2,
normalisation robuste par patch, quotas fixes par rouleau dans chaque lot.

Ce n'est pas la recette complète de l'équipe : les augmentations sont réduites (symétries, rotations de 90°,
transposition, gain, décalage, bruit, flou, inversion). Toutes les branches d'une comparaison partagent la même
recette ; seule la source des étiquettes ajoutées change.
"""
import glob
import json
import os
import time

import numpy as np
import torch
import torch.nn.functional as F

from . import core

P, DEPTH = 128, 17
TILE = 256


# ------------------------------------------------------------------ données
class Pack:
    """Tuiles d'une représentation : images (n, L, 256, 256) uint8 et masques 2D par version d'étiquettes."""

    def __init__(self, path):
        z = np.load(path)
        self.name = os.path.basename(path)[:-4]
        self.img = z["img"]
        self.masks = {k: np.unpackbits(z[k], axis=-1)[..., :TILE].astype(bool) for k in z.files if k not in ("img", "yx", "shape")}

    def labels(self, version):
        """(ink, sup) pour la version demandée : "h" = étiquettes humaines, "t" = carte du modèle 2 µm seuillée."""
        if version == "t" and "ink_t" in self.masks:
            return self.masks["ink_t"], self.masks["sup_t"]
        return self.masks["ink"], self.masks["sup"]


def scroll_key(name):
    """Clé de quota : un rouleau du corpus de l'équipe, ou le nom du segment pour les segments ajoutés."""
    for key, tag in (("phercparis4", "Paris4"), ("pherc1667", "1667"), ("pherc0814", "0814"), ("pherc0139", "0139"), ("natif-w", "0139")):
        if name.startswith(key):
            return tag
    return name


class Sampler:
    """Tire des patchs 17 x 128 x 128 avec un nombre fixe de patchs par groupe dans chaque lot."""

    def __init__(self, packs, quotas, versions, seed):
        self.rng = np.random.default_rng(seed)
        self.quotas = dict(quotas)
        self.groups = {}
        for p in packs:
            key = scroll_key(p.name)
            if key not in self.quotas:
                continue
            ink, sup = p.labels(versions.get(p.name, "h"))
            w = sup.reshape(len(sup), -1).sum(1).astype(np.float64)
            for i in np.nonzero(w >= 256)[0]:
                self.groups.setdefault(key, []).append((p, int(i), ink, sup, w[i]))
        missing = [k for k in self.quotas if k not in self.groups]
        assert not missing, f"groupes sans tuiles : {missing}"
        self.prob = {k: np.array([t[4] for t in v]) / sum(t[4] for t in v) for k, v in self.groups.items()}

    def _one(self, key):
        p, i, ink, sup, _ = self.groups[key][self.rng.choice(len(self.groups[key]), p=self.prob[key])]
        for _ in range(8):
            y, x = self.rng.integers(0, TILE - P + 1, 2)
            if sup[i, y:y + P, x:x + P].sum() >= 64:
                break
        else:  # tuile peu supervisée : centrer sur un pixel supervisé
            ys, xs = np.nonzero(sup[i])
            k = self.rng.integers(len(ys))
            y, x = int(np.clip(ys[k] - P // 2, 0, TILE - P)), int(np.clip(xs[k] - P // 2, 0, TILE - P))
        L = p.img.shape[1]
        z = int(np.clip(L // 2 - DEPTH // 2 + self.rng.integers(-2, 3), 0, L - DEPTH))
        return p.img[i, z:z + DEPTH, y:y + P, x:x + P], ink[i, y:y + P, x:x + P], sup[i, y:y + P, x:x + P]

    def batch(self):
        items = [self._one(k) for k, n in self.quotas.items() for _ in range(n)]
        img, ink, sup = (np.stack([it[j] for it in items]) for j in range(3))
        return torch.from_numpy(img), torch.from_numpy(ink), torch.from_numpy(sup)


# ------------------------------------------------------------------ augmentations et perte
def augment(x, ink, sup, gen):
    """x (B, 17, 128, 128) normalisé ; symétries par échantillon, puis intensité."""
    B = x.shape[0]
    r = lambda: torch.rand(B, device=x.device, generator=gen)
    for dim in (2, 3):
        m = r() < 0.5
        if m.any():
            x[m], ink[m], sup[m] = x[m].flip(dim), ink[m].flip(dim - 1), sup[m].flip(dim - 1)
    m = r() < 0.5
    if m.any():
        x[m], ink[m], sup[m] = x[m].transpose(2, 3), ink[m].transpose(1, 2), sup[m].transpose(1, 2)
    v = lambda: [B, 1, 1, 1]
    gain = torch.where(r() < 0.3, 0.75 + 0.5 * r(), torch.ones(B, device=x.device)).view(v())
    shift = torch.where(r() < 0.3, 0.3 * (r() - 0.5), torch.zeros(B, device=x.device)).view(v())
    x = x * gain + shift
    noise = torch.where(r() < 0.3, 0.2 * r(), torch.zeros(B, device=x.device)).view(v())
    x = x + noise * torch.randn(x.shape, device=x.device, generator=gen)
    m = r() < 0.3
    if m.any():
        x[m] = F.avg_pool2d(x[m], 3, 1, 1)
    m = r() < 0.1
    if m.any():
        x[m] = -x[m]
    return x, ink, sup


def loss_fn(logits, ink, sup, smoothing=0.5):
    y, m = ink.float(), sup.float()
    target = y * (1 - smoothing) + 0.5 * smoothing
    bce = (F.binary_cross_entropy_with_logits(logits, target, reduction="none") * m).sum() / m.sum().clamp(min=1e-8)
    p = torch.sigmoid(logits) * m
    inter, den = (p * y).sum((1, 2)), p.sum((1, 2)) + (y * m).sum((1, 2))
    dice = ((2 * inter + 1) / (den + 1)).mean()
    return bce + (1 - dice)


# ------------------------------------------------------------------ notation
def scores(prob, ink):
    """Précision équilibrée et F1 au seuil 0,5, AUC ; sur des vecteurs de pixels."""
    pred, n = prob >= 0.5, len(ink)
    tp, tn = int((pred & ink).sum()), int((~pred & ~ink).sum())
    pos, neg = int(ink.sum()), int((~ink).sum())
    order = np.argsort(prob, kind="stable")
    ranks = np.empty(n)
    ranks[order] = np.arange(1, n + 1)
    auc = (ranks[ink].sum() - pos * (pos + 1) / 2) / max(1, pos * neg)
    return dict(px=n, encre=round(pos / max(1, n), 3), ba=round(0.5 * (tp / max(1, pos) + tn / max(1, neg)), 4),
                f1=round(2 * tp / max(1, 2 * tp + (int(pred.sum()) - tp) + (pos - tp)), 4), auc=round(float(auc), 4))


def evaluate(model, eval_dir, only=None):
    """Note le modèle sur chaque segment d'évaluation (grille de tuiles officielle, fenêtre centrée, sens direct)."""
    model.eval()
    by_seg = {}
    for path in sorted(glob.glob(os.path.join(eval_dir, "*.npz"))):
        seg = os.path.basename(path).rsplit("_", 1)[0]
        if only and seg not in only:
            continue
        z = np.load(path)
        img, (y0, y1, x0, x1), (H, W) = z["img"], z["roi"], z["shape"]
        ink = np.unpackbits(z["ink"], axis=-1)[:, :x1 - x0].astype(bool)
        mask = np.unpackbits(z["mask"], axis=-1)[:, :x1 - x0].astype(bool)
        ys, xs = np.nonzero(mask)
        roi = (y0 + ys.min(), y0 + ys.max() + 1, x0 + xs.min(), x0 + xs.max() + 1)   # boîte serrée des pixels notés

        def read(a, b, c, d):
            assert y0 <= a and b <= y1 and x0 <= c and d <= x1, ("zone trop petite", (a, b, c, d), (y0, y1, x0, x1))
            return img[:, a - y0:b - y0, c - x0:d - x0]

        prob, _ = core.infer_roi(read, (int(H), int(W)), roi, model, core.center_window(img.shape[0]))
        sl = (slice(roi[0] - y0, roi[1] - y0), slice(roi[2] - x0, roi[3] - x0))
        m = mask[sl]
        by_seg.setdefault(seg, []).append((prob[m], ink[sl][m]))
    return {seg: scores(np.concatenate([p for p, _ in v]), np.concatenate([y for _, y in v])) for seg, v in by_seg.items()}


# ------------------------------------------------------------------ affinage
def finetune(model, sampler, steps, lr=0.002, warmup=100, seed=0, log_every=50, log=print):
    dev = next(model.parameters()).device
    amp = dev.type == "cuda"
    opt = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.99, nesterov=True, weight_decay=3e-5)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: (s + 1) / warmup if s < warmup else
                                              0.5 * (1 + np.cos(np.pi * (s - warmup) / max(1, steps - warmup))))
    scaler = torch.amp.GradScaler(enabled=amp)
    gen = torch.Generator(device=dev).manual_seed(seed)
    model.train()
    curve, t0, run = [], time.time(), 0.0
    for step in range(steps):
        img, ink, sup = (t.to(dev) for t in sampler.batch())
        x = torch.cat([core.robust_norm_t(c) for c in img.float().split(32)])   # torch.quantile est limité à 2^24 éléments
        x, ink, sup = augment(x, ink, sup, gen)
        with torch.autocast(dev.type, dtype=torch.float16, enabled=amp):
            logits = model(x[:, None]).float()[:, 0]
        loss = loss_fn(logits, ink, sup)
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        sched.step()
        run += float(loss.detach())
        if (step + 1) % log_every == 0 or step + 1 == steps:
            n = (step % log_every) + 1
            curve.append((step + 1, round(run / n, 4)))
            log(f"pas {step + 1}/{steps} perte {run / n:.4f} {(time.time() - t0) / (step + 1):.2f} s/pas")
            run = 0.0
    model.eval()
    return curve


def run_arm(bench, ckpt, arm, seed, steps, quotas, versions, lr=0.002, warmup=100, packs=None, log=print, eval_only=None):
    """Une branche : part du checkpoint, affine, note. `versions` : nom du pack -> "h" ou "t"."""
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = core.load_model(ckpt)
    t0, curve = time.time(), []
    if steps:
        packs = packs if packs is not None else load_packs(bench, quotas)
        curve = finetune(model, Sampler(packs, quotas, versions, seed), steps, lr=lr, warmup=warmup, seed=seed, log=log)
    res = evaluate(model, os.path.join(bench, "eval"), eval_only)
    return dict(branche=arm, graine=seed, pas=steps, lr=lr, quotas=quotas, versions=versions, courbe=curve,
                secondes=round(time.time() - t0), scores=res), model


def load_packs(bench, quotas):
    packs = []
    for path in sorted(glob.glob(os.path.join(bench, "train", "*.npz"))):
        if scroll_key(os.path.basename(path)[:-4]) in quotas:
            packs.append(Pack(path))
    return packs


def save_json(path, obj):
    with open(path + ".part", "w") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    os.replace(path + ".part", path)
