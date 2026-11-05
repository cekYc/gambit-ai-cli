#!/bin/bash
# Tekrar turu: bir yapılandırma sabit örnekleme ayarlarıyla 3 seed'de, her seed 4 parçaya bölünmüş olarak paralel
# (12 süreç) uzak GPU'da koşulur. Sunucu en az 12 yuvalı olmalı. Kullanım: uzak_kos_tekrar.sh <hazır_ayar> <mod> [port]
# Sonuçlar results-tekrar/<hazır_ayar>-<mod>-s<seed>-p<parça>; birleştirme ayrı yapılır. Tünel port -> uzak sunucu.
cd /c/AI/benchmark/v2
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
PRESET=$1 MODE=$2 PORT=${3:-8081}
P="C:/Users/erayc/AppData/Local/Temp/claude/d3df15a30ffc05d5/97b66010-a10b-4bd9-a358-27c055797f01/scratchpad"
for seed in 42 43 44; do
  for i in 1 2 3 4; do
    D=results-tekrar/$PRESET-$MODE-s$seed-p$i
    mkdir -p $D
    python -u run.py --out $D --no-time-limit --plan $PRESET:$MODE --seed $seed --only "$(cat $P/parca$i.txt)" \
      --remote http://127.0.0.1:$PORT/v1 >> $D/calisma.log 2>&1 &
  done
done
wait
echo BITTI
