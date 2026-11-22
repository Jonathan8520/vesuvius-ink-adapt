import sys, os, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s3ls import ls, B
def fetch(k, s, root):
    out = os.path.join(root, k)
    if os.path.exists(out) and os.path.getsize(out) == s: return 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = out + ".part"
    urllib.request.urlretrieve(B + urllib.parse.quote(k), tmp); os.replace(tmp, out); return s
def get_zarr_level(zbase, level, root, workers=16):
    for meta in [".zattrs", ".zgroup", f"{level}/.zarray"]:
        try: fetch(zbase + meta, -1, root)
        except Exception as e: pass
    _, ks = ls(zbase + f"{level}/", delim=None)
    with ThreadPoolExecutor(workers) as ex:
        tot = sum(ex.map(lambda kv: fetch(kv[0], kv[1], root), ks))
    return len(ks), tot
if __name__ == "__main__":
    root, zbase, level = sys.argv[1], sys.argv[2], sys.argv[3]
    n, tot = get_zarr_level(zbase, level, root)
    print(f"{n} chunks, {tot/1e6:.0f} MB téléchargés")
