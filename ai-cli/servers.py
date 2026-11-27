"""Gambit'in kendi başlattığı llama-server süreçleri (şimdilik ik_llama.cpp): LM Studio'nun aynı modeli daha yavaş
çalıştırdığı durumlar için. knight (Inkling 2 Mini) ik_llama.cpp'de prompt'u ~2 kat hızlı okuyor (YAPILACAKLAR).

Hazır ayarda "server" alanı varsa model metin modunda bu yoldan yüklenir:
  "server": {"bin": "~/.../llama-server", "port": 8090, "env": {...}, "args": [...],
             "efforts": [...], "effort_default": "high"}
Süreç Gambit'ten bağımsız yaşar (LM Studio'da yüklü kalan model gibi); PID'i ~/.cache/gambit/servers.json'da tutulur.
Başka bir model yüklenince ya da /unload'da kapatılır. Yüklerken lmstudio.guarded_load'daki RAM bekçisi uygulanır."""

import json
import os
import re
import signal
import subprocess
import time
import urllib.request
from pathlib import Path

import lmstudio

STATE = Path.home() / ".cache" / "gambit" / "servers.json"
HOST = "127.0.0.1"


def alias(name: str) -> str:
    """Sunucunun modeli tanıttığı ad (OpenAI isteklerindeki "model")."""
    return f"gambit-{name}"


def base_url(port: int) -> str:
    return f"http://{HOST}:{port}/v1"


def _get(port: int, path: str, timeout: float = 2) -> dict | None:
    try:
        with urllib.request.urlopen(f"http://{HOST}:{port}{path}", timeout=timeout) as r:
            return json.load(r)
    except (OSError, ValueError):
        return None


