"""Coeur de la chaîne : lecture du scan sur S3, rendu tifxyz (GPU ou CPU), modèle ink_9um réimplémenté.

Extrait du script Kaggle validé (kaggle/vesuvius_pherc1203_sweep.py). Conventions vérifiées :
- rendu : normale = -cross(d/dcol, d/drow) (signe de vc_render_tifxyz), décalages -14..13 (28 couches, indice 14 = surface)
- modèle : fenêtre de 17 couches, normalisation robuste par patch, patchs 128 pas 64, fusion de Hann
Voir docs/HANDOFF.md pour les chiffres de validation.
"""
import io
import json
import os
import re
import threading
import time
import urllib.parse
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import requests
import tifffile
import torch
import torch.nn as nn
import torch.nn.functional as F

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")
S3 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/"
HF = "https://huggingface.co/scrollprize/ink_9um/resolve/main/"
CKPT_DIR = os.environ.get("CKPT_DIR", os.path.expanduser("~/.cache/vesuvius_ink_adapt/ink_9um"))
OFFSETS = list(range(-14, 14))  # 28 couches ; indice 14 = surface
CKPTS = {
    "s43-20k": "hybrid_3d2d-seed43/step-020000.pth",
    "s43-60k": "hybrid_3d2d-seed43/step-060000.pth",
    "s42-75k": "hybrid_3d2d-seed42/step-075000.pth",
}
P = 128
STRIDE = 64
BATCH = 32
SESSION = requests.Session()
SESSION.mount("https://", requests.adapters.HTTPAdapter(pool_connections=64, pool_maxsize=64, max_retries=3))
_T0 = time.time()


def log(*a):
    print(f"[{(time.time() - _T0) / 60:6.1f} min] " + " ".join(str(x) for x in a), flush=True)


def http_get(url, tries=4):
    for k in range(tries):
        try:
            r = SESSION.get(url, timeout=120)
            if r.status_code in (403, 404):
                return None
            r.raise_for_status()
            return r.content
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))


def s3_list(prefix, delimiter="/"):
    q = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
    if delimiter:
        q["delimiter"] = delimiter
    prefixes, keys, token = [], [], None
    while True:
        if token:
            q["continuation-token"] = token
        x = http_get(S3 + "?" + urllib.parse.urlencode(q)).decode()
        prefixes += re.findall(r"<CommonPrefixes><Prefix>([^<]+)</Prefix>", x)
        keys += re.findall(r"<Key>([^<]+)</Key>", x)
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", x)
        if not m:
            return prefixes, keys
        token = m.group(1)


