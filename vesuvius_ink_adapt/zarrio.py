"""Lecture de tableaux Zarr distants par HTTP, sans dépendance à zarr-python.

Couvre les trois formats rencontrés dans les données publiques du Vesuvius Challenge :
- Zarr v2 non compressé (surfaces et volumes du bucket S3) ;
- Zarr v2 compressé avec Blosc (étiquettes `ink_9um` du bucket Hugging Face `scrollprize/datasets`) ;
- Zarr v3 avec sharding (étiquettes `ink-labels/<volume>/<date>/*.zarr` du bucket S3).

Seuls les chunks touchés par la zone demandée sont téléchargés. Un chunk absent vaut `fill_value`.
"""
import json
import re
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

import numcodecs
import numpy as np
import requests

S3 = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/"
HF_BUCKET = "https://huggingface.co/buckets/scrollprize/datasets/resolve/"
HF_TREE = "https://huggingface.co/api/buckets/scrollprize/datasets/tree/"
_SESSION = requests.Session()
_SESSION.mount("https://", requests.adapters.HTTPAdapter(pool_connections=64, pool_maxsize=64, max_retries=3))
_MISSING = 2 ** 64 - 1  # marqueur « chunk absent » de l'index d'un shard Zarr v3


def http_get(url, tries=6):
    """Contenu d'une URL, ou None si elle n'existe pas (403 et 404). Patiente en cas de limite de débit (429)."""
    for k in range(tries):
        try:
            r = _SESSION.get(url, timeout=120)
            if r.status_code in (403, 404):
                return None
            if r.status_code == 429:
                time.sleep(float(r.headers.get("retry-after", 20)) + 1)
                continue
            r.raise_for_status()
            return r.content
        except requests.RequestException:
            if k == tries - 1:
                raise
            time.sleep(2 * (k + 1))
    raise RuntimeError(f"limite de débit persistante sur {url}")


def hf_tree(prefix, recursive=True):
    """Liste un dossier du bucket Hugging Face : [(chemin, taille, empreinte)] pour les fichiers."""
    url = f"{HF_TREE}{prefix}?limit=1000&recursive={'true' if recursive else 'false'}"
    out = []
    while url:
        for k in range(6):
            r = _SESSION.get(url, timeout=120)
            if r.status_code != 429:
                break
            time.sleep(float(r.headers.get("retry-after", 20)) + 1)
        r.raise_for_status()
        out += [(e["path"], e.get("size"), e.get("xetHash")) for e in r.json() if e["type"] == "file"]
        m = re.search(r'<([^>]+)>;\s*rel="next"', r.headers.get("link", ""))
        url = m.group(1) if m else None
    return out


def _blosc(buf):
    return numcodecs.Blosc().decode(buf)


