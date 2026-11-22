# vesuvius-ink-adapt

Run the [Vesuvius Challenge](https://scrollprize.org) 9 µm ink-detection pipeline anywhere, including on a free
Kaggle GPU: stream a scroll's CT volume from the public bucket, render any `tifxyz` surface, and run the
[`scrollprize/ink_9um`](https://huggingface.co/scrollprize/ink_9um) models, with no C++ build and no local GPU.

**Status (22 November 2026).** The November sprint (label-free adaptation of `ink_9um`) was stopped: a prior-art
survey showed that every step of that plan had already been published by others, often with negative results
([`docs/RESEARCH.md`](docs/RESEARCH.md), in French).

**New goal:** publish hand-verified ink labels at ~9 µm by the end of December 2026, together with a labelling
tool that works with a stylus on a tablet and a measurement of what the labels bring to a model. Hand-corrected
labels already exist for PHerc0814, PHerc0841 and PHerc0009B (Priyank Aranke); we target objects where only
model-derived labels exist. Plan: [`docs/PLAN.md`](docs/PLAN.md). Inventory of scans and existing labels:
[`docs/INVENTAIRE.md`](docs/INVENTAIRE.md). No labels are ever made on a scroll eligible for the First Letters
prize.

One observation recorded in [`docs/HANDOFF.md`](docs/HANDOFF.md): six of the nine reserved validation zones of
`ink_9um` are missing from the 9 µm label release but are public on the open-data bucket
(`scripts/audit_reserved_validation.py`).

## What works today

| Component | Check against the official tools | Result |
| --- | --- | --- |
| Surface rendering from the remote OME-Zarr volume (GPU via `grid_sample`, or CPU) | per-layer correlation with the official `vc_render_tifxyz` render, PHerc. 211 test segment | mean 0.93 |
| PyTorch re-implementation of the `ink_9um` hybrid 3D-stem / 2D U-Net (official weights, `strict=True`) | correlation with the official published prediction made with the same checkpoint (seed 43, step 20k), tiles on the official global grid (`core.infer_roi`) | 0.9999 (max difference: 1 grey level out of 255) |
| Per-patch robust normalisation (p1/p99 clip, median, 1.4826·MAD) | max absolute difference with the reference implementation | 2.4e-7 |
| Kaggle sweep: render and scan every raw surface of a scroll | 22 surfaces of PHerc. 1203 (about 120 cm², 10 passes each) on one T4 | 83 min |

## Quick start

```bash
pip install -r requirements.txt
python tests/validate_against_official.py   # downloads a small public test region, CPU is enough
```

```python
from vesuvius_ink_adapt import core
vol = core.RemoteVolume("PHerc1203/volumes/20250820131727-9.362um-1.2m-113keV-masked.zarr/0/")
g, valid, scale, meta = core.load_tifxyz("PHerc1203/segments/raw/auto_grown_20251005230830030/")
surface = core.render(g, valid, scale, vol, roi=(1500, 2012, 1000, 1512))  # (28, H, W) uint8
model = core.load_model("s43-20k")
prob, n_patches = core.infer(surface, model, start=6, reverse=False)       # ink probability map
```

## Layout

- `vesuvius_ink_adapt/core.py`: remote volume reader, `tifxyz` renderer, `ink_9um` re-implementation, inference.
- `vesuvius_ink_adapt/zarrio.py`: dependency-free reader for remote Zarr arrays (v2 raw or Blosc, sharded v3).
- `vesuvius_ink_adapt/evalset.py` and `scripts/build_evalset.py`: labelled public segments cut into small
  evaluation zones (experimental).
- `scripts/audit_reserved_validation.py`: mask-only audit of the reserved validation zones of `ink_9um`.
- `scripts/inventory.py`: inventory of scans, surfaces, ink maps and published ink labels per scroll.
- `kaggle/`: the self-contained Kaggle script used for the PHerc. 1203 sweep, and a metadata template.
- `scripts/`: CPU-only tools (S3 listing and download, CPU renderer, CPU inference).
- `tests/validate_against_official.py`: reproduces the checks above.
- `docs/`: context, plan, experiment log, hand-off notes (in French).

## Data and licences

- CT data: Vesuvius Challenge open data (`s3://vesuvius-challenge-open-data/`), CC BY-NC 4.0. Cite
  *Vesuvius Challenge - CT Scans of Herculaneum Papyri* (or *EduceLab-Scrolls* for the legacy scans).
- Model weights: [`scrollprize/ink_9um`](https://huggingface.co/scrollprize/ink_9um), MIT.
- The network definition follows the architecture of the team's code in
  [ScrollPrize/villa](https://github.com/ScrollPrize/villa).
- This repository: MIT.
