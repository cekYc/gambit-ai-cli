#!/usr/bin/env bash
# Gambit CLI başlatıcısı (Linux). Her klasörden "gambit" yazarak açmak için:
#   ln -s "$PWD/gambit.sh" ~/.local/bin/gambit
here="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
py="$here/.venv/bin/python"
if [ ! -x "$py" ]; then
    echo "Sanal ortam yok. Kurmak için:" >&2
    echo "  python3 -m venv \"$here/.venv\" && \"$here/.venv/bin/pip\" install -r \"$here/requirements.txt\"" >&2
    exit 1
fi
export PYTHONUTF8=1
exec "$py" "$here/ai.py" "$@"
