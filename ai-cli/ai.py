"""Gambit CLI: LM Studio'daki (ya da OpenAI uyumlu herhangi bir sunucudaki) yerel modellerle terminalden
sohbet eder. Model dosya okuyup arayabilir; dosya yazma ve komut çalıştırma senin onayınla olur.
Modeller ekranda config.json'daki hazır ayar adlarıyla (pawn, knight, bishop, rook, queen, king) görünür;
modeli boş ("model": "") bir hazır ayar, ileride doldurulacak boş yuvadır."""

import argparse
import base64
import json
import math
import os
import platform
import queue
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

try:
    import jiter  # noqa: F401
except ImportError:
    # Windows Akıllı Uygulama Denetimi jiter'in imzasız DLL'ini engelleyebiliyor; openai onu yalnızca .stream()
    # yardımcısı için yüklüyor, gambit akışı kendisi okuduğu için gerekmez. Engellenen DLL'i yüklemeyen bir yedek.
    import types as _types

    _jiter = _types.ModuleType("jiter")
    _jiter.from_json = lambda data, partial_mode=False, **_: json.loads(data)
    sys.modules["jiter"] = _jiter

from openai import APIConnectionError, APIStatusError, OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich.box import ROUNDED
from rich.console import Console, Group
from rich.live import Live
from rich.markdown import Heading, Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.segment import Segment
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

import lmstudio
import servers
import tools

HERE = Path(__file__).resolve().parent
HISTORY_FILE = Path.home() / ".ai_cli_history"
# Bazı modeller (ör. Gemma 4) araç çağrısını bazen sunucunun ayrıştıramadığı ham işaretlerle metne yazıyor
BROKEN_TOOL_CALL = re.compile(r"<\|?tool_call|tool_call\|?>|<function=|\[TOOL_CALLS\]")
_TOOL_NAMES = "write_file|edit_file|run_command|run_python|read_file|list_dir|search_files"
# Araç çağrısını gerçekten çağırmak yerine mesaja metin olarak yazma, ör. write_file(path="a.py", content='''...''')
PSEUDO_TOOL_CALL = re.compile(rf"(?m)^[ \t]*(?:{_TOOL_NAMES})\s*\(|\"name\"\s*:\s*\"(?:{_TOOL_NAMES})\"")
# Bir sonraki adımı söyleyip aracı çağırmadan bitirme: "Şimdi testleri çalıştırıyorum", "Düzeltelim:", "Let me ..."
NEXT_STEP = re.compile(
    r"\b(?:yaz|oluştur|kaydet|çalıştır|düzelt|düzenle|güncelle|test ed|dene|kontrol ed|doğrula|oku|bak|incele|ekle|"
    r"başl|değiştir|uygula|hazırla|sorgula|bul|yap|ara|kopyala|taşı|sil)\w*?"
    r"(?:acağım|eceğim|ıyorum|iyorum|uyorum|üyorum|yorum|alım|elim)\b|"
    r"\b(?:let me|i'll|i will|i am going to|i'm going to)\b", re.I)
# Araç kullanmadan iş yapmış gibi konuşma
CLAIMED_WORK = re.compile(
    r"\b(?:oluşturdum|kaydettim|yazdım|güncelledim|düzenledim|düzelttim|doğruladım|çalıştırdım|test ettim|ekledim|"
    r"değiştirdim|oluşturuldu|kaydedildi|yazıldı|güncellendi|düzenlendi|düzeltildi|doğrulandı|çalıştırıldı|"
    r"test edildi|eklendi|değiştirildi)\b|"
    r"\bI(?: have|'ve)? (?:created|saved|written|wrote|ran|run|tested|verified|updated|fixed)\b|"
    r"\b(?:has been|have been|was|were) (?:created|saved|written|updated)\b", re.I)
FILE_MENTION = re.compile(
    r"(?<![\w/\\.-])[\w-][\w./\\-]*\.(?:py|js|mjs|cjs|ts|sql|ps1|sh|json|md|html|css|txt|csv|ini|ya?ml|toml)\b")
PY_INLINE = re.compile(r"\bpy(?:thon\d*)?(?:\.exe)?\s+(?:-\S+\s+)*-c\b", re.I)
NOT_FOUND = re.compile(r"['‘]([^'’\n]+)['’] (?:terimi bir cmdlet|is not recognized as)|(?:^|\s)([\w.-]+): (?:command )?not found",
                       re.M)
SQLITE_DOT = re.compile(r"""execute\w*\(\s*[rRbBuU]?(?:'{1,3}|"{1,3})\s*\.(?:schema|tables|headers|mode|indexes)\b""")
RUN_TOOLS = ("run_command", "run_python")
THOUGHT_CUT = "[My unfinished reasoning, cut off by the output length limit before I wrote an answer:]"
THOUGHT_KEEP = 3500  # düşünürken kesilen modelin düşüncesinden geçmişte tutulan son karakterler
NOT_RERUN = "Not executed:"  # başarısız komutun değişmeden tekrarı çalıştırılmadığında sonucun başı
COMPACT_MARK = "[… Gambit: bağlam için kısaltıldı"
CHARS_PER_TOKEN = 3.2
LOOP_LIMIT = 5  # aynı araç çağrısı (ad + argümanlar) bir turda bu kadar tekrarlanırsa tur durdurulur

# Her modelin taşı ve renkleri (arayüzde vurgu ve degrade için); orta tonlar açık ve koyu terminalde okunur
PIECES = {"pawn": ("♟", "#87afaf", "#5f8787"), "knight": ("♞", "#00afd7", "#5f5fd7"), "rook": ("♜", "#d78700", "#d75f5f"),
          "queen": ("♛", "#af5fd7", "#5f87d7"), "bishop": ("♝", "#5faf5f", "#00afaf"),
          "king": ("♚", "#d7af00", "#d75f00")}
DEFAULT_PIECE = ("♟", "#5f87d7", "#af5fd7")
MUTED = "#8a8a8a"
THEME = Theme({"markdown.h1": "bold underline", "markdown.h2": "bold", "markdown.h3": "bold italic",
               "markdown.code": "bold cyan", "markdown.block_quote": f"italic {MUTED}", "markdown.hr": MUTED,
               "markdown.item.bullet": "bold", "markdown.link": "underline"})
console = Console(highlight=False, theme=THEME)
LOGO = [
    " ██████   █████  ███    ███ ██████  ██ ████████",
    "██       ██   ██ ████  ████ ██   ██ ██    ██   ",
    "██   ███ ███████ ██ ████ ██ ██████  ██    ██   ",
    "██    ██ ██   ██ ██  ██  ██ ██   ██ ██    ██   ",
    " ██████  ██   ██ ██      ██ ██████  ██    ██   ",
]

COMMANDS = {
    "/help": "Komutları gösterir",
    "/model": "Modelleri listeler (diskte olmayanlar ayrı); /model <ad> ile yüklü olana geçer",
    "/load": "Modeli kendi ayarlarıyla yükler, ör. /load queen (diğer modelleri boşaltır, RAM'i gözetler)",
    "/fit": "Modelin belleğe sığıp sığmadığını hesaplar, GPU oranı ve bağlam önerir; ör. /fit rook",
    "/vision": "Görsel modu açar/kapatır: model görsel ekiyle (ya da eksiz) kendi ayarıyla yeniden yüklenir",
    "/image": "Sonraki mesaja resim ekler, ör. /image ekran.png (görsel modda); /image yalnız: eklenenleri siler",
    "/unload": "Yüklü tüm modelleri boşaltır",
    "/clear": "Yeni sohbet başlatır",
    "/undo": "Modelin yaptığı son dosya değişikliğini geri alır",
    "/compact": "Eski araç çıktılarını kısaltıp bağlamda yer açar",
    "/tools": "Araçları açar/kapatır",
    "/think": "Düşünmeyi açar/kapatır ya da düzeyini seçer: /think off, on, low, medium, high, xhigh",
    "/show": "Düşünme metnini ekranda gösterir/gizler",
    "/auto": "Onay sormayı açar/kapatır (dikkatli kullan)",
    "/exit": "Çıkış (Ctrl+D de olur)",
}


def load_config() -> dict:
    """config.json; hazır ayarlar diskteki modellerle eşleştirilmiş olarak (bkz. lmstudio.resolve_presets)."""
    with open(HERE / "config.json", encoding="utf-8") as f:
        cfg = json.load(f)
    lmstudio.resolve_presets(cfg, lmstudio.catalog(cfg))
    return cfg


def _get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=5) as r:
        return json.load(r)


def server_models(base_url: str) -> list[dict] | None:
    """Sunucudaki modeller (LM Studio ise yüklü mü, bağlam uzunluğu vb. ile). Sunucuya ulaşılamazsa None."""
    base_url = base_url.rstrip("/")
    try:
        data = _get_json(base_url.removesuffix("/v1") + "/api/v0/models")["data"]
        return [m for m in data if m.get("type") in ("llm", "vlm") and m.get("arch") != "clip"]
    except urllib.error.HTTPError:
        pass  # LM Studio değil; standart OpenAI model listesine düş
    except (urllib.error.URLError, OSError, ValueError, KeyError):
        return None
    try:
        return [{"id": m["id"], "state": "loaded"} for m in _get_json(base_url + "/models")["data"]]
    except Exception:
        return None


lms_path = lmstudio.lms_path  # benchmark betikleri ai.lms_path'i kullanıyor


def is_local(base_url: str) -> bool:
    return "localhost" in base_url or "127.0.0.1" in base_url


def ensure_server(cfg: dict, base_url: str) -> list[dict] | None:
    models = server_models(base_url)
    if models is None and is_local(base_url) and lms_path(cfg):
        with console.status(Text("LM Studio sunucusu kapalı, başlatılıyor…", style=MUTED), spinner="dots"):
            lmstudio.run(cfg, "server", "start", timeout=120)
            models = server_models(base_url)
    return models


def initial_effort(cfg: dict, args: argparse.Namespace) -> str:
    """Başlangıç düşünme düzeyi: --effort, --think/--no-think, config.json'daki "effort" (eski "thinking" de olur)."""
    if getattr(args, "effort", None):
        return str(args.effort).lower()
    if getattr(args, "think", None) is not None:
        return "on" if args.think else "off"
    value = cfg.get("effort", cfg.get("thinking", "off"))
    return {True: "on", False: "off", "auto": "off"}.get(value, str(value).lower())  # otomatik mod kaldırıldı


def command_failed(result: str) -> bool:
    """run_command/run_python sonucu başarısız mı (sıfır olmayan çıkış kodu, stderr'de PowerShell hatası, araç hatası)."""
    first = result.split("\n", 1)[0]
    m = re.match(r"çıkış kodu: (-?\d+)", first)
    return bool(m and m.group(1) != "0") or tools.STDERR_WARNING in first or result.startswith("Hata:")


def _command_key(args: dict) -> str:
    """Komutu ya da Python kodunu boşluk farklarından bağımsız karşılaştırmak için anahtar."""
    return " ".join(str(args.get("command") or args.get("code") or "").split())


def _partial_tail(s: str, tag: str) -> int:
    """s'nin sonu tag'in başıyla kaç karakter örtüşüyor (etiketin yarısı gelmiş olabilir)."""
    for k in range(min(len(tag) - 1, len(s)), 0, -1):
        if s.endswith(tag[:k]):
            return k
    return 0


def alias_of(cfg: dict, model: str | None) -> str:
    """Ekranda gösterilecek ad: modelin hazır ayar adı (bishop, queen...). Model kimlikleri gösterilmez."""
    if not model:
        return "model yok"
    return next((k for k, p in cfg.get("presets", {}).items()
                 if model in (p.get("model"), (p.get("vision") or {}).get("model"))
                 or (p.get("server") and model == servers.alias(k))), "tanımsız model")


def all_models(base_url: str) -> list[dict] | None:
    """LM Studio'daki modeller ve Gambit'in başlattığı sunucular (ik_llama.cpp) birlikte; LM Studio'ya ulaşılamazsa None."""
    models = server_models(base_url)
    return None if models is None else models + servers.running()


IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
               ".gif": "image/gif", ".bmp": "image/bmp"}
MAX_IMAGE_BYTES = 10_000_000
IMAGE_CHARS = 2500  # bağlam tahmininde bir resmin kapladığı yer (~800 token)


def image_part(path: str) -> dict:
    """Resim dosyasını mesaja eklenecek OpenAI biçimli parçaya çevirir (data: URL). Sorun varsa ValueError."""
    p = Path(os.path.expanduser(path))
    mime = IMAGE_TYPES.get(p.suffix.lower())
    if not p.is_file():
        raise ValueError(f"dosya bulunamadı: {path}")
    if not mime:
        raise ValueError(f"desteklenmeyen resim türü: {p.suffix or 'uzantısız'} ({', '.join(IMAGE_TYPES)})")
    if p.stat().st_size > MAX_IMAGE_BYTES:
        raise ValueError(f"resim çok büyük ({p.stat().st_size // 1_000_000} MB, sınır 10 MB)")
    data = base64.b64encode(p.read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}, "_name": p.name}


