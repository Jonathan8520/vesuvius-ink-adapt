# Vesuvius Challenge : banc de mesure d'étiquettes d'encre à ~9 µm (docs/PLAN.md, étape 5).
#
# Affine le modèle scrollprize/ink_9um (poids MIT) avec le code du dépôt
# https://github.com/Jonathan8520/vesuvius-ink-adapt, sur des tuiles préparées par scripts/build_bench.py
# (jeu Kaggle privé). Les branches ne diffèrent que par la source des étiquettes ajoutées.
# Données CT : « Vesuvius Challenge - CT Scans of Herculaneum Papyri », CC BY-NC 4.0. Aucun rouleau éligible
# à First Letters. Tout est écrit dans /kaggle/working (log.txt, resume.json, runs_*.json).
import glob
import json
import os
import subprocess
import sys
import tarfile
import time

CONFIG = {
    "branch": "claude/jolly-shannon-2xycqz",
    "ckpt": "s43-75k",
    "arms": "base,C,T,H",
    "seeds": "0",
    "steps": 30,
    "lr": 0.002,
    "warmup": 10,
    "batch": 64,
    "eval_only": ["pherc0814-46527", "pherc0139-w016"],   # liste vide : tous les segments d'évaluation
}
WORK = os.environ.get("OUT_DIR", "/kaggle/working")
T0 = time.time()
LOG = open(os.path.join(WORK, "log.txt"), "a")


def log(*a):
    line = f"[{time.time() - T0:7.0f}s] " + " ".join(str(x) for x in a)
    print(line, flush=True)
    LOG.write(line + "\n")
    LOG.flush()


def sh(cmd):
    log("+", cmd)
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip():
        log(r.stdout.strip()[-2000:])
    if r.returncode:
        log("ÉCHEC", r.returncode, r.stderr.strip()[-2000:])
        raise SystemExit(1)


def find_bench():
    """Dossier du banc : /kaggle/input/<jeu>/ avec manifest.json, train/ et eval/ (ou leurs archives tar)."""
    hits = glob.glob("/kaggle/input/**/manifest.json", recursive=True)
    if not hits:
        log("contenu de /kaggle/input :", os.listdir("/kaggle/input") if os.path.isdir("/kaggle/input") else "absent")
        raise SystemExit("jeu de données du banc introuvable")
    root = os.path.dirname(hits[0])
    if os.path.isdir(os.path.join(root, "train")) and os.path.isdir(os.path.join(root, "eval")):
        return root
    local = "/tmp/bench"
    os.makedirs(local, exist_ok=True)
    for name in ("train", "eval"):
        tars = glob.glob(os.path.join(root, name + "*.tar")) + glob.glob(os.path.join(root, name, "*.tar"))
        log("extraction", tars)
        for t in tars:
            with tarfile.open(t) as f:
                f.extractall(os.path.join(local, name) if not any(m.startswith(name + "/") for m in f.getnames()[:3]) else local)
    os.system(f"cp {root}/manifest.json {local}/")
    return local


def main():
    import torch
    n_gpu = torch.cuda.device_count()
    log("torch", torch.__version__, "| GPU :", [torch.cuda.get_device_name(i) for i in range(n_gpu)] or "aucun")
    repo = os.path.join("/tmp", "repo")
    if not os.path.isdir(repo):
        sh(f"git clone -q --depth 1 -b {CONFIG['branch']} https://github.com/Jonathan8520/vesuvius-ink-adapt {repo}")
    sh(f"git -C {repo} log -1 --format=%h_%ad --date=short")
    bench = find_bench()
    log("banc :", bench, "| train", len(glob.glob(bench + "/train/*.npz")), "| eval", len(glob.glob(bench + "/eval/*.npz")))
    out = os.path.join(WORK, "results")
    os.makedirs(out, exist_ok=True)
    n = max(1, n_gpu)
    procs = []
    for i in range(n):
        cmd = [sys.executable, os.path.join(repo, "scripts", "run_bench.py"), "--bench", bench, "--out", out,
               "--ckpt", CONFIG["ckpt"], "--arms", CONFIG["arms"], "--seeds", CONFIG["seeds"],
               "--steps", str(CONFIG["steps"]), "--lr", str(CONFIG["lr"]), "--warmup", str(CONFIG["warmup"]),
               "--batch", str(CONFIG["batch"]), "--shard", f"{i}/{n}"]
        if CONFIG["eval_only"]:
            cmd += ["--eval-only"] + CONFIG["eval_only"]
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(i), CKPT_DIR="/tmp/ink_9um", PYTHONUNBUFFERED="1")
        log("lancement", i, " ".join(cmd[2:]))
        procs.append(subprocess.Popen(cmd, env=env, stdout=open(os.path.join(WORK, f"stdout_{i}.txt"), "w"), stderr=subprocess.STDOUT))
        time.sleep(20 if i == 0 else 0)   # le premier télécharge le checkpoint
    codes = [p.wait() for p in procs]
    log("codes de sortie", codes)
    for i in range(n):
        with open(os.path.join(WORK, f"stdout_{i}.txt")) as f:
            log(f"--- fin de la sortie {i}\n" + f.read()[-3000:])
    # fusion des résultats de tous les processus
    sys.path.insert(0, os.path.join(repo, "scripts"))
    import run_bench
    runs = [r for p in sorted(glob.glob(out + "/runs_*.json")) for r in json.load(open(p))]
    with open(os.path.join(WORK, "resume.json"), "w") as f:
        json.dump(dict(config=CONFIG, secondes=round(time.time() - T0), runs=len(runs), **run_bench.summarize(runs)), f, indent=1, ensure_ascii=False)
    with open(os.path.join(WORK, "runs.json"), "w") as f:
        json.dump(runs, f, indent=1, ensure_ascii=False)
    log("terminé,", len(runs), "branches")


if __name__ == "__main__":
    main()
