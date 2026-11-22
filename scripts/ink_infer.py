"""Inférence d'encre (CPU, version autonome ; la version de référence est vesuvius_ink_adapt/core.py) avec les poids scrollprize/ink_9um, réseau réécrit ici.

Aucun code téléchargé n'est exécuté : l'architecture (pile 3D de fusion en profondeur
+ U-Net 2D à encodeur résiduel) est réimplémentée d'après le dépôt villa, et les poids
sont chargés avec torch.load(weights_only=True) puis vérifiés en strict=True.

Conventions reprises de vesuvius.ink_detection.inference.infer :
- fenêtre de 17 couches centrée (ou --layer-start/--layer-end), option --reverse
- normalisation robuste par patch (clip p1/p99, médiane, 1.4826*MAD)
- patchs 128x128, pas de 64, fusion pondérée par une fenêtre de Hann
"""
from __future__ import annotations

import argparse
import time

import numpy as np
import tifffile
import torch
import zarr
from torch import nn


# ---------------------------------------------------------------- réseau
class ConvNormAct(nn.Module):
    def __init__(self, cin, cout, k=3, stride=1, bias=True, act=True):
        super().__init__()
        self.conv = nn.Conv2d(cin, cout, k, stride, padding=(k - 1) // 2, bias=bias)
        self.norm = nn.InstanceNorm2d(cout, eps=1e-5, affine=True)
        self.act = nn.LeakyReLU(0.01, inplace=True) if act else nn.Identity()

    def forward(self, x):
        return self.act(self.norm(self.conv(x)))


class StackedConv(nn.Module):
    def __init__(self, cin, cout):
        super().__init__()
        self.convs = nn.Sequential(ConvNormAct(cin, cout, 3))

    def forward(self, x):
        return self.convs(x)


class BasicBlockD(nn.Module):
    def __init__(self, cin, cout, stride):
        super().__init__()
        self.conv1 = ConvNormAct(cin, cout, 3, stride)
        self.conv2 = ConvNormAct(cout, cout, 3, 1, act=False)
        ops = []
        if stride != 1:
            ops.append(nn.AvgPool2d(stride, stride))
        if cin != cout:
            ops.append(ConvNormAct(cin, cout, 1, 1, bias=False, act=False))
        self.skip = nn.Sequential(*ops) if ops else None
        self.act = nn.LeakyReLU(0.01, inplace=True)

    def forward(self, x):
        r = self.skip(x) if self.skip is not None else x
        return self.act(self.conv2(self.conv1(x)) + r)


class Stage(nn.Module):
    def __init__(self, n, cin, cout, stride):
        super().__init__()
        self.blocks = nn.Sequential(BasicBlockD(cin, cout, stride), *[BasicBlockD(cout, cout, 1) for _ in range(n - 1)])

    def forward(self, x):
        return self.blocks(x)


FEATS = [32, 64, 128, 256, 320, 320]
BLOCKS = [1, 3, 4, 6, 6, 6]
STRIDES = [1, 2, 2, 2, 2, 2]


class Encoder(nn.Module):
    def __init__(self, cin=32):
        super().__init__()
        self.stem = StackedConv(cin, FEATS[0])
        stages, c = [], FEATS[0]
        for n, f, s in zip(BLOCKS, FEATS, STRIDES):
            stages.append(Stage(n, c, f, s))
            c = f
        self.stages = nn.Sequential(*stages)

    def forward(self, x):
        x = self.stem(x)
        skips = []
        for st in self.stages:
            x = st(x)
            skips.append(x)
        return skips


class Decoder(nn.Module):
    def __init__(self):
        super().__init__()
        n = len(FEATS)
        self.transpconvs = nn.ModuleList(
            [nn.ConvTranspose2d(FEATS[-(s + 1)], FEATS[-(s + 2)], 2, 2, bias=True) for s in range(n - 1)])
        self.stages = nn.ModuleList([StackedConv(2 * FEATS[-(s + 2)], FEATS[-(s + 2)]) for s in range(n - 1)])

    def forward(self, skips):
        x = skips[-1]
        for s in range(len(self.stages)):
            x = self.transpconvs[s](x)
            x = torch.cat((x, skips[-(s + 2)]), 1)
            x = self.stages[s](x)
        return x


class Net2D(nn.Module):
    def __init__(self):
        super().__init__()
        self.shared_encoder = Encoder(32)
        self.shared_decoder = Decoder()
        self.task_heads = nn.ModuleDict({"ink": nn.Conv2d(FEATS[0], 1, 1, bias=True)})

    def forward(self, x):
        return self.task_heads["ink"](self.shared_decoder(self.shared_encoder(x)))


class DepthFusion(nn.Module):
    def __init__(self, ch=16):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv3d(1, ch, 3, padding=1, bias=False), nn.InstanceNorm3d(ch, affine=True), nn.LeakyReLU(0.01, inplace=True),
            nn.Conv3d(ch, ch, 3, padding=1, bias=False), nn.InstanceNorm3d(ch, affine=True), nn.LeakyReLU(0.01, inplace=True))
        self.attention_logits = nn.Conv3d(ch, 1, 1)

    def forward(self, x):
        f = self.features(x)
        w = torch.softmax(self.attention_logits(f).float(), dim=2)
        return torch.cat([(f * w.to(f.dtype)).sum(dim=2), f.amax(dim=2)], dim=1)


class InkModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = Net2D()
        self.depth_fusion = DepthFusion(16)

    def forward(self, x):
        return self.network(self.depth_fusion(x))


def load_model(path):
    ck = torch.load(path, map_location="cpu", weights_only=True)
    sd = {k: v for k, v in ck["model"].items() if ".all_modules." not in k}
    m = InkModel()
    m.load_state_dict(sd, strict=True)
    m.eval()
    return m, int(ck["config"]["patch_size"][0])


# ---------------------------------------------------------------- inférence
def robust_norm(patch):
    v = patch.astype(np.float32)
    flat = v.reshape(-1)
    std = float(flat.std())
    lo, hi = np.percentile(flat, [1.0, 99.0])
    v = np.clip(v, lo, hi)
    c = np.clip(flat, lo, hi)
    med = float(np.median(c))
    scale = 1.4826 * float(np.median(np.abs(c - med)))
    if not (np.isfinite(scale) and scale >= 1e-6):
        scale = std if std >= 1e-6 else ((hi - lo) / 2 if (hi - lo) / 2 >= 1e-6 else 1.0)
    return ((v - med) / scale).astype(np.float32)


def hann2d(n):
    w = np.outer(np.hanning(n), np.hanning(n)).astype(np.float32)
    return np.maximum(w / max(w.max(), 1e-6), 0.001)


def positions(length, patch, stride):
    if length <= patch:
        return [0]
    p = list(range(0, length - patch + 1, stride))
    if p[-1] != length - patch:
        p.append(length - patch)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zarr_level0")
    ap.add_argument("checkpoint")
    ap.add_argument("out_tif")
    ap.add_argument("--layer-start", type=int)
    ap.add_argument("--layer-end", type=int)
    ap.add_argument("--reverse", action="store_true")
    ap.add_argument("--crop", type=int, nargs=4, metavar=("Y0", "Y1", "X0", "X1"))
    ap.add_argument("--stride", type=int, default=64)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--min-valid", type=float, default=0.05)
    ap.add_argument("--max-seconds", type=float, default=540)
    a = ap.parse_args()

    model, depth = load_model(a.checkpoint)
    vol = zarr.open(a.zarr_level0, mode="r")
    L = vol.shape[0]
    idx = np.arange(0 if a.layer_start is None else a.layer_start, L if a.layer_end is None else a.layer_end)
    if idx.size > depth:
        s = idx.size // 2 - depth // 2
        idx = idx[s:s + depth]
    if a.reverse:
        idx = idx[::-1]
    y0, y1, x0, x1 = a.crop if a.crop else (0, vol.shape[1], 0, vol.shape[2])
    sub = np.asarray(vol[int(idx.min()):int(idx.max()) + 1, y0:y1, x0:x1])[idx - idx.min()]
    H, W = sub.shape[1:]
    P = 128
    acc = np.zeros((H, W), np.float32)
    wsum = np.zeros((H, W), np.float32)
    win = hann2d(P)
    tiles = [(ty, tx) for ty in positions(H, P, a.stride) for tx in positions(W, P, a.stride)]
    tiles = [(ty, tx) for ty, tx in tiles if (sub[depth // 2, ty:ty + P, tx:tx + P] > 0).mean() >= a.min_valid]
    print(f"couches {idx.tolist()} | zone {H}x{W} | {len(tiles)} patchs", flush=True)
    t0 = time.time()
    done = 0
    with torch.inference_mode():
        for b in range(0, len(tiles), a.batch):
            batch = tiles[b:b + a.batch]
            arr = []
            for ty, tx in batch:
                t = sub[:, ty:ty + P, tx:tx + P]
                if t.shape[1] < P or t.shape[2] < P:
                    t = np.pad(t, ((0, 0), (0, P - t.shape[1]), (0, P - t.shape[2])))
                arr.append(robust_norm(t))
            prob = model(torch.from_numpy(np.stack(arr)[:, None])).float().sigmoid()[:, 0].numpy()
            for (ty, tx), p in zip(batch, prob):
                h, w = min(P, H - ty), min(P, W - tx)
                acc[ty:ty + h, tx:tx + w] += p[:h, :w] * win[:h, :w]
                wsum[ty:ty + h, tx:tx + w] += win[:h, :w]
            done += len(batch)
            el = time.time() - t0
            if b == 0 or (b // a.batch) % 20 == 0:
                print(f"  {done}/{len(tiles)} patchs, {el:.0f} s (~{el / done * (len(tiles) - done):.0f} s restantes)", flush=True)
            if el > a.max_seconds:
                print(f"  arrêt au bout de {el:.0f} s ({done}/{len(tiles)} patchs)", flush=True)
                break
    out = np.where(wsum > 0, acc / np.maximum(wsum, 1e-6), 0.0).astype(np.float32)
    np.save(a.out_tif.replace(".tif", "_raw.npy"), out.astype(np.float16))
    disp = np.clip((out - 0.25) / 0.5, 0, 1)  # affichage conseillé par la fiche du modèle
    tifffile.imwrite(a.out_tif, (disp * 255).astype(np.uint8))
    print(f"fini en {time.time() - t0:.0f} s -> {a.out_tif}", flush=True)


if __name__ == "__main__":
    main()