def _one_line(text: str, limit: int = 100) -> str:
    lines = [line.strip() for line in str(text).splitlines() if line.strip()]
    first = lines[0] if lines else ""
    more = len(lines) > 1
    if len(first) > limit:
        first, more = first[: limit - 1], True
    return first + ("…" if more else "")


def _short_args(args: dict) -> str:
    parts = []
    for k, v in args.items():
        if isinstance(v, str) and "\n" in v:
            v = f"<{v.count(chr(10)) + 1} satır>"
        elif isinstance(v, str) and len(v) > 80:
            v = v[:77] + "…"
        parts.append(f"{k}={v}")
    return " ".join(parts)


def _describe_call(name: str, a: dict) -> str:
    """Araç çağrısının ekranda tek satırlık özeti."""
    lines = lambda s: str(s).count("\n") + 1  # noqa: E731
    match name:
        case "run_command":
            return _one_line(a.get("command", ""), 110)
        case "run_python":
            code = str(a.get("code", ""))
            return _one_line(code, 90) + (f"  ({lines(code)} satır)" if lines(code) > 1 else "")
        case "write_file":
            return f"{a.get('path', '')}  ({lines(a.get('content', ''))} satır)"
        case "edit_file":
            return str(a.get("path", ""))
        case "read_file":
            return str(a.get("path", "")) + (f"  (satır {a['start_line']}…)" if a.get("start_line") else "")
        case "list_dir":
            extra = [str(a["pattern"])] if a.get("pattern") not in (None, "", "*") else []
            return " ".join([str(a.get("path") or "."), *extra] + (["(alt klasörler)"] if a.get("recursive") else []))
        case "search_files":
            return f"/{a.get('pattern', '')}/  {a.get('path') or '.'}" + (f"  {a['file_pattern']}" if a.get("file_pattern") else "")
    return _short_args(a)


def _result_summary(name: str, result: str) -> str:
    """Araç sonucunun ekrandaki ilk satırı: modele giden tam metin yerine kısa bir özet."""
    first = result.split("\n", 1)[0]
    if result.startswith("Hata"):
        return first
    cwd = os.getcwd().rstrip("\\/") + os.sep
    if name == "read_file" and (m := re.search(r" \((\d+) satır;", first)):
        shown = len(result.splitlines()) - 1 - ("satır daha var" in result)
        return f"{m.group(1)} satır" + (f" (ilk {shown} gösterildi)" if shown < int(m.group(1)) else "")
    if name == "list_dir" and (m := re.search(r"\((\d+) öğe\)", first)):
        return f"{m.group(1)} öğe"
    if name == "search_files":
        return first if first == "eşleşme yok" else f"{len(result.splitlines())} eşleşme"
    if name in ("write_file", "edit_file"):
        return first.replace(cwd, "") + (" · sözdizimi tamam" if "Syntax check: OK." in result else "")
    if name in RUN_TOOLS:
        return first.replace("çıkış kodu:", "çıkış")
    return first


def _clip(text: str, max_lines: int) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[:max_lines]) + f"\n… (+{len(lines) - max_lines} satır)"


def _error_text(e: APIStatusError) -> str:
    body = e.body
    if isinstance(body, dict):
        err = body.get("error", body)
        return str(err.get("message", err)) if isinstance(err, dict) else str(err)
    return str(e.message)


def _error_line(result: str) -> str:
    """Bir komut sonucundaki asıl hata satırı (aynı hatanın tekrarlanıp tekrarlanmadığını anlamak için)."""
    body = result.split("[stderr]", 1)[1] if "[stderr]" in result else result
    lines = [line.strip() for line in body.splitlines() if line.strip() and not line.startswith("çıkış kodu")]
    return lines[-1][:200] if lines else ""


def _repair_json(raw: str) -> str | None:
    """Araç argümanlarını geçerli bir JSON nesnesine çevirir; onarılamazsa None. Küçük modeller sık sık regex'lerdeki
    ters bölüleri kaçırmayı unutuyor, dizelere ham satır sonu koyuyor ya da nesneden sonra fazladan karakter yazıyor."""
    try:
        return raw if isinstance(json.loads(raw), dict) else None
    except ValueError:
        pass
    for candidate in (raw, re.sub(r'\\(?![\\"/bfnrtu])', r"\\\\", raw)):
        try:
            obj, _ = json.JSONDecoder(strict=False).raw_decode(candidate.strip())
        except ValueError:
            continue
        if isinstance(obj, dict):
            return json.dumps(obj, ensure_ascii=False)
    return None


def _chars(messages: list[dict]) -> int:
    total = 0
    for m in messages:
        content = m.get("content") or ""
        if isinstance(content, list):  # resimli kullanıcı mesajı
            total += sum(len(c.get("text", "")) if c.get("type") == "text" else IMAGE_CHARS for c in content) + 8
        else:
            total += len(content) + 8
        for c in m.get("tool_calls") or []:
            total += len(c["function"]["arguments"]) + len(c["function"]["name"]) + 24
    return total


# --- görünüm ---

def _rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _mix(a: str, b: str, k: float) -> str:
    k = min(1.0, max(0.0, k))
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * k) for x, y in zip(_rgb(a), _rgb(b)))


def _shimmer(label: str, color: str, t: float) -> Text:
    """Soluk metnin üzerinde soldan sağa kayan parlak bir şerit."""
    out = Text()
    pos = (t * 14) % (len(label) + 16) - 8
    for i, ch in enumerate(label):
        out.append(ch, style=_mix(MUTED, color, 1 - abs(i - pos) / 5))
    return out


def _bar(fraction: float, width: int = 10) -> str:
    filled = min(width, max(0, round(fraction * width)))
    return "▰" * filled + "▱" * (width - filled)


class Spinner:
    """Bekleme göstergesi: nabız gibi atan taş, üzerinde ışık kayan etiket, ek bilgi ve geçen süre."""

    def __init__(self, piece: str, color: str, animate: bool):
        self.piece, self.color, self.animate = piece, color, animate
        self.label, self.detail = "", ""
        self.since = time.perf_counter()

    def set(self, label: str, detail: str = "") -> None:
        if label != self.label:
            self.since = time.perf_counter()
        self.label, self.detail = label, detail

    def __rich__(self) -> Text:
        t = time.perf_counter()
        text = Text("  ")
        if self.animate:
            text.append(self.piece, style="bold " + _mix(MUTED, self.color, 0.5 + 0.5 * math.sin(t * 5)))
            text.append(" ")
            text.append_text(_shimmer(self.label, self.color, t))
        else:
            text.append(f"{self.piece} ", style=self.color)
            text.append(self.label, style=MUTED)
        extra = [x for x in (self.detail, f"{t - self.since:.0f} sn") if x]
        text.append("  " + " · ".join(extra), style=MUTED)
        return text


class _Lines:
    """Önceden çizilmiş satırlar (canlı alanda yazılmakta olan bloğun yalnızca son satırlarını göstermek için)."""

    def __init__(self, lines: list[list[Segment]]):
        self.lines = lines

    def __rich_console__(self, _console, _options):
        for line in self.lines:
            yield from line
            yield Segment.line()


class _Heading(Heading):
    LEVEL_ALIGN = {**Heading.LEVEL_ALIGN, "h1": "left"}  # ortalanmış başlık terminalde kaybolup gidiyor


class _Markdown(Markdown):
    elements = {**Markdown.elements, "heading_open": _Heading}


def _md(text: str) -> Markdown:
    return _Markdown(text, code_theme="ansi_dark", hyperlinks=False)


def _stable_cut(src: str) -> int:
    """src'de tamamlanmış son Markdown bloğunun bittiği yer: kod bloğu içinde olmayan son boş satırın sonu (yoksa 0).
    Bundan önceki kısım bir daha değişmeyeceği için kalıcı olarak basılabilir."""
    cut = pos = 0
    fence = ""
    for line in src.splitlines(keepends=True):
        pos += len(line)
        if not line.endswith("\n"):
            break
        s = line.strip()
        m = re.match(r"`{3,}|~{3,}", s)
        if fence:
            if m and s.startswith(fence) and set(s) == {fence[0]}:
                fence = ""
        elif m:
            fence = m.group(0)
        elif not s:
            cut = pos
    return cut


class StreamPrinter:
    """Akan cevabı ekrana yazar. Düşünme kısmı (reasoning_content alanı ya da <think> etiketi) soluk gösterilir ya da
    gizlenir; geçmişe yalnızca asıl cevap (answer) kaydedilir.

    Terminalde cevap Markdown olarak biçimlendirilir: tamamlanan bloklar kalıcı basılır, yazılmakta olan blok ve bekleme
    göstergesi tek bir canlı alanda güncellenir. Terminal değilse (dosyaya/boruya yazılıyorsa) metin olduğu gibi akar."""

    def __init__(self, show_thinking: bool, spinner: Spinner, fancy: bool, markdown: bool = True):
        self.show_thinking = show_thinking
        self.spinner = spinner
        self.fancy, self.markdown = fancy, markdown
        self.answer = ""
        self.thought = ""
        self.think_tokens = 0
        self._buf = ""
        self._pending_ws = ""  # sondaki boşluklar; arkasından metin gelirse yazılır (düz akış)
        self._in_tag = False  # <think> ... </think> arasında mıyız
        self._mode = None  # en son ekrana yazılan tür: "think" | "text"
        self.active = False  # bekleme göstergesi görünüyor mu
        # canlı alan (yalnızca terminalde)
        self._src = ""  # bu bölümün henüz kalıcı basılmamış kaynağı
        self._tail: list[list[Segment]] = []
        self._blocks = 0  # bu bölümde kalıcı basılan blok sayısı
        self._sections = 0  # ekrana basılmış bölüm sayısı (düşünme / cevap)
        self._dirty = False
        self._last_sync = 0.0
        self._live = None
        if fancy:
            self._live = Live(console=console, get_renderable=self._render, refresh_per_second=12.5, transient=True,
                              redirect_stdout=False, redirect_stderr=False)
            self._live.start()

    # bekleme göstergesi

    def show_status(self, label: str, detail: str = "") -> None:
        """Ekrana bir şey akmıyorken ne olduğunu ve ne kadar süredir beklendiğini gösterir."""
        self.spinner.set(label, detail)
        if not self.active and self._mode and not self.fancy:
            console.out("")  # yarım kalan satırı bitir
            self._mode = None
        self.active = True

    def tick(self) -> None:
        if self._dirty:
            self._sync()

    def stop_status(self) -> None:
        self.active = False

    # akış

    def reasoning(self, s: str) -> None:
        self._emit("think", s)

    def content(self, s: str) -> None:
        self._buf += s
        while self._buf:
            tag = "</think>" if self._in_tag else "<think>"
            kind = "think" if self._in_tag else "text"
            i = self._buf.find(tag)
            if i == -1:
                keep = _partial_tail(self._buf, tag)
                self._emit(kind, self._buf[: len(self._buf) - keep])
                self._buf = self._buf[len(self._buf) - keep :]
                return
            self._emit(kind, self._buf[:i])
            self._buf = self._buf[i + len(tag) :]
            self._in_tag = not self._in_tag

    def finish(self) -> None:
        if self._buf:
            self._emit("think" if self._in_tag else "text", self._buf)
            self._buf = ""
        self.stop_status()
        if self.fancy:
            self._end_section()
            self.close()
        elif self._mode:
            console.out("")
        self._mode = None
        self.answer = self.answer.rstrip()

    def close(self) -> None:
        if self._live:
            self._live.stop()
            self._live = None

    def _emit(self, kind: str, s: str) -> None:
        if kind == "think":
            self.thought += s
            if s:
                self.think_tokens += 1
        if kind == "think" and not self.show_thinking:
            if s:
                self.show_status("düşünüyor", f"{self.think_tokens} token")
            return
        if kind != self._mode:
            s = s.lstrip()
            if not s:
                return
            self.stop_status()
            if self.fancy:
                self._end_section()
            elif self._mode:
                console.out("\n")
            self._mode = kind
            self._pending_ws = ""
        if kind == "text":
            self.answer += s
        if self.fancy:
            self.stop_status()
            self._src += s
            self._sync()
            return
        s = self._pending_ws + s
        visible = s.rstrip()
        self._pending_ws = s[len(visible) :]
        console.out(visible, end="", style="dim italic" if kind == "think" else None, highlight=False)

    # canlı alan

    def _render(self):
        parts = []
        if self._tail:
            parts.append(_Lines(self._tail))
        if self.active:
            parts.append(self.spinner)
        return Group(*parts)

    def _renderable(self, text: str):
        if self._mode == "text" and self.markdown:
            return _md(text)
        return Text(text, style="dim italic" if self._mode == "think" else "")

    def _sync(self, final: bool = False) -> None:
        now = time.perf_counter()
        if not final and now - self._last_sync < 0.05:
            self._dirty = True
            return
        self._last_sync, self._dirty = now, False
        if self._mode == "text" and self.markdown:
            cut = len(self._src) if final else _stable_cut(self._src)
        else:
            cut = len(self._src) if final else self._src.rfind("\n") + 1
        done, self._src = self._src[:cut], self._src[cut:]
        if done.strip():
            if self._blocks and self._mode == "text" and self.markdown:
                console.print()
            if self._blocks == 0 and self._sections:
                console.print()  # düşünme ile cevap arasında boşluk
            console.print(self._renderable(done.rstrip("\n") if self._mode != "text" else done.strip("\n")))
            self._blocks += 1
        tail = self._src if self._src.strip() else ""
        if not tail:
            self._tail = []
            return
        lines = console.render_lines(self._renderable(tail.strip("\n")), console.options, pad=False)
        if self._blocks and self._mode == "text" and self.markdown:
            lines = [[]] + lines
        self._tail = lines[-max(4, console.height - 4) :]

    def _end_section(self) -> None:
        if self._mode:
            self._sync(final=True)
            if self._blocks:
                self._sections += 1
        self._src, self._tail, self._blocks = "", [], 0