# ------------------------------------------------------------------ volume distant (chunks 128^3 bruts)
class RemoteVolume:
    def __init__(self, prefix, max_chunks=3000):
        self.prefix = prefix
        meta = json.loads(http_get(S3 + prefix + ".zarray"))
        assert meta.get("compressor") is None and meta["dtype"] == "|u1", meta
        self.shape = tuple(meta["shape"])
        self.chunks = tuple(meta["chunks"])
        self.sep = meta.get("dimension_separator", ".")
        self.cache = OrderedDict()
        self.max_chunks = max_chunks
        self.lock = threading.Lock()
        self.pool = ThreadPoolExecutor(32)
        self.downloaded = 0

    def _fetch(self, key):
        data = http_get(S3 + urllib.parse.quote(self.prefix + self.sep.join(map(str, key))))
        arr = np.zeros(self.chunks, np.uint8) if not data else np.frombuffer(data, np.uint8).reshape(self.chunks)
        return key, arr, len(data or b"")

    def get_chunks(self, keys):
        with self.lock:
            missing = [k for k in keys if k not in self.cache]
        for key, arr, nbytes in self.pool.map(self._fetch, missing):
            with self.lock:
                self.cache[key] = arr
                self.downloaded += nbytes
        out = {}
        with self.lock:
            for k in keys:
                self.cache.move_to_end(k)
                out[k] = self.cache[k]
            while len(self.cache) > self.max_chunks:
                self.cache.popitem(last=False)
        return out

    def block(self, lo, hi):
        lo = [max(0, int(v)) for v in lo]
        hi = [min(s, int(v)) for v, s in zip(hi, self.shape)]
        if any(h - l < 2 for l, h in zip(lo, hi)):
            return None, lo
        rng = [range(l // c, (h - 1) // c + 1) for l, h, c in zip(lo, hi, self.chunks)]
        keys = [(a, b, c) for a in rng[0] for b in rng[1] for c in rng[2]]
        chunks = self.get_chunks(keys)
        out = np.zeros([h - l for l, h in zip(lo, hi)], np.uint8)
        for key, ch in chunks.items():
            c0 = [k * c for k, c in zip(key, self.chunks)]
            s = [max(l, a) for l, a in zip(lo, c0)]
            e = [min(h, a + c) for h, a, c in zip(hi, c0, self.chunks)]
            out[s[0] - lo[0]:e[0] - lo[0], s[1] - lo[1]:e[1] - lo[1], s[2] - lo[2]:e[2] - lo[2]] = \
                ch[s[0] - c0[0]:e[0] - c0[0], s[1] - c0[1]:e[1] - c0[1], s[2] - c0[2]:e[2] - c0[2]]
        return out, lo


# ------------------------------------------------------------------ rendu tifxyz
def load_tifxyz(prefix):
    meta = json.loads(http_get(S3 + prefix + "meta.json"))
    g = np.stack([tifffile.imread(io.BytesIO(http_get(S3 + prefix + f"{a}.tif"))).astype(np.float64) for a in "xyz"], -1)
    valid = (g > 0).all(-1) & np.isfinite(g).all(-1)
    return g, valid, float(meta["scale"][0]), meta


def grid_normals(g, valid):
    dc = np.zeros_like(g)
    dr = np.zeros_like(g)
    dc[:, 1:-1] = (g[:, 2:] - g[:, :-2]) / 2
    dc[:, 0] = g[:, 1] - g[:, 0]
    dc[:, -1] = g[:, -1] - g[:, -2]
    dr[1:-1] = (g[2:] - g[:-2]) / 2
    dr[0] = g[1] - g[0]
    dr[-1] = g[-1] - g[-2]
    n = np.cross(dc, dr)
    n /= np.maximum(np.linalg.norm(n, axis=-1, keepdims=True), 1e-9)
    vv = valid.copy()
    vv[:, 1:-1] &= valid[:, 2:] & valid[:, :-2]
    vv[1:-1] &= valid[2:] & valid[:-2]
    return -n, vv  # signe de vc_render_tifxyz (vérifié contre un rendu officiel)


def bilinear(field, valid, rr, cc):
    hg, wg = valid.shape
    r0 = np.clip(np.floor(rr).astype(int), 0, hg - 2)
    c0 = np.clip(np.floor(cc).astype(int), 0, wg - 2)
    fr = (rr - r0)[..., None]
    fc = (cc - c0)[..., None]
    v = valid[r0, c0] & valid[r0 + 1, c0] & valid[r0, c0 + 1] & valid[r0 + 1, c0 + 1]
    val = (field[r0, c0] * (1 - fr) * (1 - fc) + field[r0 + 1, c0] * fr * (1 - fc)
           + field[r0, c0 + 1] * (1 - fr) * fc + field[r0 + 1, c0 + 1] * fr * fc)
    return val, v


def render(g, valid, scale, vol, offsets=OFFSETS, tile=256, roi=None):
    n, nvalid = grid_normals(g, valid)
    H, W = int(round(g.shape[0] / scale)), int(round(g.shape[1] / scale))
    r0, r1, c0, c1 = roi if roi else (0, H, 0, W)
    L = len(offsets)
    out = np.zeros((L, r1 - r0, c1 - c0), np.uint8)
    offs = torch.tensor(offsets, dtype=torch.float32, device=DEV)
    for ta in range(r0, r1, tile):
        for tb in range(c0, c1, tile):
            ha, hb = min(tile, r1 - ta), min(tile, c1 - tb)
            rr, cc = np.meshgrid(np.arange(ta, ta + ha) * scale, np.arange(tb, tb + hb) * scale, indexing="ij")
            pos, pv = bilinear(g, valid, rr, cc)
            nor, nv = bilinear(n, valid & nvalid, rr, cc)
            ok = pv & nv
            if not ok.any():
                continue
            nor /= np.maximum(np.linalg.norm(nor, axis=-1, keepdims=True), 1e-9)
            sel_p, sel_n = pos[ok], nor[ok]
            ext = np.concatenate([sel_p + offsets[0] * sel_n, sel_p + offsets[-1] * sel_n])
            lo = np.floor(ext.min(0))[::-1] - 1  # z, y, x
            hi = np.ceil(ext.max(0))[::-1] + 2
            blk, lo_i = vol.block(lo, hi)
            if blk is None:
                continue
            bt = torch.from_numpy(blk).to(DEV, dtype=torch.float32)[None, None]  # (1,1,D,H,W)
            D, Hb, Wb = blk.shape
            p = torch.from_numpy(sel_p).to(DEV, dtype=torch.float32)
            q = torch.from_numpy(sel_n).to(DEV, dtype=torch.float32)
            pts = p[None] + offs[:, None, None] * q[None]  # (L, N, 3) en x, y, z
            gx = 2 * (pts[..., 0] - lo_i[2]) / (Wb - 1) - 1
            gy = 2 * (pts[..., 1] - lo_i[1]) / (Hb - 1) - 1
            gz = 2 * (pts[..., 2] - lo_i[0]) / (D - 1) - 1
            grid = torch.stack([gx, gy, gz], -1)[None, :, :, None, :]  # (1, L, N, 1, 3)
            smp = F.grid_sample(bt, grid, mode="bilinear", padding_mode="zeros", align_corners=True)[0, 0, :, :, 0]
            res = np.zeros((L, ha, hb), np.uint8)
            res[:, ok] = torch.clamp(torch.round(smp), 0, 255).to(torch.uint8).cpu().numpy()
            out[:, ta - r0:ta - r0 + ha, tb - c0:tb - c0 + hb] = res
    return out


# ------------------------------------------------------------------ réseau (poids scrollprize/ink_9um)
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


FEATS, BLOCKS, STRIDES = [32, 64, 128, 256, 320, 320], [1, 3, 4, 6, 6, 6], [1, 2, 2, 2, 2, 2]


class Encoder(nn.Module):
    def __init__(self):
        super().__init__()
        self.stem = StackedConv(32, FEATS[0])
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
        self.transpconvs = nn.ModuleList([nn.ConvTranspose2d(FEATS[-(s + 1)], FEATS[-(s + 2)], 2, 2) for s in range(n - 1)])
        self.stages = nn.ModuleList([StackedConv(2 * FEATS[-(s + 2)], FEATS[-(s + 2)]) for s in range(n - 1)])

    def forward(self, skips):
        x = skips[-1]
        for s in range(len(self.stages)):
            x = self.stages[s](torch.cat((self.transpconvs[s](x), skips[-(s + 2)]), 1))
        return x


class Net2D(nn.Module):
    def __init__(self):
        super().__init__()
        self.shared_encoder = Encoder()
        self.shared_decoder = Decoder()
        self.task_heads = nn.ModuleDict({"ink": nn.Conv2d(FEATS[0], 1, 1)})

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


def load_model(name):
    path = os.path.join(CKPT_DIR, CKPTS[name].replace("/", "__"))
    if not os.path.exists(path):
        os.makedirs(CKPT_DIR, exist_ok=True)
        log("téléchargement", name)
        with SESSION.get(HF + CKPTS[name], stream=True, timeout=600) as r:
            r.raise_for_status()
            with open(path + ".part", "wb") as f:
                for b in r.iter_content(1 << 22):
                    f.write(b)
        os.replace(path + ".part", path)
    ck = torch.load(path, map_location="cpu", weights_only=True)
    m = InkModel()
    m.load_state_dict({k: v for k, v in ck["model"].items() if ".all_modules." not in k}, strict=True)
    return m.to(DEV).eval()


# ------------------------------------------------------------------ inférence
def robust_norm_t(x):
    """Normalisation robuste par patch : clip p1/p99, (x - médiane) / (1.4826 * MAD)."""
    B = x.shape[0]
    f = x.reshape(B, -1)
    std = f.std(dim=1, unbiased=False)
    q = torch.quantile(f, torch.tensor([0.01, 0.99], device=f.device), dim=1)
    lo, hi = q[0], q[1]
    c = torch.minimum(torch.maximum(f, lo[:, None]), hi[:, None])
    med = torch.quantile(c, 0.5, dim=1)
    mad = torch.quantile((c - med[:, None]).abs(), 0.5, dim=1)
    scale = 1.4826 * mad
    half = (hi - lo) / 2
    alt = torch.where(std >= 1e-6, std, torch.where(half >= 1e-6, half, torch.ones_like(std)))
    scale = torch.where(torch.isfinite(scale) & (scale >= 1e-6), scale, alt)
    return ((c - med[:, None]) / scale[:, None]).reshape(x.shape)


def positions(length, patch, stride):
    if length <= patch:
        return [0]
    p = list(range(0, length - patch + 1, stride))
    if p[-1] != length - patch:
        p.append(length - patch)
    return p


HANN = None


def infer(vol, model, start, reverse, depth=17):
    global HANN
    if HANN is None:
        w = torch.outer(torch.hann_window(P, periodic=False), torch.hann_window(P, periodic=False))
        HANN = torch.clamp(w / w.max(), min=0.001).to(DEV)
    idx = list(range(start, start + depth))
    sub = torch.from_numpy(np.ascontiguousarray(vol[idx])).to(DEV)
    if reverse:
        sub = sub.flip(0)
    H, W = sub.shape[1:]
    if H < P or W < P:
        sub = F.pad(sub, (0, max(0, P - W), 0, max(0, P - H)))
    Hp, Wp = sub.shape[1:]
    center = sub[depth // 2] > 0
    tiles = [(y, x) for y in positions(Hp, P, STRIDE) for x in positions(Wp, P, STRIDE)
             if center[y:y + P, x:x + P].float().mean().item() >= 0.05]
    acc = torch.zeros(Hp, Wp, device=DEV)
    wsum = torch.zeros(Hp, Wp, device=DEV)
    with torch.no_grad():
        for b in range(0, len(tiles), BATCH):
            bt = tiles[b:b + BATCH]
            xs = torch.stack([sub[:, y:y + P, x:x + P] for y, x in bt]).float()
            prob = torch.sigmoid(model(robust_norm_t(xs)[:, None]).float())[:, 0]
            for k, (y, x) in enumerate(bt):
                acc[y:y + P, x:x + P] += prob[k] * HANN
                wsum[y:y + P, x:x + P] += HANN
    out = torch.where(wsum > 0, acc / wsum.clamp(min=1e-6), torch.zeros_like(acc))[:H, :W]
    return out.cpu().numpy(), len(tiles)
