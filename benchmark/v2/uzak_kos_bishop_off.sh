#!/bin/bash
# bishop kapalı (Qwen3.5-9B IQ4_XS) uzak GPU'da, sınırsız süre; yerel bishop kapalı v2 ile ortam karşılaştırması.
# Sunucu 4 yuvalı (--parallel 4, yuva başına 16384 bağlam); görevler 4 parçaya bölünüp 4 süreçte koşulur,
# her parça kendi klasörüne yazar, bitince results-uzak-bishop'a birleştirilir. Tünel 8081 -> uzak bishop.
cd /c/AI/benchmark/v2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
P="C:/Users/erayc/AppData/Local/Temp/claude/d3df15a30ffc05d5/97b66010-a10b-4bd9-a358-27c055797f01/scratchpad"
for i in 1 2 3 4; do
  mkdir -p results-uzak-bishop-p$i
  python -u run.py --out results-uzak-bishop-p$i --no-time-limit --plan bishop:off --only "$(cat $P/parca$i.txt)" \
    --remote http://127.0.0.1:8081/v1 >> results-uzak-bishop-p$i/calisma.log 2>&1 &
done
wait
echo BITTI
