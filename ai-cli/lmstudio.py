"""LM Studio model yönetimi: diskteki modeller, hazır ayarların hangi dosyaya karşılık geldiği, yüklemeden önce bellek
tahmini, donanıma göre GPU oranı önerisi ve yüklerken RAM bekçisi. Gambit CLI ve benchmark betikleri birlikte kullanır.

Bir hazır ayar modeli iki yoldan bulabilir:
  "model": LM Studio model anahtarı (lms ls'deki ad). Sistemden sisteme değişebiliyor.
  "file":  GGUF dosyasının adı. Değişmez; anahtar bilinmese de model diskte bulunur.
"repo", "quant", "size_gb" modeli indirmek ve diskte olup olmadığını anlatmak için; "context", "gpu", "mtp" ise
yükleme ayarlarıdır (lms load argümanlarına çevrilir, "args" içindekiler önceliklidir)."""

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

GIB = 1024 ** 3
MIB = 1024 ** 2
RAM_GUARD_MB = 800  # yüklerken boş RAM bunun altına inerse yükleme durdurulur (config: ram_guard_mb)
PSI_GUARD = 40.0  # Linux'ta bellek baskısı (PSI full avg10, %) bunu geçerse de durdurulur (config: psi_guard)
RAM_RESERVE_GB = 1.0  # tahmin karşılaştırılırken sisteme ve açık uygulamalara bırakılan pay (config: ram_reserve_gb)
VRAM_RESERVE_MB = 300  # GPU'da boş bırakılan pay (config: vram_reserve_mb)
CONTEXT_FLAGS = ("-c", "--context-length")


def gib(n: float) -> str:
    return f"{n / GIB:.1f} GiB"


# --- lms ---

def lms_path(cfg: dict) -> str | None:
    """lms'in yolu: config.json'daki lms_path (Windows'tan kalan .exe uzantısı olsa da olmasa da), yoksa LM Studio'nun
    varsayılan yeri, yoksa PATH."""
    exe = ".exe" if os.name == "nt" else ""
    candidates = []
    if cfg.get("lms_path"):
        p = Path(os.path.expandvars(os.path.expanduser(cfg["lms_path"])))
        candidates += [p, p.with_suffix(exe)]
    candidates.append(Path.home() / ".lmstudio" / "bin" / f"lms{exe}")
    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)
    return shutil.which("lms")


