#!/bin/bash
# queen (Gemma 4 26B-A4B QAT q4_0, yereldeki dosyanın aynısı) uzak GPU'da, sınırsız süre; kapalı ve otomatik paralel,
# her biri kendi sunucusunda ve klasöründe. Yerel sınırsız sonuçlarla (results-sinirsiz) karşılaştırıp kiralık GPU ile
# yerel arasındaki farkı ölçmek için. Tünel 8082 -> kapalı, 8081 -> otomatik (ikisi de queen).
cd /c/AI/benchmark/v2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
mkdir -p results-uzak-queen results-uzak-queen-oto
python -u run.py --out results-uzak-queen --no-time-limit --plan queen:off \
  --remote http://127.0.0.1:8082/v1 >> results-uzak-queen/calisma.log 2>&1 &
python -u run.py --out results-uzak-queen-oto --no-time-limit --plan queen:auto \
  --remote http://127.0.0.1:8081/v1 >> results-uzak-queen-oto/calisma.log 2>&1 &
wait
echo BITTI
