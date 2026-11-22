import sys, re, urllib.request, urllib.parse
B = "https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/"
def ls(prefix, delim="/", maxkeys=1000):
    q = {"list-type": "2", "prefix": prefix, "max-keys": str(maxkeys)}
    if delim: q["delimiter"] = delim
    out_p, out_k, token = [], [], None
    while True:
        if token: q["continuation-token"] = token
        x = urllib.request.urlopen(B + "?" + urllib.parse.urlencode(q), timeout=30).read().decode()
        out_p += re.findall(r"<CommonPrefixes><Prefix>([^<]+)</Prefix>", x)
        out_k += [(k, int(s)) for k, s in re.findall(r"<Key>([^<]+)</Key>.*?<Size>(\d+)</Size>", x, re.S)]
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", x)
        if not m: break
        token = m.group(1)
    return out_p, out_k
if __name__ == "__main__":
    for p in sys.argv[1:]:
        ps, ks = ls(p)
        print(f"## {p}  ({len(ps)} dossiers, {len(ks)} fichiers)")
        for x in ps[:40]: print("  D", x)
        for k, s in ks[:40]: print(f"  F {k}  {s/1e6:.2f} MB")
