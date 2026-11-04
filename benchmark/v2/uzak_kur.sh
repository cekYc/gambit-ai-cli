#!/bin/bash
# Kiralık GPU'da (Vast.ai, imaj ghcr.io/ggml-org/llama.cpp:full-cuda) iki llama-server başlatır:
#   bishop -> 127.0.0.1:8081, king -> 127.0.0.1:8082
# Sunucular yalnızca makinenin içinden erişilebilir; yerelden SSH tüneliyle bağlanılır (anahtar gerekmez).
# Modeller yereldeki LM Studio dosyalarıyla aynı quant: Qwen3.5-9B IQ4_XS, Qwen3.8-27B UD-Q3_K_XL.
set -e
BIN=$(command -v llama-server || ls /app/llama-server 2>/dev/null || find / -name llama-server -type f 2>/dev/null | head -1)
[ -x "$BIN" ] || { echo "llama-server bulunamadı"; exit 1; }
echo "llama-server: $BIN"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader

basla() {  # ad port hf_model alias
  pkill -f "llama-server.*--port $2" 2>/dev/null || true
  setsid nohup "$BIN" -hf "$3" --alias "$4" -c 16384 --parallel 1 -ngl 99 --jinja \
    --host 127.0.0.1 --port "$2" > "/root/$1.log" 2>&1 &
  echo "$1 başlatıldı (port $2), günlük /root/$1.log"
}
basla bishop 8081 unsloth/Qwen3.5-9B-GGUF:IQ4_XS qwen3.5-9b
basla king 8082 unsloth/Qwen3.8-27B-GGUF:UD-Q3_K_XL qwen3.8-27b

# İkisi de model indirip yükleyene kadar bekle
for port in 8081 8082; do
  for i in $(seq 1 120); do
    if curl -sf "http://127.0.0.1:$port/health" >/dev/null; then echo "port $port hazır"; break; fi
    sleep 5
  done
done
nvidia-smi --query-gpu=memory.used --format=csv,noheader
