#!/bin/bash
# Uzak GPU'daki iki sunucuya, SSH tüneli açıkken bishop otomatik ve king otomatik sınırsız koşularını
# paralel başlatır. Her koşu kendi klasörüne yazar; bitince results-sinirsiz'e birleştirilir.
# Tünel: ssh -N -L 8081:127.0.0.1:8081 -L 8082:127.0.0.1:8082 -p <port> root@<adres>
cd /c/AI/benchmark/v2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
mkdir -p results-uzak-bishop results-uzak-king
python -u run.py --out results-uzak-bishop --no-time-limit --plan bishop:auto \
  --remote http://127.0.0.1:8081/v1 >> results-uzak-bishop/calisma.log 2>&1 &
python -u run.py --out results-uzak-king --no-time-limit --plan king:auto \
  --remote http://127.0.0.1:8082/v1 >> results-uzak-king/calisma.log 2>&1 &
wait
echo BITTI