class _ThinkOverflow(Exception):
    """Model düşünme bütçesini aştı; adım düşünmeden tekrarlanacak."""


@dataclass
class Turn:
    """Kullanıcının tek bir mesajına verilen cevap boyunca tutulan durum."""
    text: str
    missing_files: set = field(default_factory=set)  # mesajda adı geçen ama henüz olmayan dosyalar
    tool_calls: int = 0
    writes: int = 0
    py_runs: int = 0  # istenen dosya kaydedilmeden yapılan run_python sayısı
    nudges: int = 0
    broken_retries: int = 0
    empty_retry: bool = False
    think_rest: bool = False  # boş cevaptan sonra turun geri kalanında düşün
    no_think_next: bool = False  # düşünme bütçesi aşıldı: sonraki adım düşünmeden
    force_compact: bool = False
    failed_commands: dict = field(default_factory=dict)  # başarısız komut -> (o andaki changes, hata satırı)
    changes: int = 0  # dosya yazma ve komut çalıştırma sayısı: başarısız komutu tekrarlamadan önce bir şey değişti mi
    thought_cut: int = 0  # düşünürken uzunluk sınırında kesilme sayısı
    short_tests: bool = False  # adım sınırı yaklaşınca testleri kısa tutması söylendi mi
    pathless: int = 0  # path'siz gelen write_file çağrısı sayısı
    calls: dict = field(default_factory=dict)  # aynı araç çağrısının (ad + argümanlar) bu turda kaç kez yapıldığı
    last_error: str = ""
    same_error: int = 0


