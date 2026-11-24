#!/usr/bin/env bash
# Rebuild the label-source comparison bench from public data, then run it and analyse it.
# Data steps run on CPU (about 15 minutes on 4 cores, about 5 GB written); the training step needs a GPU
# (about 18 minutes per arm and seed on a Tesla T4).
# Usage: bash scripts/reproduce_bench.sh [data|train|all]   (default: data)
set -euo pipefail
cd "$(dirname "$0")/.."
step="${1:-data}"

if [[ "$step" == data || "$step" == all ]]; then
  mkdir -p data/inventory
  # 1. Catalogue of scans, segments and labels, and the list of prize-eligible scrolls (never used for labels).
  curl -sSL -o data/inventory/prizeEligibility.json \
    https://raw.githubusercontent.com/ScrollPrize/villa/main/scrollprize.org/src/data/prizeEligibility.json
  python scripts/inventory.py --eligibility data/inventory/prizeEligibility.json --out data/inventory/INVENTAIRE.md
  # 2. Labels and masks of the 9 reserved validation cases of ink_9um (evaluation only).
  python scripts/audit_reserved_validation.py
  # 3. Affine registration, on CT texture, between the fine-scan and native ~9 um canvases.
  python scripts/register_fine_to_native.py --objects PHerc0500P2 --match 20250825181859
  python scripts/register_fine_to_native.py --objects PHerc0009B --match 20250919125754
  python scripts/register_fine_to_native.py --objects PHerc0841
  # 4. Bench data: manifest, evaluation zones, training tiles, dense and misregistered variants.
  python scripts/build_bench.py --what manifest
  python scripts/build_bench.py --what eval
  python scripts/build_bench.py --what train
  python scripts/build_bench.py --what dense
  python scripts/build_bench.py --what shift
fi

if [[ "$step" == train || "$step" == all ]]; then
  # 5. Fine-tuning arms (GPU) and paired analysis. On Kaggle, use kaggle/bench/bench_kernel.py instead.
  python scripts/run_bench.py --arms base,C,T,H,D,S --seeds 0,1,2,3,4 --steps 1000 --eval-at 250,500 \
    --out data/bench/results
  python scripts/analyze_bench.py data/bench/results --json data/bench/results/report.json
fi
