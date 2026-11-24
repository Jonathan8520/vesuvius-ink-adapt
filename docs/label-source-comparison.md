# Hand labels or the 2 µm model's map? A paired fine-tuning comparison for 9 µm ink detection

Jonathan8520, November 2026. Code: this repository (MIT). Data: Vesuvius Challenge open data
("Vesuvius Challenge - CT Scans of Herculaneum Papyri", CC BY-NC 4.0). Weights: `scrollprize/ink_9um` (MIT).

## Question

When a 9 µm ink model is fine-tuned on new segments, does it matter whether those segments carry the team's
**human ink labels** or the team's **2 µm model map** (`new_canon_autoresearch_recipe`, thresholded), **on the same
pixels**?

Why it matters:
- Human labelling at 9 µm is slow and needs people who can read Greek letter forms. If the registered 2 µm map
  supervises as well, that time is better spent elsewhere.
- Published results disagree. One controlled experiment concludes that "letter form is learnable from human
  labels and not from model-generated labels" (moisescorreo/vesuvius-uncertainty-bench, August 2026), but its two
  label sources sit on different scans, energies and segments. Self-training studies (khj1222, September 2026;
  protonjls, November 2026) find machine labels from 9 µm models far weaker than human ones. Dense 2 µm maps beat
  sparse hand labels in Domenico Russo's and Erwin Nieuwlaar's benches, but with different supervised areas.
- When closing villa PR #2381 (where to label next), the maintainer wrote: "without a training run comparison
  we'd prefer this one stay in a separate repo". This is such a training-run comparison.

As far as we could find (searches of 24 November 2026, listed in `docs/RESEARCH.md`, sections 10 and 11), nobody
has published the same-pixel comparison.

## Design

Everything is fixed except the source of the labels on two new segments.

| | |
| --- | --- |
| Start | `scrollprize/ink_9um`, `hybrid_3d2d-seed43/step-075000` (and `seed42/step-075000` in the consolidation run) |
| Recipe | 1,000 steps, batch 64, SGD Nesterov (momentum 0.99, lr 0.002, cosine, 100 warm-up steps), smoothed BCE (0.5) + Dice inside the supervision mask, 17-of-N layer window jittered by ±2, robust per-patch normalisation, flips, transposes and light intensity augmentation (`vesuvius_ink_adapt/finetune.py`). An abbreviated version of the team's `aligned21_hybrid_3d2d` recipe, identical for every arm. |
| Replay | the team's `ink_9um` corpus (29 representations, 2,191 tiles of 256 px), 69 % of each batch, with the team's batch quotas |
| New segments | PHerc0500P2 `20250825181859--1` (native 9.362 µm, 113 keV) and PHerc0009B `20250919125754-auto_grown_20250919055754487_inp_hr` (native 8.64 µm, 116 keV), 31 % of each batch; 4.8 cm² of supervised pixels |
| Pairing | for a given seed, arms draw exactly the same patches (tile, crop, depth window); only the target labels differ |

Arms (labels on the two new segments):

| Arm | Labels | Supervised where |
| --- | --- | --- |
| `base` | none: the published checkpoint, not fine-tuned | |
| `C` | none: replay only (control) | |
| `H` | the team's human labels (S3 `ink-labels`, set `20260918`), transferred to the native canvas | the team's supervision mask |
| `T` | the 2 µm map transferred to the native canvas, ink if ≥ 128, background if ≤ 64, the band in between unsupervised (the reader-v2-labels rule) | the team's supervision mask, minus the band |
| `D` | the same map, same rule | the whole segment (4 to 5 times more pixels), no human choice at all |
| `S` | as `T`, but the map is transferred by scaling only (no registration, 5 to 10 px off) | as `T` |

Transfer from the fine-scan canvas (2.2 to 2.4 µm, pyramid level 2) to the native canvas uses one affine per
segment, fitted on CT texture (`vesuvius_ink_adapt/register.py`). Median residual 0.4 px on PHerc0500P2, 0.8 px on
PHerc0009B. Check against the team's own labels published on both canvases (PHerc0139, five segments): ink IoU
0.96 to 0.99. The scale is the ratio of canvas sizes, consistent with the exact formula of
slchicoineau-creator/tifxyz-canvas-map.

Evaluation, never trained on:
- **PHerc0841**, a scroll none of the arms or the starting checkpoint saw: the team's human labels on its three
  labelled segments, transferred to the native 9.366 µm canvas, scored inside their supervision mask (3.8 M px).
- **The 9 reserved validation zones of `ink_9um`** (4.5 M px): the three masks published in `ink_9um/labels` and
  the six that are only published in the 2.4 µm frame (see the annex). These are held out from training, but they
  sit inside scrolls and segments the model was trained on.

Scoring follows the official inference (global tile grid, Hann blending, centred 17-layer window, forward
order). Metrics: AUC and balanced accuracy at 0.5, averaged over the segments of a group. Uncertainty: paired
bootstrap, resampling 128 px blocks (the same blocks for all arms) and seeds, 2,000 draws. **The decision rule was
written and committed before the results were read** (`docs/PLAN.md` history, 22 November 2026, 22:28 UTC).

## Results

Mean over segments of each group, mean ± sd over seeds, at 1,000 steps.

