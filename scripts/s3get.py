import sys, os, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from s3ls import ls, B
def get_prefix(prefix, dest_root, recursive=False):
    ps, ks = ls(prefix, delim=None if recursive else "/")
    n = 0
    for k, s in ks:
        out = os.path.join(dest_root, k)
        if os.path.exists(out) and os.path.getsize(out) == s: continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        urllib.request.urlretrieve(B + urllib.parse.quote(k), out); n += 1
    return n, len(ks)
if __name__ == "__main__":
    import urllib.parse
    dest = sys.argv[1]
    for p in sys.argv[2:]:
        rec = p.endswith("**")
        p = p.rstrip("*")
        print(p, get_prefix(p, dest, recursive=rec))
