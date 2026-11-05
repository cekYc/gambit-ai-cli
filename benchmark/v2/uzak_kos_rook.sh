#!/bin/bash
# Yeni rook (Qwen3.6-35B-A3B UD-IQ3_S) uzak GPU'da: önce kapalı, sonra otomatik, sınırsız süre.
# Tünel 8081 -> uzak rook sunucusu.
cd /c/AI/benchmark/v2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
mkdir -p results-uzak-rook
python -u run.py --out results-uzak-rook --no-time-limit --plan rook:off,rook:auto \
  --remote http://127.0.0.1:8081/v1 >> results-uzak-rook/calisma.log 2>&1
echo BITTI