class RemoteArray:
    """Tableau Zarr distant (v2 ou v3 shardé) indexable par tranches : `a[z0:z1, y0:y1, x0:x1]`.

    url : adresse du tableau (dossier qui contient `.zarray` ou `zarr.json`), avec la barre finale.
    skip : ensemble de clés de chunks connus comme vides, à ne pas télécharger (utile sur Hugging Face, où le
           listing donne l'empreinte des chunks vides et où le nombre de requêtes est limité).
    """

    def __init__(self, url, max_chunks=512, threads=32, skip=None):
        self.url = url
        self.skip = skip or set()
        self.cache = OrderedDict()
        self.max_chunks = max_chunks
        self.lock = threading.Lock()
        self.pool = ThreadPoolExecutor(threads)
        self.downloaded = 0
        meta = http_get(url + ".zarray")
        if meta is not None:
            m = json.loads(meta)
            self.v3 = False
            self.shape = tuple(m["shape"])
            self.chunks = tuple(m["chunks"])
            self.dtype = np.dtype(m["dtype"])
            self.fill = m.get("fill_value") or 0
            self.sep = m.get("dimension_separator", ".")
            comp = m.get("compressor")
            assert comp is None or comp["id"] == "blosc", comp
            assert not m.get("filters") and m.get("order", "C") == "C", m
            self.compressed = comp is not None
            self.inner = None
        else:
            meta = http_get(url + "zarr.json")
            if meta is None:
                raise FileNotFoundError(url)
            m = json.loads(meta)
            assert m["node_type"] == "array", m["node_type"]
            self.v3 = True
            self.shape = tuple(m["shape"])
            self.chunks = tuple(m["chunk_grid"]["configuration"]["chunk_shape"])
            self.dtype = np.dtype(m["data_type"])
            self.fill = m.get("fill_value") or 0
            self.sep = m["chunk_key_encoding"]["configuration"].get("separator", "/")
            codecs = m["codecs"]
            if codecs[0]["name"] == "sharding_indexed":
                c = codecs[0]["configuration"]
                assert c.get("index_location", "end") == "end", c
                self.inner = tuple(c["chunk_shape"])
                names = [x["name"] for x in c["codecs"]]
            else:
                self.inner = None
                names = [x["name"] for x in codecs]
            assert names in (["bytes"], ["bytes", "blosc"]), names
            self.compressed = "blosc" in names
        self.ndim = len(self.shape)

    def _key(self, idx):
        body = self.sep.join(map(str, idx))
        return ("c" + self.sep + body) if self.v3 else body

    def _decode(self, data):
        if data is None:
            return np.full(self.chunks, self.fill, self.dtype)
        if self.inner is None:
            raw = _blosc(data) if self.compressed else data
            return np.frombuffer(raw, self.dtype).reshape(self.chunks)
        # shard Zarr v3 : chunks internes compressés bout à bout, puis index (offset, taille) et CRC32C à la fin
        grid = tuple(c // i for c, i in zip(self.chunks, self.inner))
        n = int(np.prod(grid))
        index = np.frombuffer(data[-(16 * n + 4):-4], "<u8").reshape(grid + (2,))
        out = np.full(self.chunks, self.fill, self.dtype)
        for pos in np.ndindex(*grid):
            off, size = (int(v) for v in index[pos])
            if off == _MISSING and size == _MISSING:
                continue
            raw = data[off:off + size]
            raw = _blosc(raw) if self.compressed else raw
            sl = tuple(slice(p * i, (p + 1) * i) for p, i in zip(pos, self.inner))
            out[sl] = np.frombuffer(raw, self.dtype).reshape(self.inner)
        return out

    def _fetch(self, idx):
        key = self._key(idx)
        data = None if key in self.skip else http_get(self.url + key)
        return idx, self._decode(data), len(data or b"")

    def _chunks_for(self, idxs):
        with self.lock:
            missing = [i for i in idxs if i not in self.cache]
        for idx, arr, nbytes in self.pool.map(self._fetch, missing):
            with self.lock:
                self.cache[idx] = arr
                self.downloaded += nbytes
        out = {}
        with self.lock:
            for i in idxs:
                self.cache.move_to_end(i)
                out[i] = self.cache[i]
            while len(self.cache) > self.max_chunks:
                self.cache.popitem(last=False)
        return out

    def __getitem__(self, key):
        if not isinstance(key, tuple):
            key = (key,)
        key = key + (slice(None),) * (self.ndim - len(key))
        lo, hi, squeeze = [], [], []
        for k, s in zip(key, self.shape):
            if isinstance(k, (int, np.integer)):
                k = int(k) + (s if k < 0 else 0)
                lo.append(k)
                hi.append(k + 1)
                squeeze.append(True)
            else:
                a, b, step = k.indices(s)
                assert step == 1, "pas de tranche à pas non unitaire"
                lo.append(a)
                hi.append(max(a, b))
                squeeze.append(False)
        out = np.full([h - l for l, h in zip(lo, hi)], self.fill, self.dtype)
        if out.size:
            rng = [range(l // c, (h - 1) // c + 1) for l, h, c in zip(lo, hi, self.chunks)]
            idxs = [tuple(i) for i in np.stack(np.meshgrid(*rng, indexing="ij"), -1).reshape(-1, self.ndim).tolist()]
            for idx, ch in self._chunks_for(idxs).items():
                c0 = [i * c for i, c in zip(idx, self.chunks)]
                s = [max(l, a) for l, a in zip(lo, c0)]
                e = [min(h, a + c) for h, a, c in zip(hi, c0, self.chunks)]
                dst = tuple(slice(a - l, b - l) for a, b, l in zip(s, e, lo))
                src = tuple(slice(a - o, b - o) for a, b, o in zip(s, e, c0))
                out[dst] = ch[src]
        return out[tuple(0 if q else slice(None) for q in squeeze)]