class Chat:
    def __init__(self, client: OpenAI, cfg: dict, base_url: str, args: argparse.Namespace):
        self.client = client
        self._clients: dict[str, OpenAI] = {}  # Gambit'in başlattığı sunucular için istemciler (adrese göre)
        self.cfg = cfg
        self.base_url = base_url
        self.model: str | None = None
        self.ctx: int | None = None  # modelin yüklü bağlam uzunluğu
        self.use_tools = not args.no_tools
        self.reasoning: dict[str, tuple[list[str], str]] = {}  # LM Studio'nun bildirdiği düşünme düzeyleri
        self.efforts, self.effort_default = ["off", "on"], "on"  # şu anki modelin düzeyleri
        self.effort_pref = initial_effort(cfg, args)  # kullanıcının istediği düzey
        self.effort = self.effort_pref  # bu modelde geçerli olan düzey (refresh_efforts ayarlar)
        self.step_effort = self.effort  # bu adımda kullanılan düzey
        self.refresh_efforts()
        self.vision = bool(getattr(args, "vision", False) or getattr(args, "image", None))  # görsel mod
        self.pending_images: list[dict] = []  # sonraki mesaja eklenecek resimler (/image)
        self.show_thinking = args.show_think or cfg.get("show_thinking", False)
        self.auto = args.yes
        self.animate = cfg.get("animations", True) and not getattr(args, "no_anim", False)
        self.interactive = False  # sohbet modunda mı (adım sınırında devam etmek için sorulabilir)
        self.always: set[str] = set()  # bu oturumda hep onaylanan araçlar
        self.env = tools.environment()
        self.turn = Turn("")
        self.last_finish: str | None = None
        self.last_tokens: int | None = None  # son isteğin toplam token sayısı (istem + cevap)
        self.last_len = 0  # o istekten sonra geçmişte kaç mesaj vardı
        self.pending_note = ""  # bir sonraki mesaja eklenecek not (ör. /undo)
        self.messages: list[dict] = []
        self.reset()

    def system_prompt(self) -> str:
        lines = [
            f"You are Gambit, a helpful assistant running in the user's terminal, powered by a local model. "
            f"Your current mode is '{alias_of(self.cfg, self.model) if self.model else 'gambit'}'. If asked who or "
            "what you are, introduce yourself by that name; do not name the underlying model or its maker.",
            f"Current directory: {os.getcwd()}",
            f"OS: {platform.system()} {platform.release()} | Date: {date.today().isoformat()}",
            "Always reply in the language the user writes in (usually Turkish). Be concise and practical.",
        ]
        if self.tools_on():
            have, missing = self.env
            shell = tools.SHELL_NAME
            lines += [
                f"You have tools to list, read, search, create and edit files, to run shell commands ({shell}) and "
                "to run Python code.",
                "Use them whenever you need real information; never invent file contents or command output.",
                "Relative paths are relative to the current directory. For files in the current directory use a "
                "relative path (for example notes.py), not an absolute path.",
                f"Installed programs: {', '.join(have) or 'none'}." + (f" Not installed: {', '.join(missing)}."
                                                                       if missing else ""),
                (f"run_command uses {shell}: write PowerShell syntax, not bash. For any Python code (tests, data "
                 "processing, SQLite queries) use run_python instead of python -c, which breaks on PowerShell quoting."
                 if tools.POWERSHELL else f"run_command uses {shell}. For any Python code use run_python instead of "
                 "python -c."),
                "Read a file before editing it. Use edit_file for small changes, write_file for new files or full rewrites.",
                "When the user asks you to write or create a program, script or file, save it with write_file; do not "
                "paste the whole file into the chat instead. If they also ask you to run it, run it.",
                "run_python only runs code in memory; it never creates or saves a file. When a file is requested, save "
                "a first working version with write_file early, then test the saved file (import it or run it) and "
                "improve it, so a usable file exists even if you are stopped before you finish.",
                "Never say that you created a file, ran a command or verified something unless a tool result in this "
                "conversation confirms it.",
                "write_file, edit_file, run_command and run_python ask the user for approval. If the user rejects, "
                "follow their note or ask what they want instead.",
                "After writing or changing code you MUST verify it yourself before finishing; never ask the user to run "
                "it for you. write_file and edit_file already check the syntax, so also run its tests or exercise it "
                "with a short script in run_python (for a web app, call it through its test client, e.g. Flask's "
                "app.test_client()). If the check fails, fix the code and check again. Briefly tell the user what you "
                "verified.",
                "If a command fails, read the error and fix its cause; never repeat the same failing command.",
                "Never stop right after announcing a next step: either call the tool for it or finish with a summary.",
                "Never run commands that do not finish on their own (web servers, watchers, interactive programs that "
                "wait for keyboard input); they hang until the timeout. Check those another way (syntax check, a short "
                "script that imports and tests the logic) and tell the user the command to start them themselves.",
                "Never remove or weaken a requested feature just to make a check pass (for example deleting input() "
                "calls so a game exits cleanly). If something cannot be verified here, keep it and say so honestly.",
            ]
        return "\n".join(lines)

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt()}]
        self.last_tokens, self.last_len = None, 0

    def set_model(self, name: str, models: list[dict] | None) -> bool:
        """name: hazır ayar adı (queen) ya da adın başı (q); model kimliği de kabul edilir ama gösterilmez."""
        presets = self.cfg.get("presets", {})
        aliases = [k for k in presets if k == name.lower()] or [k for k in presets if k.startswith(name.lower())]
        if len(aliases) == 1 and lmstudio.is_empty_slot(presets[aliases[0]]):
            console.print(f"[yellow]{escape(aliases[0])} boş bir yuva; önce config.json'da ona bir model ata.[/]")
            return False
        if len(aliases) == 1:
            p = presets[aliases[0]]
            if p.get("_disk", True) is None and not any(m["id"] == p.get("model") for m in models or []):
                self._missing_note(aliases[0], p)
                return False
            v = lmstudio.vision_of(p)
            loaded = {m["id"] for m in models or [] if m.get("state") == "loaded"}
            if v and v["model"] in loaded and p["model"] not in loaded:
                self.vision = True  # yüklü olan görsel model: görsel mod açık
            elif p["model"] in loaded and not (v and v["model"] in loaded):
                self.vision = False
            if self.vision and not v:
                self._note(f"{aliases[0]} modelinin görsel eki yok; görsel mod kapalı.", "yellow")
                self.vision = False
            model = v["model"] if self.vision and v else p["model"]
            server_id = servers.alias(aliases[0])
            if any(m["id"] == server_id for m in models or []):
                self.vision, model = False, server_id  # metin modu sunucuda (ik_llama.cpp) yüklü
            elif not self.vision and p.get("server") and servers.binary(p):
                model = server_id
        elif any(m["id"] == name for m in models or []):
            model = name
        else:
            reason = "model yok" if not aliases else "birden fazla model var: " + ", ".join(aliases)
            console.print(f"[red]'{escape(name)}' ile eşleşen {escape(reason)}[/]")
            return False
        info = next((m for m in models or [] if m["id"] == model), {})
        self.model = model
        self.ctx = info.get("loaded_context_length")
        self.messages[0]["content"] = self.system_prompt()
        self.reasoning = lmstudio.reasoning_options(self.base_url)
        self.refresh_efforts()
        if info and info.get("state") != "loaded":
            console.print("[yellow]Bu model yüklü değil; ilk mesajda LM Studio varsayılan ayarlarla yükler. "
                          f"Kendi ayarlarıyla yüklemek için: /load {alias_of(self.cfg, model)}[/]")
        elif not info and model.startswith("gambit-") and not self.on_server():
            console.print(f"[yellow]{escape(self.name())} yüklü değil; yüklemek için: /load {escape(self.name())}[/]")
        return True

    def on_server(self) -> dict | None:
        """Şu anki model Gambit'in başlattığı bir sunucudaysa onun kaydı ("_base_url" ile)."""
        return next((m for m in servers.running() if m["id"] == self.model), None)

    def _client(self) -> OpenAI:
        """İsteğin gideceği sunucu: model Gambit'in başlattığı sunucudaysa o, değilse LM Studio."""
        srv = self.on_server() if self.model and self.model.startswith("gambit-") else None
        if not srv:
            return self.client
        url = srv["_base_url"]
        if url not in self._clients:
            self._clients[url] = OpenAI(base_url=url, api_key="gambit", timeout=3600, max_retries=0)
        return self._clients[url]

    def name(self) -> str:
        return alias_of(self.cfg, self.model)

    def piece(self) -> tuple[str, str, str]:
        return PIECES.get(self.name(), DEFAULT_PIECE)

    def fancy(self) -> bool:
        """Canlı alan, animasyon ve Markdown biçimi: yalnızca gerçek bir terminalde."""
        return console.is_terminal

    def _preset(self) -> dict:
        return self.cfg.get("presets", {}).get(self.name(), {})

    def can_think(self) -> bool:
        """Düşünme açılıp kapatılabiliyor mu: model hem düşünmeden hem düşünerek çalışabiliyorsa."""
        return "off" in self.efforts and len(self.efforts) > 1

    def refresh_efforts(self) -> None:
        """Modelin düşünme düzeylerini belirler: hazır ayardaki "efforts", yoksa LM Studio'nun bildirdiği, yoksa
        açık/kapalı. Eski "thinking": false (düşünemez) ve "always" (kapatılamaz) ayarları da geçerli."""
        p = self._preset()
        opts, default = list(p["efforts"]) if p.get("efforts") else None, p.get("effort_default")
        srv = p.get("server") or {}
        if self.model and self.model == servers.alias(self.name()) and srv.get("efforts"):
            opts, default = list(srv["efforts"]), srv.get("effort_default")  # sunucu düzeyi şablona doğrudan iletir
        if opts is None and self.model in self.reasoning:
            opts, default = self.reasoning[self.model]
        opts = opts or ["off", "on"]
        if p.get("thinking") is False:
            opts = ["off"]
        elif p.get("thinking") == "always":
            opts = [o for o in opts if o != "off"] or ["on"]
        self.efforts = opts
        self.effort_default = default if default in opts else next((o for o in reversed(opts) if o != "off"), "off")
        self.effort = self._resolve_effort(self.effort_pref)
        self.step_effort = self.effort
        self.thinking = self.effort != "off"

    def _resolve_effort(self, want: str) -> str:
        """İstenen düzeyin bu modeldeki karşılığı: varsa kendisi; "on" ya da modelde olmayan bir düzey modelin
        varsayılanı; "off" kapatılamayan modelde en düşük düzey."""
        if want in self.efforts:
            return want
        if want == "off":
            return self.efforts[0]
        return self.effort_default

    def set_effort(self, arg: str) -> None:
        """/think: düzeyi seçer; düzey verilmezse kapalı ile modelin varsayılanı arasında geçer."""
        aliases = {"aç": "on", "ac": "on", "açık": "on", "kapat": "off", "kapalı": "off", "none": "off"}
        want = (arg.lower() if arg.lower() in self.efforts else aliases.get(arg.lower(), arg.lower())) if arg else (
            "on" if self.effort == self.efforts[0] else "off")
        if want not in {"on", "off", *lmstudio.API_EFFORTS}:
            console.print(f"[red]Bilinmeyen düzey: {escape(arg)}.[/] Bu modelde: {', '.join(self.efforts)}")
            return
        self.effort_pref = want
        self.effort = self.step_effort = self._resolve_effort(want)
        self.thinking = self.effort != "off"
        note = f"Düşünme {self._effort_label(self.effort)}."
        if want not in (self.effort, "on"):
            note += f" Bu modelde '{want}' yok, en yakını seçildi."
        self._note(note + f"  [düzeyler: {', '.join(self.efforts)}]")

    @staticmethod
    def _effort_label(level: str) -> str:
        return {"off": "kapalı", "on": "açık"}.get(level, level)

    def tools_on(self) -> bool:
        """Araçlar bu turda gönderilir mi: /tools ile açık ve model araç çağırabiliyor ("tools": false değil)."""
        return self.use_tools and self._preset().get("tools", True)

    def _note(self, text: str, style: str = MUTED) -> None:
        console.print(Text(f"  {text}", style=style))

    # --- sohbet / ajan döngüsü ---

    def ask(self, text: str) -> None:
        if self.pending_note:
            text, self.pending_note = f"{self.pending_note}\n\n{text}", ""
        start = len(self.messages)
        if self.pending_images:
            parts = [{k: v for k, v in img.items() if k != "_name"} for img in self.pending_images]
            self.messages.append({"role": "user", "content": [{"type": "text", "text": text}, *parts]})
            self.pending_images = []
        else:
            self.messages.append({"role": "user", "content": text})
        turn = self.turn = Turn(text, missing_files={m for m in FILE_MENTION.findall(text) if not Path(m).exists()})
        limit = self.cfg.get("max_steps", 25)
        step = 0
        try:
            while True:
                if step >= limit:
                    if not self._continue_after_limit(limit):
                        console.print("[yellow]Adım sınırına ulaşıldı, durduruldu.[/]")
                        return
                    limit += self.cfg.get("max_steps", 25)
                step += 1
                self._choose_thinking()
                self._compact_if_needed(force=turn.force_compact)
                turn.force_compact = False
                try:
                    calls = self._complete()
                except _ThinkOverflow:
                    turn.no_think_next = True
                    lowest = "düşünmeden" if self.efforts[0] == "off" else f"en düşük düzeyle ({self.efforts[0]})"
                    self._note(f"Düşünme {self._think_budget()} token sınırını aştı; bu adım {lowest} tekrarlanıyor.",
                               "yellow")
                    continue
                if not calls:
                    if self._nudge():
                        continue
                    return
                for call in calls:
                    turn.tool_calls += 1
                    result = self._run_tool(call)
                    result = self._diagnose(call, result, limit - step)
                    self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
                if max(turn.calls.values(), default=0) >= LOOP_LIMIT:
                    console.print(f"[yellow]Model aynı adımı {LOOP_LIMIT} kez tekrarladı ve döngüye girdi; "
                                  "durduruldu.[/] Farklı bir şekilde sormayı ya da daha büyük bir modeli dene.")
                    return
        except KeyboardInterrupt:
            console.print("\n[yellow]Durduruldu.[/]")
            self._close_pending()
        except (APIConnectionError, APIStatusError) as e:
            if isinstance(e, APIStatusError):
                console.print(f"[red]Sunucu hatası ({e.status_code}): {escape(_error_text(e))}[/]")
            else:
                console.print(f"[red]Sunucuya bağlanılamadı ({escape(self.base_url)}).[/] Şunu çalıştır: lms server start")
            if len(self.messages) == start + 1:
                self.messages.pop()  # cevapsız kalan soruyu geçmişe bırakma
        finally:
            self.step_effort = self.effort  # turda geçici değişen düzeyi geri al
            self.thinking = self.effort != "off"

    def _choose_thinking(self) -> None:
        """Bu adımda hangi düzeyle düşünülecek: seçilen düzey; düşünme bütçesi aşıldıysa bu adım düşünmeden, model
        düşünmeden boş döndüyse turun geri kalanı modelin varsayılan düzeyiyle."""
        t = self.turn
        level = self.effort
        if t.no_think_next:
            t.no_think_next = False
            level = self.efforts[0]  # en düşük düzey: kapalı ya da kapatılamayan modelde low
        elif t.think_rest and level == "off":
            level = self.effort_default
        self.step_effort, self.thinking = level, level != "off"

    def _api_effort(self) -> str | None:
        """İstekteki reasoning_effort: kapalı "none", "on" modelin varsayılanı (gönderilmez), kademeli düzey kendisi."""
        level = self.step_effort
        if level == "off":
            return "none" if self.can_think() else None
        return level if level in lmstudio.API_EFFORTS else None

    def _think_budget(self) -> int:
        return int(self.cfg.get("think_budget", 6144) or 0)

    def _continue_after_limit(self, limit: int) -> bool:
        if not self.interactive:
            return False
        try:
            ans = console.input(Text.assemble(("  ? ", "bold yellow"), (f"Adım sınırına ({limit}) ulaşıldı. ", "bold"),
                                              ("Devam etsin mi? [E/h] ", MUTED))).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return False
        return ans in ("", "e", "evet", "y", "yes")

    def _say_to_model(self, shown: str, message: str) -> None:
        self._note(f"↻ {shown}")
        self.messages.append({"role": "user", "content": f"[Gambit CLI] {message}"})

    def _nudge(self) -> bool:
        """Model araç çağırmadan durduğunda iş yarım kaldıysa modele devam etmesini söyler; söylediyse True."""
        t, last = self.turn, self.messages[-1]
        if last["role"] != "assistant":
            if not self.thinking and not t.empty_retry and self.can_think():
                # Bazı modeller (ör. bazı Gemma ince ayarları) düşünme kapalıyken araç sonucundan sonra boş dönüyor
                t.empty_retry = t.think_rest = True
                self._note("Model boş cevap verdi; düşünme açılarak tekrar deneniyor.")
                return True
            return False
        text = last.get("content") or ""
        if BROKEN_TOOL_CALL.search(text) and t.broken_retries < 2:
            t.broken_retries += 1
            self._say_to_model("Model bozuk bir araç çağrısı üretti; tekrar denemesi isteniyor.",
                               "Your last message contained a malformed tool call, so it was not executed. Call the "
                               "tool again in the correct format; if the task is done, write the result.")
            return True
        if text.startswith(THOUGHT_CUT) and t.thought_cut <= 2:
            self._say_to_model("Düşünürken kesildi; düşündüklerinden devam edip cevabı yazması isteniyor.",
                               "You ran out of output tokens while still thinking, before writing any answer. The end of "
                               "your reasoning is in your previous message. Do not start over or repeat it: think only "
                               "briefly, then write your final answer now"
                               + (" (or make the next tool call)." if self.tools_on() else "."))
            return True
        if t.nudges >= 2:
            return False
        reason = None
        if self.last_finish == "length":
            reason = ("Cevap uzunluk sınırında kesildi; devam etmesi isteniyor.",
                      "Your last message was cut off by the output length limit. Continue exactly where it stopped, "
                      "without repeating. If you were writing a file, write it with write_file in smaller parts.")
        elif not self.tools_on():
            pass
        elif PSEUDO_TOOL_CALL.search(text):
            reason = ("Model aracı çağırmak yerine metin olarak yazdı; gerçekten çağırması isteniyor.",
                      "You wrote a tool call as plain text in your message, so it was NOT executed and nothing "
                      "happened. Call the tool for real, as a tool call.")
        elif text.rstrip().endswith(":") or NEXT_STEP.search(text[-300:]):
            reason = ("Model bir sonraki adımı söyleyip durdu; devam etmesi isteniyor.",
                      "You described your next step but did not call any tool, so it did not happen and the task is "
                      "not finished. Do that step now with a tool call. If everything is actually finished, write your "
                      "complete final answer for the user instead (not just 'done').")
        elif t.tool_calls == 0 and CLAIMED_WORK.search(text) and re.search(r"\.\w{1,5}\b|dosya|komut|test|file|command",
                                                                            text, re.I):
            reason = ("Model araç kullanmadan iş yaptığını söyledi; gerçekten yapması isteniyor.",
                      "You said you created, ran or verified something, but you have not called any tool in this task, "
                      "so nothing was actually done. Do the work now with the tools, or tell the user plainly that it "
                      "was not done.")
        elif ((missing := sorted(f for f in t.missing_files if not Path(f).exists()))
              and ("```" in text or t.py_runs or CLAIMED_WORK.search(text))):
            where = ("you only ran the code with run_python, which does not save anything" if t.py_runs
                     else "the code is only in your message")
            reason = (f"İstenen dosya kaydedilmedi ({', '.join(missing)}); kaydetmesi isteniyor.",
                      f"The user asked for {', '.join(missing)}, but it does not exist: {where}. Save it with "
                      "write_file now, then run or import the saved file to verify it. Do not claim it was created "
                      "until a write_file result confirms it.")
        if not reason:
            return False
        t.nudges += 1
        self._say_to_model(*reason)
        return True

    def _diagnose(self, call: dict, result: str, remaining: int) -> str:
        """Araç sonucuna, modelin aynı hatayı tekrarlamaması için CLI'nin gözlemlerini ekler."""
        t = self.turn
        name = call["function"]["name"]
        try:
            args = json.loads(call["function"]["arguments"] or "{}")
        except ValueError:
            args = None
        args = args if isinstance(args, dict) else {}
        hints = []
        if result.startswith("Hata: argümanlar geçerli bir JSON") and (self.last_finish == "length" or self._near_full()):
            t.force_compact = True
            hints.append("The tool call was cut off because the output or context limit was reached, so it was not "
                         "executed. Older tool outputs are being shortened now; retry, and write long files in smaller "
                         "pieces (write_file the first part, then add the rest with edit_file).")
        if name in ("write_file", "edit_file") and not result.startswith(("Hata", "Kullanıcı")):
            t.writes += 1
            t.changes += 1
            written = tools._path(str(args.get("path", "")))
            wanted = [f for f in t.missing_files if Path(f).name == written.name and not Path(f).exists()]
            if wanted:
                hints.append(f"You saved it to {written}, but the user asked for {wanted[0]} in the current directory "
                             f"({os.getcwd()}). Write it again with the relative path {wanted[0]}.")
        key = name + json.dumps(args, sort_keys=True, ensure_ascii=False)
        t.calls[key] = t.calls.get(key, 0) + 1
        if t.calls[key] >= 3:
            hints.append(f"You have made this exact {name} call {t.calls[key]} times in this task. Repeating it gives the "
                         "same result: change something (fix the code, try another approach) or finish with your answer.")
        if name in RUN_TOOLS and not result.startswith(("Kullanıcı", NOT_RERUN)):
            t.changes += 1
            hints += self._command_hints(name, args, result)
        missing = sorted(f for f in t.missing_files if not Path(f).exists())
        if name == "run_python" and missing and not result.startswith("Kullanıcı"):
            t.py_runs += 1
            if t.py_runs >= 2:
                hints.append(f"{', '.join(missing)} is still not saved: run_python does not create files. Save your "
                             "current version with write_file now, then keep testing the saved file.")
        if 2 < remaining <= 5 and not self.interactive and not t.short_tests:
            t.short_tests = True
            hints.append(f"Only {remaining} steps left before the step limit. From now on keep testing short: one quick "
                         "run of the saved file with a few checks, no new large test scripts or test suites. Make sure "
                         "the requested files are saved, then finish with your answer.")
        if 0 < remaining <= 2 and not self.interactive:
            hints.append(f"Only {remaining} step(s) left before the step limit: finish the task now (make sure the "
                         "final files are saved and verified); do not start anything new.")
        if not hints:
            return result
        for h in hints:
            self._note(f"  ↳ {_one_line(h, 110)}", f"italic {MUTED}")
        return result + "\n\n[Gambit CLI hint] " + " ".join(hints)

    def _command_hints(self, name: str, args: dict, result: str) -> list[str]:
        t = self.turn
        key = _command_key(args)
        if not command_failed(result):
            t.same_error, t.last_error = 0, ""
            t.failed_commands.pop(key, None)
            if result.strip() == "çıkış kodu: 0":
                return ["It succeeded but printed nothing. If you expected output, the code never prints it (for "
                        "example a function whose result is not passed to print()); fix the code instead of rerunning it."]
            return []
        code = str(args.get("command") or args.get("code") or "")
        hints = []
        if name == "run_command" and tools.POWERSHELL and PY_INLINE.search(code):
            if '\\"' in code:
                hints.append("PowerShell does not treat \\\" as an escaped quote, so the quotes inside this python -c "
                             "command broke. Use the run_python tool for Python code instead: it needs no quoting.")
            elif re.search(r"SyntaxError|ParserError|unexpected|Unexpected", result):
                hints.append("Quoting Python code inside a PowerShell command is error-prone; use the run_python tool.")
        if m := NOT_FOUND.search(result):
            prog = m.group(1) or m.group(2)
            if re.fullmatch(r"[\w.-]+", prog):
                hints.append(f"'{prog}' is not installed on this machine (installed: {', '.join(self.env[0]) or 'none'})."
                             + (" For SQLite databases use Python's sqlite3 module with run_python."
                                if "sqlite" in prog.lower() else ""))
        if SQLITE_DOT.search(code):
            hints.append("'.schema' and '.tables' are sqlite3 shell commands, not SQL, so they fail in Python. "
                         "Use SELECT name, sql FROM sqlite_master instead.")
        err = _error_line(result)
        if key in t.failed_commands:
            hints.append("This exact command already failed earlier in this task. Do not repeat it; change the approach.")
        t.failed_commands[key] = (t.changes, err)
        t.same_error = t.same_error + 1 if err and err == t.last_error else 1
        t.last_error = err
        if t.same_error >= 3:
            hints.append(f"The last {t.same_error} attempts failed with the same error ({err[:120]}). Stop making small "
                         "variations of the same command: rethink the problem and use a different method.")
        return hints

    # --- bağlam ---

    def _context_limit(self) -> int | None:
        return self.ctx or self.cfg.get("context_length")

    def _estimate_tokens(self) -> int:
        if self.last_tokens is None or self.last_len > len(self.messages):
            return int(_chars(self.messages) / CHARS_PER_TOKEN) + 1500  # araç şemaları için pay
        return self.last_tokens + int(_chars(self.messages[self.last_len :]) / CHARS_PER_TOKEN)

    def _near_full(self) -> bool:
        limit = self._context_limit()
        return bool(limit and self._estimate_tokens() > 0.9 * limit)

    def _compact_if_needed(self, force: bool = False) -> int:
        """Bağlam dolmaya yaklaştıysa eski araç çıktılarını ve dosya içeriklerini kısaltır (16k bağlamlı yerel modellerde
        uzun görevler yoksa bağlamı doldurup araç çağrısını yarıda kesiyor). Kazanılan token sayısını döndürür."""
        limit = self._context_limit()
        if not limit:
            return 0
        est = self._estimate_tokens()
        if est < 0.62 * limit and not force:
            return 0
        saved = self._compact(max(est - int(0.45 * limit), 1500 if force else 0))
        if saved:
            self.last_tokens = max(0, (self.last_tokens if self.last_tokens is not None else est) - saved)
            self._note(f"Bağlam %{est * 100 // limit} doluydu; eski araç çıktıları kısaltıldı (~{saved} token açıldı).")
        return saved

    def _compact(self, need_tokens: int) -> int:
        tool_idx = [i for i, m in enumerate(self.messages) if m["role"] == "tool"]
        asst_idx = [i for i, m in enumerate(self.messages) if m["role"] == "assistant"]
        # son adımların ayrıntısı modelin işine yarıyor; yine de yetmezse yalnızca en son çıktı korunur
        saved = self._compact_pass(need_tokens * CHARS_PER_TOKEN, set(tool_idx[-2:]) | set(asst_idx[-2:]))
        if saved < need_tokens * CHARS_PER_TOKEN:
            saved += self._compact_pass(need_tokens * CHARS_PER_TOKEN - saved, set(tool_idx[-1:]) | set(asst_idx[-1:]))
        return int(saved / CHARS_PER_TOKEN)

    def _compact_pass(self, need: float, protect: set[int]) -> int:
        """Korunanlar dışındaki eski mesajları kısaltır; kazanılan karakter sayısını döndürür."""
        saved = 0

        def shorten(value: str, head_lines: int, head_chars: int) -> str:
            lines = value.splitlines()
            head = "\n".join(lines[:head_lines])[:head_chars]
            return f"{head}\n{COMPACT_MARK}: {len(lines)} satırdı; gerekirse aracı tekrar çalıştır ya da dosyayı yeniden oku]"

        for stage in ("tool", "args", "text"):
            for i, m in enumerate(self.messages):
                if saved >= need:
                    return saved
                if i == 0 or i in protect or m["role"] == "user":
                    continue
                if stage == "tool" and m["role"] == "tool":
                    c = m.get("content") or ""
                    if len(c) > 600 and COMPACT_MARK not in c:
                        m["content"] = shorten(c, 8, 500)
                        saved += len(c) - len(m["content"])
                elif stage == "args" and m.get("tool_calls"):
                    for call in m["tool_calls"]:
                        raw = call["function"]["arguments"]
                        try:
                            args = json.loads(raw)
                        except ValueError:
                            continue
                        changed = False
                        for k, v in args.items():
                            if isinstance(v, str) and len(v) > 400 and COMPACT_MARK not in v:
                                args[k], changed = shorten(v, 4, 150), True
                        if changed:
                            call["function"]["arguments"] = json.dumps(args, ensure_ascii=False)
                            saved += len(raw) - len(call["function"]["arguments"])
                elif stage == "text" and m["role"] == "assistant":
                    c = m.get("content") or ""
                    if len(c) > 1500 and COMPACT_MARK not in c:
                        m["content"] = shorten(c, 12, 600)
                        saved += len(c) - len(m["content"])
        return saved

    # --- model çağrısı ---

    def _complete(self) -> list[dict]:
        """Modelden tek bir cevap akıtır; istediği araç çağrılarını döndürür."""
        kwargs = {
            "model": self.model, "messages": self.messages, "stream": True,
            "stream_options": {"include_usage": True},
        }
        if self.tools_on():
            kwargs["tools"] = tools.schemas()
        if effort := self._api_effort():
            kwargs["reasoning_effort"] = effort  # "none" LM Studio'da düşünmeyi gerçekten kapatır
        if self.cfg.get("temperature") is not None:
            kwargs["temperature"] = self.cfg["temperature"]

        piece, color, _ = self.piece()
        out = StreamPrinter(self.show_thinking, Spinner(piece, color, self.animate), self.fancy(),
                            self.cfg.get("markdown", True))
        calls: dict[int, dict] = {}
        usage = None
        first = None
        # Bütçe yalnızca daha düşük bir düzeye inilebiliyorsa: aşılınca adım en düşük düzeyle tekrarlanır
        budget = self._think_budget() if self.thinking and self.step_effort != self.efforts[0] else 0
        self.last_finish = None
        out.show_status("bağlam işleniyor")
        # Akış ayrı bir iş parçacığında okunur; böylece model bir süre hiçbir şey göndermediğinde (ör. LM Studio araç
        # çağrısını tamamlanana kadar tutarken) ekranda ne olduğu ve geçen süre gösterilebilir.
        chunks: queue.Queue = queue.Queue()
        holder: dict = {}

        def pump() -> None:
            try:
                holder["stream"] = self._client().chat.completions.create(**kwargs)
                for item in holder["stream"]:
                    chunks.put(item)
            except Exception as e:
                chunks.put(e)
            chunks.put(None)

        def close_stream() -> None:
            try:
                holder["stream"].close()  # sunucunun üretmeyi bırakması için bağlantıyı kapat
            except Exception:
                pass

        threading.Thread(target=pump, daemon=True).start()
        last = time.perf_counter()
        try:
            while True:
                try:
                    chunk = chunks.get(timeout=0.1)
                except queue.Empty:
                    if not out.active and time.perf_counter() - last > 2:
                        name = next((c["name"] for c in calls.values() if c["name"]), "")
                        size = sum(len(c["arguments"]) for c in calls.values())
                        out.show_status(f"{name} hazırlanıyor" if name else "araç çağrısı hazırlanıyor olabilir",
                                        f"{size / 1000:.1f}k karakter" if size else "")
                    out.tick()
                    continue
                if chunk is None:
                    break
                if isinstance(chunk, Exception):
                    raise chunk
                last = time.perf_counter()
                first = first or last
                if chunk.usage:
                    usage = chunk.usage
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                if getattr(choice, "finish_reason", None):
                    self.last_finish = choice.finish_reason
                delta = choice.delta
                reasoning = getattr(delta, "reasoning_content", None) or getattr(delta, "reasoning", None)
                if reasoning:
                    out.reasoning(reasoning)
                if delta.content:
                    out.content(delta.content)
                for tc in delta.tool_calls or []:
                    slot = calls.setdefault(tc.index or 0, {"id": "", "name": "", "arguments": ""})
                    slot["id"] = tc.id or slot["id"]
                    if tc.function and tc.function.name:
                        slot["name"] += tc.function.name
                        out.show_status(f"{slot['name']} hazırlanıyor")
                    if tc.function and tc.function.arguments:
                        slot["arguments"] += tc.function.arguments
                if budget and out.think_tokens > budget and not out.answer.strip() and not calls:
                    close_stream()
                    out.finish()
                    raise _ThinkOverflow
        except KeyboardInterrupt:
            close_stream()
            out.finish()
            self._save_assistant(out.answer, [])
            raise
        finally:
            out.stop_status()
            out.close()
        out.finish()

        tool_calls, history = [], []
        for i, c in sorted(calls.items()):
            cid = c["id"] or f"call_{i}_{len(self.messages)}"
            raw = c["arguments"] or "{}"
            fixed = _repair_json(raw)
            # Bozuk argüman araca olduğu gibi verilir (model hatayı görsün); geçmişe yazılırsa LM Studio sonraki
            # istekte 500 veriyor, o yüzden geçmişte "{}" durur
            tool_calls.append({"id": cid, "type": "function", "function": {"name": c["name"], "arguments": fixed or raw}})
            history.append({"id": cid, "type": "function", "function": {"name": c["name"], "arguments": fixed or "{}"}})
        if not out.answer and not tool_calls and out.thought.strip() and self.last_finish == "length":
            # Düşünürken kesildi: düşüncenin sonu geçmişte kalsın ki model baştan başlamasın ve sıfırdan uydurmasın;
            # cevap gibi gösterilmez (_nudge modelden bunun üzerine cevabı yazmasını ister)
            thought = out.thought.strip()
            self.turn.thought_cut += 1
            self._note(f"Model düşünürken çıktı sınırında kesildi ({out.think_tokens} token); düşüncesinin son kısmı "
                       "saklanıyor.", "yellow")
            self._save_assistant(f"{THOUGHT_CUT}\n" + ("…" if len(thought) > THOUGHT_KEEP else "")
                                 + thought[-THOUGHT_KEEP:], [])
            self._print_stats(usage, first)
            return []
        if not out.answer and not tool_calls and out.thought.strip():
            # Bazı modeller (ör. Qwen3.5) araç kullandıktan sonra cevabın tamamını düşünme kısmına yazıyor
            out.answer = out.thought.strip()
            if not self.show_thinking:
                console.print(_md(out.answer)) if self.fancy() else console.out(out.answer)
        if not out.answer and not tool_calls:
            self._note("(boş cevap)")
        self._save_assistant(out.answer, history)
        if usage:
            self.last_tokens, self.last_len = usage.total_tokens, len(self.messages)
        self._quiet_stats = bool(tool_calls) and not out.answer and (not first or time.perf_counter() - first < 10)
        self._print_stats(usage, first)
        return tool_calls

    def _save_assistant(self, text: str, tool_calls: list[dict]) -> None:
        if not text and not tool_calls:
            return
        msg = {"role": "assistant", "content": text}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def _print_stats(self, usage, first: float | None) -> None:
        if not usage or not first or getattr(self, "_quiet_stats", False):
            return  # yalnızca araç çağıran kısa adımlarda satır kalabalığı yapma
        elapsed = time.perf_counter() - first
        parts = [f"{usage.completion_tokens} token"]
        if elapsed > 0:
            parts.append(f"{usage.completion_tokens / elapsed:.1f} tok/s")
        if self.ctx:
            frac = usage.total_tokens / self.ctx
            parts.append(f"bağlam {_bar(frac)} {usage.total_tokens / 1000:.1f}k/{self.ctx / 1000:.1f}k")
        console.print(Text(f"  {' · '.join(parts)}", style=MUTED))
        if self.ctx and usage.total_tokens > 0.8 * self.ctx:
            self._note("Bağlam dolmak üzere; eski araç çıktıları otomatik kısaltılacak (/clear ile yeni sohbet).",
                       "yellow")

    # --- araçlar ---

    def _tool_header(self, name: str, args: dict, ok: bool = True) -> None:
        _, color, _ = self.piece()
        line = Text("● ", style=color if ok else "red")
        line.append(name, style="bold")
        detail = _describe_call(name, args)
        if detail:
            line.append(f"  {detail}", style=MUTED)
        console.print(line)

    def _show_result(self, tool: tools.Tool, name: str, result: str, elapsed: float) -> None:
        lines = result.splitlines() or [""]
        error = result.startswith("Hata")
        failed = error or (name in RUN_TOOLS and command_failed(result))
        line = Text("  └ ", style=MUTED)
        line.append("✗ " if failed else "✓ ", style="red" if failed else "green")
        line.append(_result_summary(name, result)[:200], style="red" if error else MUTED)
        if elapsed >= 1:
            line.append(f" · {elapsed:.1f} sn", style=MUTED)
        console.print(line)
        if name in ("write_file", "edit_file"):
            for extra in lines[1:]:
                if extra.startswith(("SYNTAX ERROR", "Warning:")):
                    self._note(f"  ⚠ {_one_line(extra, 160)}", "yellow")
            return
        if tool.echo_lines <= 1:
            return
        for extra in lines[1 : tool.echo_lines]:
            console.print(Text(f"    {extra[:200]}", style=MUTED))
        if len(lines) > tool.echo_lines:
            console.print(Text(f"    … (+{len(lines) - tool.echo_lines} satır)", style=MUTED))

    def _show_preview(self, tool: tools.Tool, name: str, args: dict) -> None:
        text = tool.preview(**args)
        if text.startswith("# UYARI: "):
            warning, _, text = text.partition("\n")
            self._note(f"⚠ {warning.removeprefix('# UYARI: ')}", "yellow")
        console.print(Panel(Syntax(_clip(text, 80), tool.preview_lexer, theme="ansi_dark", background_color="default",
                                   word_wrap=True), box=ROUNDED, border_style=MUTED, padding=(0, 1)))

    def _execute(self, tool: tools.Tool, name: str, args: dict) -> str:
        if not (self.fancy() and name in RUN_TOOLS):
            return tool.run(**args)
        piece, color, _ = self.piece()
        spinner = Spinner(piece, color, self.animate)
        spinner.set("çalışıyor")
        with Live(spinner, console=console, refresh_per_second=12.5, transient=True, redirect_stdout=False,
                  redirect_stderr=False):
            return tool.run(**args)

    def _run_tool(self, call: dict) -> str:
        name = call["function"]["name"]
        tool = tools.TOOLS.get(name)
        try:
            args = json.loads(call["function"]["arguments"] or "{}")
            if not isinstance(args, dict):
                raise ValueError("JSON nesnesi bekleniyordu")
        except ValueError as e:
            self._tool_header(name, {}, ok=False)
            cut = {None: "çağrı yarıda kesildi (cevap akışı tamamlanmadı)",
                   "length": "çağrı çıktı uzunluk sınırında kesildi"}.get(self.last_finish, "argümanlar okunamadı")
            self._note(f"└ ✗ {cut}", "red")
            return f"Hata: argümanlar geçerli bir JSON nesnesi değil ({e})."
        if tool is None:
            self._tool_header(name, {}, ok=False)
            self._note("└ ✗ bilinmeyen araç", "red")
            return f"Hata: '{name}' adında bir araç yok. Kullanılabilir araçlar: {', '.join(tools.TOOLS)}"
        filled = ""
        if name == "write_file" and "path" not in args and args.get("content") and self.turn:
            # Bazı modeller (Gemma 4 26B, Qwen3.8 27B) uzun içerikte path'i hiç göndermiyor ve aynı çağrıyı tekrarlıyor
            t = self.turn
            t.pathless += 1
            # kullanıcının bu turda istediği dosyalar; ilk kayıttan sonra da (dosya artık varken) aynı hedef geçerli
            wanted = sorted(t.missing_files)
            if len(wanted) == 1 and t.pathless >= 2:
                args["path"] = filled = wanted[0]
                self._note(f"write_file yine path'siz geldi; kullanıcının istediği tek dosya olan {filled} dosyasına "
                           "yazılıyor.", "yellow")
            else:
                self._tool_header(name, args, ok=False)
                self._note("└ ✗ eksik argüman: path", "red")
                example = wanted[0] if len(wanted) == 1 else "dosya.py"
                return ('Hata: write_file call arrived without the "path" argument (only "content"), so nothing was '
                        f'saved. Call write_file again and put "path" FIRST, before "content": '
                        f'{{"path": "{example}", "content": "..."}}.'
                        + (f" The user asked for {', '.join(wanted)}." if wanted else ""))
        if missing := [k for k in tool.parameters.get("required", []) if k not in args]:
            self._tool_header(name, args, ok=False)
            self._note(f"└ ✗ eksik argüman: {', '.join(missing)}", "red")
            return (f"Hata: {name} için zorunlu argüman eksik: {', '.join(missing)}. Gönderilen argümanlar: "
                    f"{', '.join(args) or 'yok'}. Aracı tüm zorunlu argümanlarla tekrar çağır.")

        if name in RUN_TOOLS and (prev := self.turn.failed_commands.get(_command_key(args))) \
                and prev[0] == self.turn.changes:
            # Arada hiçbir dosya ya da komut değişmedi: aynı komut aynı hatayı verir, çalıştırmanın anlamı yok
            self._tool_header(name, args, ok=False)
            self._note("└ ✗ çalıştırılmadı: aynı komut az önce aynı durumda başarısız oldu", "yellow")
            return (f"{NOT_RERUN} this exact {'code' if name == 'run_python' else 'command'} already failed and nothing "
                    f"has changed since (no file written, no other command run), so it would fail the same way. Last "
                    f"error: {prev[1] or 'see the earlier result'}. Fix the cause first (edit the file or change the "
                    "code/command), or use a different approach.")
        self._tool_header(name, args)
        started = time.perf_counter()
        try:
            if tool.needs_approval and not self.auto and name not in self.always:
                if tool.preview:
                    self._show_preview(tool, name, args)
                verdict = self._approve(name)
                if verdict is not True:
                    self._note("└ reddedildi", "yellow")
                    return "Kullanıcı bu işlemi reddetti." + (f" Kullanıcının notu: {verdict}" if verdict else "")
                started = time.perf_counter()
            result = self._execute(tool, name, args)
        except TypeError as e:
            result = f"Hata: geçersiz argümanlar ({e})."
        except tools.ToolError as e:
            result = f"Hata: {e}"
        except Exception as e:
            result = f"Hata: {type(e).__name__}: {e}"
        self._show_result(tool, name, result, time.perf_counter() - started)
        if filled:
            result += (f'\n\nNote: your write_file call again had no "path", so it was saved to {filled}, the file the '
                       'user asked for. Always include "path" (write it first).')
        return tools.truncate(result, self._output_limit())

    def _output_limit(self) -> int:
        """Tek bir araç çıktısının modele giden üst sınırı: bağlamın en fazla yaklaşık %30'u (16k bağlamda ~15k
        karakter); daha büyüğü tek başına bağlamı doldurup sonraki adımları kesiyor."""
        limit = self._context_limit()
        return min(tools.MAX_OUTPUT, int(limit * 0.3 * CHARS_PER_TOKEN)) if limit else tools.MAX_OUTPUT

    def _approve(self, name: str) -> bool | str:
        """True: onaylandı. str: reddedildi (boş değilse kullanıcının modele notu)."""
        _, color, _ = self.piece()
        try:
            ans = console.input(Text.assemble(
                ("  ? ", f"bold {color}"), ("Onaylıyor musun?  ", "bold"), ("e", "bold green"), (" evet · ", MUTED),
                ("t", "bold green"), (" bu oturumda hep · ", MUTED), ("h", "bold red"),
                (" hayır · ya da modele ne yapmasını istediğini yaz\n  › ", MUTED))).strip()
        except EOFError:
            return ""
        if ans.lower() in ("e", "evet", "y", "yes"):
            return True
        if ans.lower() in ("t", "tümü", "tumu"):
            self.always.add(name)
            return True
        return "" if ans.lower() in ("", "h", "hayır", "hayir", "n", "no") else ans

    def _close_pending(self) -> None:
        """İptal edilen turda cevapsız kalan araç çağrılarını kapatır; yoksa sunucu sonraki isteği reddedebilir."""
        for i in range(len(self.messages) - 1, -1, -1):
            msg = self.messages[i]
            if msg["role"] == "assistant":
                answered = {m.get("tool_call_id") for m in self.messages[i + 1 :]}
                for call in msg.get("tool_calls") or []:
                    if call["id"] not in answered:
                        self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": "Kullanıcı iptal etti."})
                return

    # --- komutlar ---

    def command(self, line: str) -> bool:
        """Slash komutunu çalıştırır; çıkılacaksa False döner."""
        cmd, _, arg = line.partition(" ")
        arg = arg.strip()
        match cmd:
            case "/exit" | "/quit" | "/q":
                return False
            case "/help":
                table = Table(show_header=False, box=None, padding=(0, 2))
                for c, desc in COMMANDS.items():
                    table.add_row(Text(c, style=f"bold {self.piece()[1]}"), desc)
                console.print(table)
                self._note("Alt+Enter: yeni satır · Ctrl+C: cevabı durdurur · ↑/↓: önceki mesajlar")
            case "/clear":
                self.reset()
                self._note("Yeni sohbet başladı.")
            case "/undo":
                done = tools.undo_last()
                if done:
                    self.pending_note = f"(Not: kullanıcı /undo ile senin son dosya değişikliğini geri aldı: {done})"
                self._note(done or "Geri alınacak dosya değişikliği yok.")
            case "/compact":
                if not self._compact_if_needed(force=True):
                    self._note("Kısaltılacak eski araç çıktısı yok.")
            case "/tools":
                self.use_tools = not self.use_tools
                self.messages[0]["content"] = self.system_prompt()
                self._note(f"Araçlar {'açık' if self.use_tools else 'kapalı'}.")
            case "/think" | "/effort":
                self.set_effort(arg)
            case "/show":
                self.show_thinking = not self.show_thinking
                self._note(f"Düşünme metni {'gösteriliyor' if self.show_thinking else 'gizli'}.")
            case "/auto":
                self.auto = not self.auto
                if self.auto:
                    self._note("Onay sorulmayacak: model doğrudan dosya yazıp komut çalıştırabilir.", "yellow")
                else:
                    self._note("Onay yeniden soruluyor.")
            case "/model" | "/models":
                models = all_models(self.base_url)
                if arg:
                    if self.set_model(arg, models):
                        self._note(f"Model: {self.name()}")
                else:
                    self.show_models(models)
            case "/load":
                self.load_preset(arg)
            case "/fit":
                self.fit(arg)
            case "/vision" | "/görsel":
                self.toggle_vision(arg)
            case "/image" | "/resim":
                self.add_image(arg)
            case "/unload":
                stopped = servers.stop_all()
                if self._lms("unload", "--all"):
                    self.model, self.ctx = None, None
                    if stopped:
                        self._note(f"Sunucu kapatıldı: {', '.join(stopped)}")
            case _:
                console.print(f"[red]Bilinmeyen komut: {escape(cmd)}[/] [dim](/help)[/]")
        return True

    def _catalog(self) -> list[dict] | None:
        """Diskteki modeller (yalnızca yerel LM Studio için) ve hazır ayarların onlarla yeniden eşleştirilmesi."""
        cat = lmstudio.catalog(self.cfg) if is_local(self.base_url) else None
        lmstudio.resolve_presets(self.cfg, cat)
        return cat

    def _missing_note(self, name: str, p: dict) -> None:
        progress = lmstudio.download_progress(p)
        if progress is not None:
            pct = f" (%{progress * 100:.0f})" if progress >= 0 else ""
            console.print(f"[yellow]{escape(name)}: modeli LM Studio'da hâlâ iniyor{pct}; inince kullanılabilir.[/]")
            return
        console.print(f"[red]{escape(name)}: model diskte yok (silinmiş ya da hiç indirilmemiş).[/]")
        self._note(f"İndirmek için: {lmstudio.download_hint(p)}")

    @staticmethod
    def _disk_info(m: dict | None) -> str:
        if not m:
            return ""
        quant = (m.get("quantization") or {}).get("name", "")
        return f"{m.get('sizeBytes', 0) / 1e9:.1f} GB" + (f" {quant}" if quant else "")

    def show_models(self, models: list[dict] | None) -> None:
        if models is None:
            console.print("[red]Sunucuya ulaşılamadı.[/]")
            return
        cat = self._catalog()
        info = {m["id"]: m for m in models}
        presets = self.cfg.get("presets", {})
        missing = {a for a, p in presets.items() if cat is not None and not lmstudio.is_empty_slot(p)
                   and p.get("_disk") is None and p.get("model") not in info}
        table = Table(box=None, padding=(0, 2))
        for col in ("", "Model", "Durum", "Bağlam", "Dosya", ""):
            table.add_column(col)
        for alias, p in presets.items():
            if alias in missing:
                continue
            v = lmstudio.vision_of(p)
            vm = info.get(v["model"], {}) if v else {}
            sm = info.get(servers.alias(alias), {})
            m = vm if vm.get("state") == "loaded" else sm or info.get(p.get("model"), {})
            loaded = m.get("state") == "loaded"
            glyph, color, _ = PIECES.get(alias, DEFAULT_PIECE)
            state = ("[dim]boş yuva[/]" if lmstudio.is_empty_slot(p) else
                     ("[green]yüklü · görsel[/]" if m is vm else
                      f"[green]yüklü · {escape(m.get('_engine') or 'sunucu')}[/]" if m is sm else "[green]yüklü[/]") if loaded
                     else "[dim]yüklü değil[/]" if m or p.get("_disk") else "[red]bulunamadı[/]")
            table.add_row(
                "→" if self.model and self.model in (p.get("model"), v and v.get("model"), servers.alias(alias)) else "",
                Text(f"{glyph} {alias}", style=f"bold {color}"), state,
                str(m.get("loaded_context_length") or "") if loaded else "",
                f"[dim]{self._disk_info(p.get('_disk'))}{' · görsel var' if v else ''}[/]",
                f"[dim]{escape(p.get('desc', ''))}[/]",
            )
        console.print(table)
        if missing:
            console.print(Text("\n  Diskte yok", style="bold"))
            gone = Table(box=None, padding=(0, 2), show_header=False)
            for alias in presets:
                if alias not in missing:
                    continue
                p = presets[alias]
                glyph, color, _ = PIECES.get(alias, DEFAULT_PIECE)
                progress = lmstudio.download_progress(p)
                state = ("[red]silinmiş ya da indirilmemiş[/]" if progress is None
                         else f"[yellow]iniyor{f' %{progress * 100:.0f}' if progress >= 0 else ''}[/]")
                gone.add_row("", Text(f"{glyph} {alias}", style=f"bold {color}"), state,
                             f"[dim]{escape(p.get('file') or p.get('model', ''))}"
                             + (f" ({p['size_gb']} GB)" if p.get("size_gb") else "") + "[/]")
            console.print(gone)
            self._note("İndirme komutunu görmek için: /load <ad> (depo ve dosya adları config.json'da)")
        extra = lmstudio.unassigned(self.cfg, cat)
        if extra:
            console.print(Text("\n  Ayarı olmayan modeller", style="bold"))
            free = Table(box=None, padding=(0, 2), show_header=False)
            for m in extra:
                free.add_row("", m.get("modelKey", ""), f"[dim]{self._disk_info(m)}[/]",
                             f"[dim]/fit {escape(m.get('modelKey', ''))} ile ayar önerisi al[/]")
            console.print(free)
        self._note("/load <ad> ile yükle · /model <ad> ile yüklü olana geç · /fit <ad> belleğe sığar mı")

    def _load_on_server(self, name: str, p: dict) -> None:
        """Hazır ayarı Gambit'in başlattığı sunucuda (ik_llama.cpp) yükler: önce LM Studio modellerini boşaltır."""
        glyph, color, _ = PIECES.get(name, DEFAULT_PIECE)
        engine = p["server"].get("engine") or "llama-server"
        spinner = Spinner(glyph, color, self.animate)
        label = f"{name} yükleniyor ({engine})"
        spinner.set(label, "LM Studio modelleri boşaltılıyor")
        with Live(spinner, console=console, refresh_per_second=12.5, transient=True):
            lmstudio.unload_all(self.cfg)
            self.model, self.ctx = None, None
            spinner.set(label, "")
            res = servers.start(self.cfg, name, p, on_tick=lambda avail: spinner.set(
                label, f"boş RAM {lmstudio.gib(avail)}" if avail is not None else ""))
        if not res.ok:
            style = "bold red" if res.guard_tripped else "red"
            console.print(f"[{style}]{escape(name)} yüklenemedi: {escape(res.message)}[/]")
            return
        if self.set_model(name, all_models(self.base_url) or servers.running()):
            console.print(Text.assemble(("  ✓ ", "green"), (f"{glyph} {name}", f"bold {color}"), " hazır",
                                        (f" · bağlam {self.ctx}" if self.ctx else "", MUTED),
                                        (f" · {res.message}", MUTED)))

    def toggle_vision(self, arg: str) -> None:
        """/vision [aç|kapat]: görsel modu değiştirir ve modeli o moddaki ayarıyla yeniden yükler."""
        want = {"on": True, "aç": True, "ac": True, "açık": True, "off": False, "kapat": False, "kapalı": False}
        target = want.get(arg.lower(), not self.vision) if arg else not self.vision
        name = self.name()
        p = self.cfg.get("presets", {}).get(name)
        if target and p and not lmstudio.vision_of(p):
            console.print(f"[yellow]{escape(name)} modelinin görsel eki yok (diskte mmproj dosyası bulunmuyor).[/]")
            return
        self.vision = target
        if not target:
            self.pending_images = []
        if not p:
            self._note(f"Görsel mod {'açık' if target else 'kapalı'}; /load <ad> ile yükle.")
            return
        self.load_preset(name)

    def add_image(self, arg: str) -> None:
        """/image <dosya>: resmi sonraki mesaja ekler; dosya verilmezse eklenenleri siler."""
        if not arg:
            self._note(f"{len(self.pending_images)} resim kaldırıldı." if self.pending_images else
                       "Kullanım: /image <dosya> (png, jpg, webp, gif, bmp)")
            self.pending_images = []
            return
        if not self.vision:
            console.print("[yellow]Görsel mod kapalı; önce /vision ile aç (model görsel ekiyle yeniden yüklenir).[/]")
            return
        try:
            part = image_part(arg.strip().strip("'\""))
        except ValueError as e:
            console.print(f"[red]{escape(str(e))}[/]")
            return
        self.pending_images.append(part)
        self._note(f"Resim eklendi: {part['_name']} · sonraki mesajla gönderilecek ({len(self.pending_images)} resim)")

    def load_preset(self, name: str) -> None:
        presets = self.cfg.get("presets", {})
        if name not in presets:
            if name:
                console.print(f"[red]'{escape(name)}' adında hazır ayar yok.[/]")
            table = Table(show_header=False, box=None, padding=(0, 2))
            for key, p in presets.items():
                table.add_row(Text(f"/load {key}", style=f"bold {PIECES.get(key, DEFAULT_PIECE)[1]}"),
                              f"[dim]{escape(p.get('desc', ''))}[/]")
            console.print(table)
            return
        p = presets[name]
        if lmstudio.is_empty_slot(p):
            console.print(f"[yellow]{escape(name)} boş bir yuva; önce config.json'da ona bir model ata.[/]")
            return
        if is_local(self.base_url) and self._catalog() is not None and p.get("_disk") is None:
            self._missing_note(name, p)  # diğer modelleri boşaltmadan önce: yüklenemeyecek model için onlar gitmesin
            return
        v = lmstudio.vision_of(p)
        if self.vision and not v:
            self._note(f"{name} modelinin görsel eki yok; metin modunda yükleniyor.", "yellow")
            self.vision = False
        if not self.vision and p.get("server") and servers.binary(p):
            self._load_on_server(name, p)
            return
        if p.get("server") and not self.vision:
            self._note(f"Sunucu programı bulunamadı ({p['server'].get('bin')}); LM Studio ile yükleniyor.", "yellow")
        key = v["model"] if self.vision else p["model"]
        glyph, color, _ = PIECES.get(name, DEFAULT_PIECE)
        args = lmstudio.preset_args(p, vision=self.vision)
        # Gerçek yüklemeyle ölçülmüş ayar (tune_gpu --fit --apply) ya da ayarı sanal modelde olan taş: LM Studio'nun
        # tahmini görsel ekinin kapatıldığını ve uzman bölmesini bilmediği için onu aşıyor; tahmin denetimi atlanır
        measured = (v if self.vision else p).get("measured") or p.get("fit") is False
        spinner = Spinner(glyph, color, self.animate)
        spinner.set(f"{name} hazırlanıyor", "diğer modeller boşaltılıyor")
        with Live(spinner, console=console, refresh_per_second=12.5, transient=True):
            servers.stop_all()  # VRAM'i Gambit'in başlattığı sunucu tutmasın
            lmstudio.unload_all(self.cfg)
            self.model, self.ctx = None, None
            spinner.set(f"{name} hazırlanıyor", "bellek tahmini")
            vram_budget, ram_budget, _ = lmstudio.budgets(self.cfg)
            est = None if measured else lmstudio.estimate(self.cfg, key, args)
            problems = lmstudio.fit_problems(est, vram_budget, ram_budget) if est else []
            if problems:
                spinner.set(f"{name} hazırlanıyor", "sığan ayar aranıyor")
                advice = lmstudio.advise(self.cfg, key, args, vram_budget, ram_budget)
        if measured:
            self._note(f"Ölçülmüş ayar: --gpu {lmstudio.get_arg(args, ('--gpu',), '?')}"
                       + (f" ({measured})" if isinstance(measured, str) else " (sanal modelde)"))
        if est:
            self._note(f"Tahmin: GPU {lmstudio.gib(est.gpu)} · RAM {lmstudio.gib(est.ram)}"
                       + (f" · ayrılabilecek VRAM {lmstudio.gib(vram_budget)}" if vram_budget is not None else "")
                       + (f", RAM {lmstudio.gib(ram_budget)}" if ram_budget is not None else ""))
        if problems:
            for problem in problems:
                console.print(f"  [yellow]! {escape(problem)}[/]")
            args = self._choose_fit(args, advice)
            if args is None:
                self._note("Yükleme iptal edildi.")
                return
        label = f"{name} yükleniyor" + (" (görsel)" if self.vision else "")
        spinner.set(label, "")
        with Live(spinner, console=console, refresh_per_second=12.5, transient=True):
            res = lmstudio.guarded_load(self.cfg, key, args, on_tick=lambda avail: spinner.set(
                label, f"boş RAM {lmstudio.gib(avail)}" if avail is not None else ""))
        if not res.ok:
            style = "bold red" if res.guard_tripped else "red"
            console.print(f"[{style}]{escape(name)} yüklenemedi: {escape(res.message)}[/]")
            if res.guard_tripped:
                self._note(f"Daha az bellek için: /fit {name} (GPU oranı ve bağlam önerisi)")
            return
        models = server_models(self.base_url) or []
        if self.set_model(name, models):
            console.print(Text.assemble(("  ✓ ", "green"), (f"{glyph} {name}", f"bold {color}"),
                                        " hazır" + (" · görsel mod" if self.vision else ""),
                                        (f" · bağlam {self.ctx}" if self.ctx else "", MUTED),
                                        (f" · {res.message}" if res.message else "", MUTED)))

    def _choose_fit(self, args: list[str], advice: "lmstudio.Advice | None") -> list[str] | None:
        """Tahmin belleğe sığmıyorsa ne yapılacağını sorar: önerilen ayar, yine de bu ayar ya da vazgeç."""
        better = None
        if advice and advice.fits:
            better = lmstudio.set_arg(args, ("--gpu",), advice.gpu)
            if advice.context.isdigit():
                better = lmstudio.set_arg(better, lmstudio.CONTEXT_FLAGS, advice.context)
            ctx_note = (f", bağlam {advice.context}" if advice.context != lmstudio.get_arg(args, lmstudio.CONTEXT_FLAGS)
                        else "")
            self._note(f"Öneri: --gpu {advice.gpu}{ctx_note} → GPU {lmstudio.gib(advice.est.gpu)} · "
                       f"RAM {lmstudio.gib(advice.est.ram)}", "cyan")
        elif advice:
            self._note("Daha düşük GPU oranı ve 8k bağlamla da sığmıyor; açık uygulamaları kapatmak yer açar.", "yellow")
        if not self.interactive:
            return better
        question = ("[Ö]neriyle yükle / [y]ine de bu ayarla / [v]azgeç " if better
                    else "Yine de yüklensin mi? RAM bekçisi açık [e/H] ")
        try:
            ans = console.input(Text.assemble(("  ? ", "bold yellow"), (question, MUTED))).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None
        if better:
            return better if ans in ("", "ö", "o", "öneri") else args if ans in ("y", "yine", "e") else None
        return args if ans in ("e", "evet", "y", "yes") else None

    def fit(self, arg: str) -> None:
        """/fit <ad|model anahtarı>: yüklemeden bellek tahmini ve bu makineye uygun ayar önerisi."""
        presets = self.cfg.get("presets", {})
        if not arg:
            console.print("[red]Kullanım: /fit <ad>, ör. /fit queen ya da /fit <model anahtarı>[/]")
            return
        cat = self._catalog()
        if cat is None:
            console.print("[red]Diskteki modeller okunamadı (lms bulunamadı ya da sunucu yerel değil).[/]")
            return
        if arg in presets and not lmstudio.is_empty_slot(presets[arg]):
            p, label = presets[arg], arg
            if p.get("_disk") is None:
                self._missing_note(arg, p)
                return
            disk, args = p["_disk"], lmstudio.preset_args(p)
        else:
            disk = lmstudio.find_on_disk(arg, arg, cat)
            if not disk:
                console.print(f"[red]'{escape(arg)}' ne bir hazır ayar ne de diskteki bir model.[/] [dim](/model)[/]")
                return
            label, args = disk["modelKey"], lmstudio.preset_args({"context": 16384, "gpu": "max"})
        key = disk["modelKey"]
        glyph, color, _ = PIECES.get(label, DEFAULT_PIECE)
        spinner = Spinner(glyph, color, self.animate)
        spinner.set(f"{label} hesaplanıyor", "bellek tahmini")
        with Live(spinner, console=console, refresh_per_second=12.5, transient=True):
            vram_budget, ram_budget, source = lmstudio.budgets(self.cfg)
            est = lmstudio.estimate(self.cfg, key, args)
            advice = lmstudio.advise(self.cfg, key, args, vram_budget, ram_budget) if est else None
        if not est:
            console.print("[red]LM Studio bellek tahmini alınamadı (lms load --estimate-only).[/]")
            return
        loaded = [m for m in all_models(self.base_url) or [] if m.get("state") == "loaded"]
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row(Text(f"{glyph} {label}", style=f"bold {color}"), f"[dim]{escape(self._disk_info(disk))}[/]")
        table.add_row("Bu ayar", f"--gpu {lmstudio.get_arg(args, ('--gpu',), 'otomatik')} · bağlam "
                                 f"{lmstudio.get_arg(args, lmstudio.CONTEXT_FLAGS, 'varsayılan')}")
        problems = lmstudio.fit_problems(est, vram_budget, ram_budget)
        table.add_row("Tahmin", f"GPU {lmstudio.gib(est.gpu)} · RAM {lmstudio.gib(est.ram)}  "
                                + ("[yellow]sığmıyor[/]" if problems else "[green]sığıyor[/]"))
        table.add_row("Ayrılabilecek",
                      (f"VRAM {lmstudio.gib(vram_budget)} [dim]({source})[/]" if vram_budget is not None
                       else "VRAM [yellow]ölçülemedi[/] [dim](nvidia-smi çalışmıyor; config'e vram_limit_gb yaz)[/]")
                      + (f" · RAM {lmstudio.gib(ram_budget)}" if ram_budget is not None else ""))
        if advice:
            table.add_row("Öneri", f"--gpu {advice.gpu} · bağlam {advice.context} → GPU {lmstudio.gib(advice.est.gpu)} "
                                   f"· RAM {lmstudio.gib(advice.est.ram)}  "
                                   + ("[green]sığıyor[/]" if advice.fits else "[yellow]yine de sığmıyor[/]"))
        console.print(table)
        if loaded:
            self._note("Şu an yüklü model var; boşaltılınca (/unload) daha fazla yer açılır, öneri buna göre değişir.")
        if label not in presets and advice:
            snippet = {"model": key, "file": Path(str(disk.get("path", ""))).name,
                       "quant": (disk.get("quantization") or {}).get("name", ""),
                       "size_gb": round(disk.get("sizeBytes", 0) / 1e9, 2),
                       "context": int(advice.context) if advice.context.isdigit() else 16384,
                       "gpu": float(advice.gpu) if advice.gpu[0].isdigit() else advice.gpu, "desc": ""}
            self._note("config.json'a hazır ayar olarak eklemek için (\"presets\" içine, bir taş adıyla):")
            console.print(Syntax(json.dumps(snippet, ensure_ascii=False, indent=2), "json", theme="ansi_dark",
                                 background_color="default"))

    def _lms(self, *args: str) -> bool:
        """lms'i çalıştırır; çıktısı (model kimlikleri içerir) ekrana basılmaz."""
        r = lmstudio.run(self.cfg, *args)
        if r.returncode != 0:
            console.print(f"[red]LM Studio işlemi başarısız oldu ({escape(args[0])}): "
                          f"{escape((r.stderr or r.stdout).strip()[-200:])}[/]")
        return r.returncode == 0

    def _think_state(self) -> str:
        if self.efforts == ["off"]:
            return "yok"
        return self._effort_label(self.effort)

    def _tools_state(self) -> str:
        if self.use_tools and not self.tools_on():
            return "yok"
        return "açık" if self.use_tools else "kapalı"

    def toolbar(self) -> FormattedText:
        glyph, color, _ = self.piece()
        parts = [f"düşünme {self._think_state()}", f"araçlar {self._tools_state()}"]
        if self.vision:
            parts.append("görsel açık" + (f" · {len(self.pending_images)} resim" if self.pending_images else ""))
        parts.append(f"onay {'otomatik' if self.auto else 'sorulur'}")
        limit = self._context_limit()
        if limit and self.last_tokens is not None:
            parts.append(f"bağlam {_bar(self.last_tokens / limit, 8)} %{self.last_tokens * 100 // limit}")
        parts.append("/help")
        return FormattedText([(f"bg:{color} #000000 bold", f" {glyph} {self.name()} "), ("", "  " + " · ".join(parts))])

    def prompt_message(self) -> FormattedText:
        glyph, color, _ = self.piece()
        return FormattedText([(f"fg:{color} bold", f"{glyph} "), (f"fg:{MUTED}", "› ")])