def run(cfg: dict, *args: str, timeout: float = 600) -> subprocess.CompletedProcess:
    """lms'i çalıştırır; lms yoksa ya da süre dolarsa çıkış kodu 1 olan bir sonuç döner."""
    lms = lms_path(cfg)
    if not lms:
        return subprocess.CompletedProcess(["lms", *args], 1, "", "lms bulunamadı")
    try:
        return subprocess.run([lms, *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess([lms, *args], 1, "", f"lms {timeout:.0f} saniyede bitmedi")


def catalog(cfg: dict) -> list[dict] | None:
    """Diskteki dil modelleri (lms ls --json: modelKey, path, sizeBytes, quantization...). lms yoksa None."""
    r = run(cfg, "ls", "--json", timeout=30)
    if r.returncode != 0:
        return None
    try:
        data = json.loads(r.stdout)
    except ValueError:
        return None
    return [m for m in data if isinstance(m, dict) and m.get("type") in ("llm", "vlm")]


# --- hazır ayar <-> diskteki model ---

def find_on_disk(model: str, file: str, cat: list[dict]) -> dict | None:
    model, file = (model or "").lower(), (file or "").lower()
    if model:
        for m in cat:
            if model in (str(m.get("modelKey", "")).lower(), str(m.get("indexedModelIdentifier", "")).lower(),
                         str(m.get("path", "")).lower()):
                return m
    if file:
        for m in cat:
            if Path(str(m.get("path", ""))).name.lower() == file:
                return m
    return None


def is_empty_slot(p: dict) -> bool:
    """Modeli hiç atanmamış boş yuva mı."""
    return not (p.get("model") or p.get("file"))


def resolve_presets(cfg: dict, cat: list[dict] | None) -> None:
    """Hazır ayarları diskteki modellerle eşleştirir. Eşleşen ayarın "model" alanı diskteki anahtarla değiştirilir
    (anahtar Windows ile Linux arasında farklı olabiliyor, dosya adı değişmez). "_disk": eşleşen kayıt; diskte yoksa
    None. Katalog alınamadıysa (lms yok) ayarlara dokunulmaz."""
    for p in cfg.get("presets", {}).values():
        p.setdefault("model", "")
    if cat is None:
        return
    for p in cfg.get("presets", {}).values():
        p.setdefault("_wanted", p.get("model", ""))
        if is_empty_slot({"model": p["_wanted"], "file": p.get("file")}):
            continue
        m = find_on_disk(p["_wanted"], p.get("file", ""), cat)
        p["_disk"] = m
        p["model"] = m["modelKey"] if m else p["_wanted"]
        if isinstance(p.get("vision"), dict):
            v = p["vision"]
            v.setdefault("_wanted", v.get("model", ""))
            # Görsel sanal model kurulu değilse düz model: LM Studio görsel ekini zaten onunla yükler
            base = find_on_disk("", p.get("file", ""), cat)
            vm = find_on_disk(v["_wanted"], "", cat) if v["_wanted"] else None
            vm = vm or (base if base and base.get("vision") else None)
            v["_disk"] = vm
            v["model"] = vm["modelKey"] if vm else v["_wanted"]


def vision_of(p: dict) -> dict | None:
    """Hazır ayarın görsel modu ({"model", "gpu", "_disk"}); modelin görsel eki yoksa None."""
    v = p.get("vision")
    return v if isinstance(v, dict) and (v.get("_disk") or (v.get("model") and "_disk" not in v)) else None


def unassigned(cfg: dict, cat: list[dict] | None) -> list[dict]:
    """Diskte olup hiçbir hazır ayara bağlı olmayan modeller (Gambit'in sanal modelleri ve hazır ayarların düz
    kopyaları sayılmaz)."""
    presets = cfg.get("presets", {}).values()
    used = {d.get("modelKey") for p in presets for d in (p.get("_disk"), (p.get("vision") or {}).get("_disk")) if d}
    files = {str(p.get("file", "")).lower() for p in presets}
    # Sanal modeller (yolu .gguf olmayan: Gambit'inkiler ve LM Studio'nun kendi tanımları) bir dosyanın kopyası sayılır
    return [m for m in cat or [] if m.get("modelKey") not in used and str(m.get("path", "")).lower().endswith(".gguf")
            and Path(str(m.get("path", ""))).name.lower() not in files]


def downloads_folder() -> Path:
    try:
        settings = json.loads((Path.home() / ".lmstudio" / "settings.json").read_text(encoding="utf-8"))
        if folder := settings.get("downloadsFolder"):
            return Path(folder)
    except (OSError, ValueError):
        pass
    return Path.home() / ".lmstudio" / "models"


def download_progress(p: dict) -> float | None:
    """Ayarın dosyası LM Studio'da iniyorsa inen oran (0-1; boyut bilinmiyorsa -1). İnmiyorsa None."""
    name = p.get("file")
    folder = downloads_folder()
    if not name or not folder.is_dir():
        return None
    for part in folder.glob(f"*/*/downloading_{name}.part"):
        size = p.get("size_gb")
        return min(part.stat().st_size / (size * 1e9), 0.99) if size else -1.0
    return None


def download_hint(p: dict) -> str:
    """Diskte olmayan ayarın nasıl indirileceği."""
    if p.get("repo"):
        file = f" → {p['file']}" if p.get("file") else ""
        return f"lms get https://huggingface.co/{p['repo']} --select{file}"
    return "LM Studio'da modeli indir ya da config.json'da başka bir modele bağla"


def preset_args(p: dict, vision: bool = False) -> list[str]:
    """Hazır ayarın lms load argümanları: "args" + context, gpu, mtp alanları (args'ta aynı ayar varsa o geçerli).
    vision: görsel modun GPU oranı ("vision": {"gpu": ...}; görsel eki VRAM'de yer tuttuğu için daha düşük)."""
    args = [str(a) for a in p.get("args", [])]
    if vision and isinstance(p.get("vision"), dict) and "gpu" in p["vision"]:
        p = {**p, "gpu": p["vision"]["gpu"]}
    if "context" in p and not any(a in args for a in CONTEXT_FLAGS):
        args += ["-c", str(p["context"])]
    if "--parallel" not in args:
        args += ["--parallel", "1"]
    if "gpu" in p and "--gpu" not in args:
        args += ["--gpu", str(p["gpu"])]
    if "mtp" in p and not any(a.endswith("speculative-draft-mtp") for a in args):
        args.append("--speculative-draft-mtp" if p["mtp"] else "--no-speculative-draft-mtp")
    return args


def get_arg(args: list[str], flags: tuple[str, ...], default: str = "") -> str:
    for i, a in enumerate(args[:-1]):
        if a in flags:
            return args[i + 1]
    return default


def set_arg(args: list[str], flags: tuple[str, ...], value: str) -> list[str]:
    out, skip = [], False
    for i, a in enumerate(args):
        if skip:
            skip = False
            continue
        if a in flags and i + 1 < len(args):
            skip = True
            continue
        out.append(a)
    return out + [flags[0], value]


# --- düşünme düzeyleri ---

API_EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh")  # LM Studio OpenAI ucunun kabul ettiği reasoning_effort


def reasoning_options(base_url: str) -> dict[str, tuple[list[str], str]]:
    """LM Studio'nun her model için bildirdiği düşünme düzeyleri: {model anahtarı: (düzeyler, varsayılan)}.

    Düz modellerde yalnızca "off" ve "on" olur: LM Studio istekteki reasoning_effort'u şablona iletmez, yalnızca
    düşünmeyi açar ya da kapatır. Şablonu kademeli düzey tanıyan modeller (Inkling, Qwen3.8/Bonsai) için
    ai-cli/lmstudio-hub/ altındaki sanal model tanımları düzeyi şablona bağlar; o zaman "low", "medium"... de gelir.
    "on" kademeli bir modelde varsayılan düzeyin eşidir ve listeden çıkarılır. LM Studio değilse boş sözlük."""
    url = base_url.rstrip("/").removesuffix("/v1") + "/api/v1/models"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.load(r)
    except (OSError, ValueError):
        return {}
    out = {}
    for m in data.get("models", []):
        reasoning = (m.get("capabilities") or {}).get("reasoning")
        if not isinstance(reasoning, dict) or not reasoning.get("allowed_options"):
            continue
        opts = [str(o) for o in reasoning["allowed_options"]]
        default = str(reasoning.get("default") or opts[-1])
        if any(o not in ("off", "on") for o in opts):
            opts = [o for o in opts if o != "on"]
            default = default if default in opts else next((o for o in reversed(opts) if o != "off"), opts[0])
        out[m.get("key", "")] = (opts, default)
    return out


# --- bellek ---

def mem_available() -> int | None:
    """Kullanılabilir RAM (bayt): Linux'ta MemAvailable, Windows'ta ullAvailPhys. Ölçülemezse None."""
    if sys.platform.startswith("linux"):
        try:
            with open("/proc/meminfo", encoding="ascii") as f:
                for line in f:
                    if line.startswith("MemAvailable:"):
                        return int(line.split()[1]) * 1024
        except OSError:
            return None
    if os.name == "nt":
        import ctypes

        class MemoryStatus(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        *((n, ctypes.c_ulonglong) for n in ("total", "avail", "total_pf", "avail_pf", "total_v",
                                                             "avail_v", "avail_ext"))]

        st = MemoryStatus()
        st.dwLength = ctypes.sizeof(st)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
            return int(st.avail)
    return None


def mem_pressure() -> float | None:
    """Linux bellek baskısı (PSI): son ~10 sn'de tüm süreçlerin aynı anda belleği beklerken durduğu zamanın yüzdesi
    ("full avg10"). Pop!_OS'ta model dosyası diskten eşlendiği (mmap) ve açık uygulamalar zram'e itildiği için boş RAM
    yüklerken düşmeyebiliyor; sistemin tıkanmaya başladığını bu gösterir. Ölçülemezse (Windows) None."""
    try:
        with open("/proc/pressure/memory", encoding="ascii") as f:
            for line in f:
                if line.startswith("full") and (m := re.search(r"avg10=([\d.]+)", line)):
                    return float(m.group(1))
    except OSError:
        pass
    return None


def vram() -> tuple[int, int] | None:
    """NVIDIA ekran kartında (boş, toplam) bellek, bayt. nvidia-smi yoksa ya da çalışmıyorsa None (ör. sürücü
    güncellenip bilgisayar yeniden başlatılmadıysa: "Driver/library version mismatch")."""
    smi = shutil.which("nvidia-smi")
    if not smi:
        return None
    try:
        out = subprocess.run([smi, "--query-gpu=memory.free,memory.total", "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.match(r"\s*(\d+)\s*,\s*(\d+)", out.stdout)
    return (int(m.group(1)) * MIB, int(m.group(2)) * MIB) if out.returncode == 0 and m else None


def budgets(cfg: dict) -> tuple[int | None, int | None, str]:
    """Modele ayrılabilecek (VRAM, RAM) bayt ve VRAM'in nereden geldiği. Diğer modeller boşaltıldıktan sonra
    çağrılmalı. VRAM: nvidia-smi'deki boş bellek eksi pay, config'deki vram_limit_gb ile sınırlı."""
    limit = cfg.get("vram_limit_gb")
    limit = int(float(limit) * GIB) if limit else None
    v = vram()
    if v:
        free = v[0] - int(cfg.get("vram_reserve_mb", VRAM_RESERVE_MB)) * MIB
        vram_budget, source = (min(free, limit), "nvidia-smi") if limit else (free, "nvidia-smi")
    else:
        vram_budget, source = limit, "config (vram_limit_gb)" if limit else ""
    ram = mem_available()
    ram_budget = ram - int(float(cfg.get("ram_reserve_gb", RAM_RESERVE_GB)) * GIB) if ram is not None else None
    return vram_budget, ram_budget, source


@dataclass
class Estimate:
    gpu: int  # bayt
    total: int

    @property
    def ram(self) -> int:
        return max(0, self.total - self.gpu)


_UNITS = {"B": 1, "KB": 1e3, "MB": 1e6, "GB": 1e9, "KIB": 1024, "MIB": MIB, "GIB": GIB}


def _size(text: str, label: str) -> int | None:
    m = re.search(rf"{label}:\s*([\d.,]+)\s*([KMG]i?B|B)", text, re.I)
    return int(float(m.group(1).replace(",", "")) * _UNITS[m.group(2).upper()]) if m else None


def estimate(cfg: dict, key: str, args: list[str]) -> Estimate | None:
    """lms load --estimate-only: modelin bu ayarlarla GPU'da ve toplamda ne kadar bellek isteyeceği."""
    r = run(cfg, "load", key, *args, "--estimate-only", "-y", timeout=60)
    text = ANSI.sub("", r.stdout + r.stderr)
    gpu, total = _size(text, "Estimated GPU Memory"), _size(text, "Estimated Total Memory")
    return Estimate(gpu, total) if r.returncode == 0 and gpu is not None and total is not None else None


def fit_problems(est: Estimate, vram_budget: int | None, ram_budget: int | None) -> list[str]:
    problems = []
    if vram_budget is not None and est.gpu > vram_budget:
        problems.append(f"GPU'ya sığmayacak: tahmini {gib(est.gpu)}, ayrılabilecek {gib(max(vram_budget, 0))}")
    if ram_budget is not None and est.ram > ram_budget:
        problems.append(f"RAM yetmeyebilir: GPU dışında kalan kısım tahmini {gib(est.ram)}, ayrılabilecek "
                        f"{gib(max(ram_budget, 0))} (tarayıcı gibi uygulamaları kapatmak yer açar)")
    return problems


@dataclass
class Advice:
    gpu: str  # "--gpu" değeri: "max", "0.35", "off"
    context: str
    est: Estimate
    fits: bool  # hem VRAM'e hem RAM'e sığıyor mu


def _ratio(step: int) -> str:
    return "off" if step == 0 else "max" if step == 20 else f"{step / 20:.2f}".rstrip("0")


def advise(cfg: dict, key: str, args: list[str], vram_budget: int | None, ram_budget: int | None) -> Advice | None:
    """VRAM bütçesine sığan en yüksek GPU oranı (0,05 adımlarla) ve RAM'e sığmıyorsa daha kısa bağlam önerisi.
    VRAM bütçesi bilinmiyorsa None."""
    if vram_budget is None:
        return None
    context = get_arg(args, CONTEXT_FLAGS, "")
    contexts = [context] + ([c for c in ("16384", "8192") if context and int(c) < int(context)])
    best = None
    for ctx in contexts:
        base = set_arg(args, CONTEXT_FLAGS, ctx) if ctx else list(args)
        cache: dict[int, Estimate | None] = {}

        def at(step: int) -> Estimate | None:
            if step not in cache:
                cache[step] = estimate(cfg, key, set_arg(base, ("--gpu",), _ratio(step)))
            return cache[step]

        lo, hi = 0, 20  # GPU belleği oranla artar: sığan en büyük adımı ikili aramayla bul
        if (top := at(hi)) and top.gpu <= vram_budget:
            lo = hi
        else:
            while hi - lo > 1:
                mid = (lo + hi) // 2
                e = at(mid)
                if e and e.gpu <= vram_budget:
                    lo = mid
                else:
                    hi = mid
        est = at(lo)
        if est is None:
            return None
        fits = est.gpu <= vram_budget and (ram_budget is None or est.ram <= ram_budget)
        best = Advice(_ratio(lo), ctx or "varsayılan", est, fits)
        if fits:
            break
    return best


# --- yükleme ---

@dataclass
class LoadResult:
    ok: bool
    message: str = ""
    guard_tripped: bool = False


def guarded_load(cfg: dict, key: str, args: list[str], on_tick=None, timeout: float = 900) -> LoadResult:
    """lms load'u RAM bekçisiyle çalıştırır: boş RAM ram_guard_mb'nin altına inerse ya da bellek baskısı psi_guard'ı
    geçerse yükleme durdurulur ve tüm modeller boşaltılır (bellek tükenince sistem takas yapıp kilitleniyor).
    on_tick(boş_ram_bayt) bekleme göstergesi için yaklaşık 10 kez/sn çağrılır."""
    lms = lms_path(cfg)
    if not lms:
        return LoadResult(False, "lms bulunamadı; config.json'daki lms_path ayarını kontrol et")
    guard = int(cfg.get("ram_guard_mb", RAM_GUARD_MB)) * MIB
    psi_guard = float(cfg.get("psi_guard", PSI_GUARD))
    proc = subprocess.Popen([lms, "load", key, *args, "-y"], stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                            start_new_session=os.name != "nt")
    output: list[str] = []
    reader = threading.Thread(target=lambda: output.extend(proc.stdout), daemon=True)  # boru dolup lms tıkanmasın
    reader.start()
    start, lowest, peak = time.monotonic(), None, 0.0
    try:
        while proc.poll() is None:
            avail, pressure = mem_available(), mem_pressure()
            if avail is not None:
                lowest = avail if lowest is None else min(lowest, avail)
            peak = max(peak, pressure or 0.0)
            reason = (f"boş RAM {avail // MIB} MB'a düştü (sınır {guard // MIB} MB)" if avail is not None and avail < guard
                      else f"bellek baskısı %{pressure:.0f} oldu: süreçler zamanın bu kadarında belleği bekledi "
                           f"(sınır %{psi_guard:g})" if pressure is not None and pressure >= psi_guard else "")
            if reason:
                _stop(proc)
                freed = unload_all(cfg, guard)
                return LoadResult(False, f"RAM bekçisi: {reason}; yükleme durduruldu ve modeller boşaltıldı"
                                         + ("" if freed else ", ama RAM hâlâ az: LM Studio'yu kontrol et"),
                                  guard_tripped=True)
            if on_tick:
                on_tick(avail)
            if time.monotonic() - start > timeout:
                _stop(proc)
                unload_all(cfg, guard)
                return LoadResult(False, f"yükleme {timeout:.0f} saniyede bitmedi; durduruldu")
            time.sleep(0.1)
    except KeyboardInterrupt:
        _stop(proc)
        unload_all(cfg, guard)
        raise
    reader.join(timeout=2)
    text = ANSI.sub("", "".join(output)).strip()
    if proc.returncode != 0:
        return LoadResult(False, _error_text(text) or f"lms load çıkış kodu {proc.returncode}")
    note = ", ".join(([f"yüklerken en düşük boş RAM {gib(lowest)}"] if lowest is not None else [])
                     + ([f"en yüksek bellek baskısı %{peak:.0f}"] if mem_pressure() is not None else []))
    return LoadResult(True, note)


def _stop(proc: subprocess.Popen) -> None:
    """lms load'u durdurur: önce Ctrl+C gibi (LM Studio yüklemeyi iptal etsin), olmazsa zorla."""
    try:
        if os.name == "nt":
            proc.terminate()
        else:
            os.killpg(proc.pid, signal.SIGINT)
        proc.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        proc.kill()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass


def unload_all(cfg: dict, guard: int | None = None) -> bool:
    """Tüm modelleri boşaltır. guard verilirse boş RAM ondan yukarı çıkana dek birkaç kez dener (yarım kalan yükleme
    sunucuda bir süre daha sürebiliyor); RAM toparlandıysa True."""
    for _ in range(5 if guard else 1):
        run(cfg, "unload", "--all", timeout=120)
        if guard is None:
            return True
        time.sleep(1)
        avail = mem_available()
        if avail is None or avail >= guard * 1.5:
            return True
    return False


ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _error_text(text: str) -> str:
    """lms çıktısındaki hata: "Error:" satırı (ilerleme çubuğu ve imleç kodları atılır), yoksa son satırlar. Bellek
    yetmediği için çökmeyi (llama-server SIGABRT) açıkça söyler."""
    lines = [line.strip() for line in re.split(r"[\r\n]+", ANSI.sub("", text)) if line.strip()]
    errors = [line[line.find("Error"):] for line in lines if "Error" in line]
    msg = (errors[-1] if errors else " · ".join(lines[-3:]))[:400]
    if "exited before becoming healthy" in msg:
        msg += " (çoğunlukla VRAM yetmedi: --gpu oranını düşür ya da /fit ile öner)"
    return msg