def _read_state() -> dict:
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _write_state(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")


def _alive(entry: dict) -> bool:
    """PID hâlâ bizim başlattığımız sunucu mu (PID başka bir sürece geçmiş olabilir)."""
    try:
        cmd = Path(f"/proc/{entry['pid']}/cmdline").read_bytes().split(b"\0")
    except (OSError, KeyError):
        return False
    return bool(cmd) and cmd[0].decode(errors="replace") == entry.get("bin")


def running() -> list[dict]:
    """Çalışan ve hazır sunucular, LM Studio'nun model listesi biçiminde ("_base_url" ve "_preset" ile)."""
    out = []
    for name, e in _read_state().items():
        if not _alive(e):
            continue
        health = _get(e["port"], "/health")
        if not health or health.get("status") != "ok":
            continue
        props = _get(e["port"], "/props") or {}
        n_ctx = props.get("n_ctx") or (props.get("default_generation_settings") or {}).get("n_ctx")
        out.append({"id": e["alias"], "type": "llm", "state": "loaded", "loaded_context_length": n_ctx,
                    "_base_url": base_url(e["port"]), "_preset": name, "_engine": e.get("engine", "llama-server")})
    return out


def model_file(cfg: dict, p: dict, cat: list[dict] | None = None) -> Path | None:
    """Hazır ayarın GGUF dosyasının tam yolu (LM Studio'nun indirme klasöründe, dosya adıyla bulunur)."""
    cat = lmstudio.catalog(cfg) if cat is None else cat
    entry = lmstudio.find_on_disk("", p.get("file", ""), cat or [])
    if not entry:
        return None
    path = lmstudio.downloads_folder() / entry["path"]
    return path if path.is_file() else None


def binary(p: dict) -> Path | None:
    srv = p.get("server") or {}
    path = Path(os.path.expanduser(str(srv.get("bin", ""))))
    return path if srv.get("bin") and path.is_file() and os.access(path, os.X_OK) else None


def stop_all() -> list[str]:
    """Gambit'in başlattığı bütün sunucuları kapatır; kapatılanların adları."""
    stopped = []
    for name, e in _read_state().items():
        if _alive(e):
            try:
                os.killpg(e["pid"], signal.SIGTERM)
            except OSError:
                pass
            for _ in range(50):
                if not _alive(e):
                    break
                time.sleep(0.2)
            if _alive(e):
                try:
                    os.killpg(e["pid"], signal.SIGKILL)
                except OSError:
                    pass
            stopped.append(name)
    _write_state({})
    return stopped


def _log_error(log: Path) -> str:
    """Sunucu günlüğündeki hata: son "error"/"failed" satırı, VRAM yetmediyse açıkça."""
    try:
        lines = [l.strip() for l in log.read_text(errors="replace").splitlines() if l.strip()]
    except OSError:
        return ""
    errors = [l for l in lines if re.search(r"(?i)error|failed|out of memory", l)]
    msg = (errors[-1] if errors else (lines[-1] if lines else ""))[:300]
    if "out of memory" in " ".join(errors).lower():
        msg += " (VRAM yetmedi)"
    return msg


def start(cfg: dict, name: str, p: dict, on_tick=None, timeout: float = 600) -> lmstudio.LoadResult:
    """Hazır ayarın sunucusunu başlatır (önce diğer Gambit sunucularını kapatır) ve hazır olmasını bekler. Yüklerken boş
    RAM ram_guard_mb'nin altına inerse ya da bellek baskısı psi_guard'ı geçerse sunucu durdurulur."""
    srv = p.get("server") or {}
    exe = binary(p)
    if not exe:
        return lmstudio.LoadResult(False, f"sunucu programı bulunamadı: {srv.get('bin')} (YAPILACAKLAR'daki derleme adımları)")
    gguf = model_file(cfg, p)
    if not gguf:
        return lmstudio.LoadResult(False, f"model dosyası diskte yok: {p.get('file')}")
    stop_all()
    port = int(srv.get("port", 8090))
    log = STATE.parent / f"{name}-server.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    argv = [str(exe), "-m", str(gguf), "--host", HOST, "--port", str(port), "--alias", alias(name),
            *[str(a) for a in srv.get("args", [])]]
    env = {**os.environ, **{k: str(v) for k, v in (srv.get("env") or {}).items()}}
    with open(log, "w") as fh:
        # cwd: ik_llama.cpp çalıştığı klasöre llama.log yazıyor; kullanıcının proje klasörüne düşmesin
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=fh, stderr=subprocess.STDOUT, env=env,
                                cwd=STATE.parent, start_new_session=True)
    entry = {"pid": proc.pid, "port": port, "alias": alias(name), "bin": str(exe), "engine": srv.get("engine", ""),
             "log": str(log), "started": time.strftime("%Y-%m-%d %H:%M:%S")}
    _write_state({name: entry})
    guard = int(cfg.get("ram_guard_mb", lmstudio.RAM_GUARD_MB)) * lmstudio.MIB
    psi_guard = float(cfg.get("psi_guard", lmstudio.PSI_GUARD))
    t0, lowest, peak = time.monotonic(), None, 0.0
    try:
        while True:
            if proc.poll() is not None:
                _write_state({})
                return lmstudio.LoadResult(False, _log_error(log) or f"sunucu kapandı (çıkış {proc.returncode})")
            health = _get(port, "/health", timeout=1)
            if health and health.get("status") == "ok":
                break
            avail, pressure = lmstudio.mem_available(), lmstudio.mem_pressure()
            if avail is not None:
                lowest = avail if lowest is None else min(lowest, avail)
            peak = max(peak, pressure or 0.0)
            reason = (f"boş RAM {avail // lmstudio.MIB} MB'a düştü" if avail is not None and avail < guard else
                      f"bellek baskısı %{pressure:.0f}" if pressure is not None and pressure >= psi_guard else "")
            if reason:
                stop_all()
                return lmstudio.LoadResult(False, f"RAM bekçisi: {reason}; sunucu durduruldu", guard_tripped=True)
            if time.monotonic() - t0 > timeout:
                stop_all()
                return lmstudio.LoadResult(False, f"sunucu {timeout:.0f} saniyede hazır olmadı; durduruldu")
            if on_tick:
                on_tick(avail)
            time.sleep(0.3)
    except KeyboardInterrupt:
        stop_all()
        raise
    note = ", ".join(([f"yüklerken en düşük boş RAM {lmstudio.gib(lowest)}"] if lowest is not None else [])
                     + [f"{srv.get('engine') or 'llama-server'}, port {port}"])
    return lmstudio.LoadResult(True, note)