# --- açılış ---

def _logo_frame(color: str, color2: str, reveal: float) -> Text:
    """Degrade renkli logo; reveal (0-1) kadarı görünür, görünen kısmın ucunda parlak bir kenar olur."""
    width = max(len(row) for row in LOGO)
    edge = reveal * (width + 6)
    text = Text()
    for r, row in enumerate(LOGO):
        text.append("\n  " if r else "  ")
        for c, ch in enumerate(row):
            if ch == " " or c > edge:
                text.append(" ")
                continue
            base = _mix(color, color2, (c + r * 2) / (width + 8))
            glow = max(0.0, 1 - (edge - c) / 6) if reveal < 1 else 0.0
            text.append(ch, style=_mix(base, "#ffffff", glow * 0.7))
    return text


def banner(chat: Chat) -> None:
    glyph, color, color2 = chat.piece()
    animate = chat.animate and chat.fancy()
    if console.width >= max(len(row) for row in LOGO) + 4:
        if animate:
            with Live(_logo_frame(color, color2, 0), console=console, refresh_per_second=60, transient=False) as live:
                for f in range(1, 19):
                    live.update(_logo_frame(color, color2, f / 18), refresh=True)
                    time.sleep(0.022)
                live.update(_logo_frame(color, color2, 1.0), refresh=True)
        else:
            console.print(_logo_frame(color, color2, 1.0))
    else:
        console.print(Text(f"  {glyph} GAMBIT", style=f"bold {color}"))
    name = chat.name() if chat.model else "model yok · /load queen ile yükle"
    info = Text.assemble(("  ", ""), (f"{glyph} {name}", f"bold {color}"))
    parts = ([f"bağlam {chat.ctx // 1024}k"] if chat.ctx else []) + [
        f"düşünme {chat._think_state()}", f"araçlar {chat._tools_state()}"] + (["görsel açık"] if chat.vision else [])
    for part in parts:
        info.append(f"  ·  {part}", style=MUTED)
    console.print(info)
    console.print(Text(f"  {os.getcwd()}", style=MUTED))
    console.print(Text("  /help komutlar · /undo son dosya değişikliğini geri alır · Alt+Enter yeni satır · "
                       "Ctrl+C durdurur", style=MUTED))
    console.print()