| Arm | Seeds | PHerc0841 (unseen scroll): AUC / balanced acc. | 9 reserved zones: AUC / balanced acc. |
| --- | --- | --- | --- |
| `base` | 1 | 0.743 / 0.649 | 0.865 / 0.757 |
| `C` replay only | 5 | 0.753 ± 0.009 / 0.682 ± 0.008 | 0.888 ± 0.005 / 0.802 ± 0.004 |
| `T` 2 µm map | 5 | 0.792 ± 0.005 / 0.730 ± 0.002 | 0.885 ± 0.001 / 0.800 ± 0.002 |
| `H` human labels | 5 | 0.792 ± 0.003 / 0.729 ± 0.002 | 0.885 ± 0.001 / 0.800 ± 0.002 |
| `D` 2 µm map, whole segment | 2 | 0.780 ± 0.003 / 0.717 ± 0.004 | 0.892 ± 0.002 / 0.808 ± 0.000 |

Paired differences in AUC (95 % block-and-seed bootstrap interval):

| Difference | PHerc0841 | 9 reserved zones |
| --- | --- | --- |
| `H − T` (human vs map, same pixels) | **+0.0002** [−0.0052, +0.0054] | **+0.0008** [−0.0026, +0.0037] |
| `H − C` | +0.039 [+0.026, +0.054] | −0.002 [−0.011, +0.008] |
| `T − C` | +0.039 [+0.026, +0.054] | −0.003 [−0.012, +0.009] |
| `D − H` (2 seeds) | −0.010 [−0.019, −0.001] | +0.007 [−0.000, +0.014] |

Same reading at 250 and 500 steps, and in balanced accuracy.

<!-- CONSOLIDATION: results of `D` at 5 seeds, `S`, and the seed42 start go here. -->

## What this shows

1. **On the same pixels, human labels and the registered 2 µm map give the same model.** The interval excludes
   any difference larger than about 0.005 AUC on the unseen scroll.
2. **What helps is adding segments from new scrolls**: +0.04 AUC and +0.05 balanced accuracy on PHerc0841, on every
   seed and every PHerc0841 segment, whatever the label source. Nothing changes on the scrolls already in the
   corpus. This agrees with the approach of reader-v2 and reader-v3 (Domenico Russo).
3. Restricting the map to the region an annotator chose (`T` vs `D`) is worth at most +0.01 on the unseen scroll
   and costs 0.007 on the seen ones, on 2 seeds: a small effect of mixed sign.

Practical consequence: at this scale, an hour of human ink labelling on new 9 µm segments buys nothing that the
registered 2 µm map does not already give. The useful work is getting more segments from more scrolls onto the
native canvas, correctly registered.

## What this does not show

- That human labels are useless in general: two segments, 1,000 steps, an abbreviated recipe, one teacher model.
- That our fine-tuned model is good: 0.79 AUC on PHerc0841 stays below what is reported for reader-v2 (0.824),
  reader-v3 (0.848) and hecate (0.857), measured with other masks.
- A cross-scroll result on the reserved zones: they are intra-segment measures.
- Independence of the three PHerc0841 segments: two of them (w00 and the `…144552896` auto-grown segment) are the
  same papyrus (ChaseHendrick/Scrolls, finding 5), so the group holds about two independent observations.
- The evaluation labels on PHerc0841 and in the reserved zones were drawn by the same team as the `H` labels.
  If anything this favours `H`; it still does not beat `T`.

## Reproduce

```bash
pip install -r requirements.txt
bash scripts/reproduce_bench.sh data     # CPU, about 15 minutes on 4 cores, public data only
bash scripts/reproduce_bench.sh train    # GPU, about 18 minutes per arm and seed on a T4
```

On Kaggle: put the output of the data step in a dataset and run `kaggle/bench/bench_kernel.py` (two T4, one arm
and seed per GPU, `PRESET` selects the arms). Analysis: `python scripts/analyze_bench.py <results folder>`.

Check (24 November 2026): `reproduce_bench.sh data` run from a fresh clone of this repository rebuilt all 60
bench files (33 training packs, 27 evaluation zones). Every array is identical to the data used for the results
above. The bucket catalogue (`metadata.json`) and the label sets can change upstream; the label set used is
`20260918`.

Files:

| File | Role |
| --- | --- |
| `scripts/build_bench.py` | training tiles (replay corpus, new segments with each label version) and evaluation zones |
| `vesuvius_ink_adapt/register.py`, `scripts/register_fine_to_native.py` | fine-to-native registration |
| `vesuvius_ink_adapt/finetune.py` | sampler (paired by seed), augmentation, loss, fine-tuning, scoring |
| `scripts/run_bench.py` | arms, quotas, seeds |
| `scripts/analyze_bench.py` | paired block bootstrap and the decision rule |
| `vesuvius_ink_adapt/core.py` | re-implementation of `ink_9um` and of the official tiled inference (checked against the official prediction: r = 0.9999, `tests/validate_against_official.py`) |

## Related work

`docs/RESEARCH.md`, section 11 (French), lists what we read and how each item differs from this comparison:
moisescorreo/vesuvius-uncertainty-bench, khj1222/vesuvius-challenge (docs/18, 20, 33), protonjls/vesuvius-first-letters,
ChaseHendrick/Scrolls (`altrain`), ibarapascal/ink-disagree, DomRusso2 (ink9um-dense, reader-v2, reader-v3),
Nieuwlaar/ink9um-dense-native, villa PRs #2381 and #2512.

## Annex

The `ink_9um` checkpoints list nine `reserved_validation_cases`, but `ink_9um/labels` ships a `_validation_mask`
for three of them only; the other six (3.5 cm², far from training pixels) exist in the 2.4 µm frame, in the
bucket's `ink/` folder and on S3 (`scripts/audit_reserved_validation.py`).
