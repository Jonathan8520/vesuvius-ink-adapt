# Vesuvius Challenge : banc de mesure d'étiquettes d'encre à ~9 µm (rapport docs/label-source-comparison.md).
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
    # Branches : base = checkpoint publié ; C = témoin ; T = carte du modèle 2 µm dans l'empreinte humaine ;
    # H = étiquettes humaines ; D = carte du modèle 2 µm sur toute la surface, sans choix humain.
    # Les travaux tournent l'un après l'autre ; chacun écrit dans results/<nom>.
    "jobs": None,               # rempli par PRESET ci-dessous
    "steps": 1000,
    "lr": 0.002,
    "warmup": 100,
    "batch": 64,
    "eval_at": "250,500",       # notations intermédiaires
    "eval_only": [],            # liste vide : tous les segments d'évaluation
}
# Lots de travaux déjà lancés (journal, entrée A8). Pour lancer un lot, changer PRESET puis pousser.
PRESETS = {
    "pretest": [{"nom": "pretest", "ckpt": "s43-75k", "arms": "base,C,T,H", "seeds": "0,1,2,3,4"}],
    "dense": [{"nom": "dense", "ckpt": "s43-75k", "arms": "D", "seeds": "0,1,2,3,4"}],
    "robust": [{"nom": "D-s43", "ckpt": "s43-75k", "arms": "D", "seeds": "0,2,4"},          # complète D à 5 graines
               {"nom": "s42", "ckpt": "s42-75k", "arms": "base,C,T,H", "seeds": "0,1,2"}],   # second checkpoint de départ
    "shift": [{"nom": "S-s43", "ckpt": "s43-75k", "arms": "S", "seeds": "0,1,2,3,4"}],     # carte non recalée
}
PRESET = "robust"
CONFIG["jobs"] = PRESETS[PRESET]
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
    n = max(1, n_gpu)
    sys.path.insert(0, os.path.join(repo, "scripts"))
    import run_bench
    allruns = []
    for job in CONFIG["jobs"]:
        out = os.path.join(WORK, "results", job["nom"])
        os.makedirs(out, exist_ok=True)
        procs = []
        for i in range(n):
            cmd = [sys.executable, os.path.join(repo, "scripts", "run_bench.py"), "--bench", bench, "--out", out,
                   "--ckpt", job["ckpt"], "--arms", job["arms"], "--seeds", job["seeds"],
                   "--steps", str(CONFIG["steps"]), "--lr", str(CONFIG["lr"]), "--warmup", str(CONFIG["warmup"]),
                   "--batch", str(CONFIG["batch"]), "--shard", f"{i}/{n}", "--eval-at", CONFIG.get("eval_at", "")]
            if CONFIG["eval_only"]:
                cmd += ["--eval-only"] + CONFIG["eval_only"]
            env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(i), CKPT_DIR="/tmp/ink_9um", PYTHONUNBUFFERED="1")
            log("lancement", job["nom"], i, " ".join(cmd[2:]))
            procs.append(subprocess.Popen(cmd, env=env, stdout=open(os.path.join(WORK, f"stdout_{job['nom']}_{i}.txt"), "w"),
                                          stderr=subprocess.STDOUT))
            time.sleep(30 if i == 0 else 0)   # le premier télécharge le checkpoint
        codes = [p.wait() for p in procs]
        log("codes de sortie", job["nom"], codes)
        for i in range(n):
            with open(os.path.join(WORK, f"stdout_{job['nom']}_{i}.txt")) as f:
                log(f"--- fin de la sortie {job['nom']} {i}\n" + f.read()[-3000:])
        runs = [r for p in sorted(glob.glob(out + "/runs_*.json")) for r in json.load(open(p))]
        for r in runs:
            r["travail"] = job["nom"]
        allruns += runs
        with open(os.path.join(WORK, f"resume_{job['nom']}.json"), "w") as f:
            json.dump(dict(travail=job, secondes=round(time.time() - T0), runs=len(runs), **run_bench.summarize(runs)), f, indent=1, ensure_ascii=False)
    runs = allruns
    with open(os.path.join(WORK, "resume.json"), "w") as f:
        json.dump(dict(config=CONFIG, secondes=round(time.time() - T0), runs=len(runs)), f, indent=1, ensure_ascii=False)
    with open(os.path.join(WORK, "runs.json"), "w") as f:
        json.dump(runs, f, indent=1, ensure_ascii=False)
    log("terminé,", len(runs), "branches")


if __name__ == "__main__":
    main()