def repl(chat: Chat) -> None:
    keys = KeyBindings()

    @keys.add("escape", "enter")
    def _newline(event):
        event.current_buffer.insert_text("\n")

    session = PromptSession(
        history=FileHistory(str(HISTORY_FILE)), key_bindings=keys,
        completer=WordCompleter(list(COMMANDS), sentence=True), bottom_toolbar=chat.toolbar,
        style=Style.from_dict({"bottom-toolbar": "noreverse bg:#262626 #bcbcbc"}),
    )
    chat.interactive = True
    while True:
        try:
            text = session.prompt(chat.prompt_message).strip()
        except KeyboardInterrupt:
            continue
        except EOFError:
            return
        if not text:
            continue
        try:
            if text.startswith("/"):
                if not chat.command(text):
                    return
            elif not chat.model:
                console.print("[red]Kullanılacak model yok.[/] Önce bir model yükle, ör. /load queen")
            else:
                chat.ask(text)
        except KeyboardInterrupt:
            console.print("\n[yellow]Durduruldu.[/]")
        console.print()


def main() -> int:
    ap = argparse.ArgumentParser(prog="gambit", description="Gambit CLI: yerel modellerle terminal asistanı.")
    ap.add_argument("prompt", nargs="*", help="tek seferlik soru; verilmezse sohbet modu açılır")
    ap.add_argument("-m", "--model", help="kullanılacak model: bishop, rook, queen, king "
                                          "(varsayılan: LM Studio'da yüklü olan)")
    ap.add_argument("--url", help="sunucu adresi (varsayılan: config.json'daki base_url)")
    ap.add_argument("--no-tools", action="store_true", help="araçları kapat, sadece sohbet")
    ap.add_argument("--think", action=argparse.BooleanOptionalAction, default=None,
                    help="düşünmeyi aç/kapat (varsayılan: config.json'daki effort)")
    ap.add_argument("--effort", metavar="DÜZEY",
                    help="düşünme düzeyi: off, on, low, medium, high, xhigh (modelde olmayan düzeyin en yakını seçilir)")
    ap.add_argument("--show-think", action="store_true", help="düşünme metnini ekranda göster")
    ap.add_argument("--vision", action="store_true",
                    help="görsel mod: modelin görsel ekli hâlini kullan (yüklemek için sohbette /load ya da /vision)")
    ap.add_argument("--image", action="append", metavar="DOSYA",
                    help="tek seferlik soruya resim ekle (birden fazla verilebilir; görsel modu açar)")
    ap.add_argument("--no-anim", action="store_true", help="animasyonları kapat")
    ap.add_argument("-y", "--yes", action="store_true", help="dosya yazma/komut onayı sorma (dikkat!)")
    args = ap.parse_args()

    cfg = load_config()
    base_url = args.url or cfg["base_url"]
    client = OpenAI(base_url=base_url, api_key=cfg.get("api_key") or "lm-studio", timeout=3600, max_retries=0)
    chat = Chat(client, cfg, base_url, args)

    models = ensure_server(cfg, base_url)
    if models is not None:
        models += servers.running()
    if models is None:
        console.print(f"[red]Sunucuya ulaşılamadı: {escape(base_url)}[/]\nLM Studio'yu aç ya da şunu çalıştır: lms server start")
        return 1
    wanted = args.model or cfg.get("model")
    if wanted:
        chat.set_model(wanted, models)
        if args.model and chat.model and chat.model.startswith("gambit-") and not chat.on_server():
            chat.load_preset(chat.name())  # -m ile istenen model Gambit'in sunucusunda: kendi ayarıyla başlatılır
    else:
        # yüklü modellerden araç kullanabilenler önce
        loaded = sorted((m for m in models if m.get("state") == "loaded"),
                        key=lambda m: "tool_use" not in m.get("capabilities", []))
        if loaded:
            chat.set_model(loaded[0]["id"], models)

    for path in args.image or []:
        try:
            chat.pending_images.append(image_part(path))
        except ValueError as e:
            console.print(f"[red]{escape(str(e))}[/]")
            return 1
    if args.prompt:
        if not chat.model:
            console.print("[red]Yüklü model yok.[/] Önce CLI'da /load queen ile bir model yükle ya da -m ile belirt.")
            return 1
        chat.ask(" ".join(args.prompt))
        return 0

    banner(chat)
    repl(chat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
