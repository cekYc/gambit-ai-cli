"""Gambit CLI: LM Studio'daki (ya da OpenAI uyumlu herhangi bir sunucudaki) yerel modellerle terminalden
sohbet eder. Model dosya okuyup arayabilir; dosya yazma ve komut çalıştırma senin onayınla olur.
Modeller ekranda config.json'daki hazır ayar adlarıyla (knight, rook, queen, bishop, king) görünür."""

import argparse
import json
import math
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

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
    r"değiştirdim)\b|\bI(?: have|'ve)? (?:created|saved|written|wrote|ran|run|tested|verified|updated|fixed)\b", re.I)
FILE_MENTION = re.compile(
    r"(?<![\w/\\.-])[\w-][\w./\\-]*\.(?:py|js|mjs|cjs|ts|sql|ps1|sh|json|md|html|css|txt|csv|ini|ya?ml|toml)\b")
# Otomatik düşünme modunda düşünmeyi açan soru kalıpları: kodun ne yaptığını, nedenini soran analiz soruları
ANALYSIS_QUESTION = re.compile(
    r"\bne (?:yazdır|döndür|yap|üret|çıkar)|çıktı(?:s[ıi])? ne|\bneden\b|\bniçin\b|\bniye\b|açıkla|analiz|"
    r"karşılaştır|nasıl çalış|hangisi daha|ne olur\b|ne fark|\bwhy\b|\bexplain\b|what does|what is the output|\bcompare\b",
    re.I)
# Dosya yazdıran/değiştirten istekler: bunlarda düşünme yalnızca planlama adımında ve bir şey ters gidince açılır
ACTION_REQUEST = re.compile(r"\b(?:yaz(?!dır)|oluştur|kaydet|düzelt|düzenle|güncelle|ekle|değiştir|uygula|write|create|"
                            r"fix|implement|add|update|refactor|rename)\w*", re.I)
PY_INLINE = re.compile(r"\bpy(?:thon\d*)?(?:\.exe)?\s+(?:-\S+\s+)*-c\b", re.I)
NOT_FOUND = re.compile(r"['‘]([^'’\n]+)['’] (?:terimi bir cmdlet|is not recognized as)|(?:^|\s)([\w.-]+): (?:command )?not found",
                       re.M)
SQLITE_DOT = re.compile(r"""execute\w*\(\s*[rRbBuU]?(?:'{1,3}|"{1,3})\s*\.(?:schema|tables|headers|mode|indexes)\b""")
RUN_TOOLS = ("run_command", "run_python")
COMPACT_MARK = "[… Gambit: bağlam için kısaltıldı"
CHARS_PER_TOKEN = 3.2

# Her modelin taşı ve renkleri (arayüzde vurgu ve degrade için); orta tonlar açık ve koyu terminalde okunur
PIECES = {"knight": ("♞", "#00afd7", "#5f5fd7"), "rook": ("♜", "#d78700", "#d75f5f"),
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
    "/model": "Modelleri listeler; /model <ad> ile yüklü olana geçer",
    "/load": "Modeli kendi ayarlarıyla yükler, ör. /load queen (diğer modelleri boşaltır)",
    "/unload": "Yüklü tüm modelleri boşaltır",
    "/clear": "Yeni sohbet başlatır",
    "/undo": "Modelin yaptığı son dosya değişikliğini geri alır",
    "/compact": "Eski araç çıktılarını kısaltıp bağlamda yer açar",
    "/tools": "Araçları açar/kapatır",
    "/think": "Düşünmeyi açar/kapatır; /think on, off ya da auto (otomatik)",
    "/show": "Düşünme metnini ekranda gösterir/gizler",
    "/auto": "Onay sormayı açar/kapatır (dikkatli kullan)",
    "/exit": "Çıkış (Ctrl+D de olur)",
}


def load_config() -> dict:
    with open(HERE / "config.json", encoding="utf-8") as f:
        return json.load(f)


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


def lms_path(cfg: dict) -> str | None:
    configured = Path(os.path.expanduser(cfg.get("lms_path") or ""))
    return str(configured) if cfg.get("lms_path") and configured.is_file() else shutil.which("lms")


def ensure_server(cfg: dict, base_url: str) -> list[dict] | None:
    models = server_models(base_url)
    if models is None and ("localhost" in base_url or "127.0.0.1" in base_url) and lms_path(cfg):
        with console.status(Text("LM Studio sunucusu kapalı, başlatılıyor…", style=MUTED), spinner="dots"):
            subprocess.run([lms_path(cfg), "server", "start"], capture_output=True)
            models = server_models(base_url)
    return models


def analysis_question(text: str) -> bool:
    """Otomatik düşünme modunda bu mesaj düşünerek cevaplanmalı mı (kodun ne yaptığı, neden, açıklama...)."""
    return bool(ANALYSIS_QUESTION.search(text))


def command_failed(result: str) -> bool:
    """run_command/run_python sonucu başarısız mı (sıfır olmayan çıkış kodu, stderr'de PowerShell hatası, araç hatası)."""
    first = result.split("\n", 1)[0]
    m = re.match(r"çıkış kodu: (-?\d+)", first)
    return bool(m and m.group(1) != "0") or tools.STDERR_WARNING in first or result.startswith("Hata:")


def _partial_tail(s: str, tag: str) -> int:
    """s'nin sonu tag'in başıyla kaç karakter örtüşüyor (etiketin yarısı gelmiş olabilir)."""
    for k in range(min(len(tag) - 1, len(s)), 0, -1):
        if s.endswith(tag[:k]):
            return k
    return 0


def alias_of(cfg: dict, model: str | None) -> str:
    """Ekranda gösterilecek ad: modelin hazır ayar adı (knight, queen...). Model kimlikleri gösterilmez."""
    if not model:
        return "model yok"
    return next((k for k, p in cfg.get("presets", {}).items() if p["model"] == model), "tanımsız model")


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
        total += len(m.get("content") or "") + 8
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
    nudges: int = 0
    broken_retries: int = 0
    empty_retry: bool = False
    think_all: bool = False  # bu tur her adımda düşün (otomatik mod, analiz sorusu)
    think_rest: bool = False  # boş cevaptan sonra turun geri kalanında düşün
    think_next: int = 0  # sonraki şu kadar adımda düşün
    no_think_next: bool = False  # düşünme bütçesi aşıldı: sonraki adım düşünmeden
    force_compact: bool = False
    failed_commands: set = field(default_factory=set)
    last_error: str = ""
    same_error: int = 0


class Chat:
    def __init__(self, client: OpenAI, cfg: dict, base_url: str, args: argparse.Namespace):
        self.client = client
        self.cfg = cfg
        self.base_url = base_url
        self.model: str | None = None
        self.ctx: int | None = None  # modelin yüklü bağlam uzunluğu
        self.use_tools = not args.no_tools
        if getattr(args, "auto_think", False):
            mode = "auto"
        elif args.think is not None:
            mode = "on" if args.think else "off"
        else:
            mode = {True: "on", False: "off"}.get(cfg.get("thinking", True), str(cfg.get("thinking")))
        self.set_think_mode(mode if mode in ("on", "off", "auto") else "on")
        self.escalations = 0  # otomatik modda doğrulama başarısız olduğu için düşünmenin açıldığı adım sayısı
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
        if self.use_tools:
            have, missing = self.env
            shell = tools.SHELL_NAME
            lines += [
                f"You have tools to list, read, search, create and edit files, to run shell commands ({shell}) and "
                "to run Python code.",
                "Use them whenever you need real information; never invent file contents or command output.",
                "Relative paths are relative to the current directory.",
                f"Installed programs: {', '.join(have) or 'none'}." + (f" Not installed: {', '.join(missing)}."
                                                                       if missing else ""),
                (f"run_command uses {shell}: write PowerShell syntax, not bash. For any Python code (tests, data "
                 "processing, SQLite queries) use run_python instead of python -c, which breaks on PowerShell quoting."
                 if tools.POWERSHELL else "For any Python code use run_python instead of python -c."),
                "Read a file before editing it. Use edit_file for small changes, write_file for new files or full rewrites.",
                "When the user asks you to write or create a program, script or file, save it with write_file; do not "
                "paste the whole file into the chat instead. If they also ask you to run it, run it.",
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
        if len(aliases) == 1:
            model = presets[aliases[0]]["model"]
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
        if info and info.get("state") != "loaded":
            console.print("[yellow]Bu model yüklü değil; ilk mesajda LM Studio varsayılan ayarlarla yükler. "
                          f"Kendi ayarlarıyla yüklemek için: /load {alias_of(self.cfg, model)}[/]")
        return True

    def name(self) -> str:
        return alias_of(self.cfg, self.model)

    def piece(self) -> tuple[str, str, str]:
        return PIECES.get(self.name(), DEFAULT_PIECE)

    def fancy(self) -> bool:
        """Canlı alan, animasyon ve Markdown biçimi: yalnızca gerçek bir terminalde."""
        return console.is_terminal

    def can_think(self) -> bool:
        """Model düşünme modunu destekliyor mu (hazır ayarda "thinking": false ise hayır)."""
        preset = self.cfg.get("presets", {}).get(self.name(), {})
        return preset.get("thinking", True)

    def _note(self, text: str, style: str = MUTED) -> None:
        console.print(Text(f"  {text}", style=style))

    # --- sohbet / ajan döngüsü ---

    def set_think_mode(self, mode: str) -> None:
        """on / off / auto. auto: varsayılan kapalı; analiz sorularında ya da bir komut başarısız olunca açılır."""
        self.think_mode = mode
        self.thinking = mode == "on"

    def ask(self, text: str) -> None:
        if self.pending_note:
            text, self.pending_note = f"{self.pending_note}\n\n{text}", ""
        start = len(self.messages)
        self.messages.append({"role": "user", "content": text})
        turn = self.turn = Turn(text, missing_files={m for m in FILE_MENTION.findall(text) if not Path(m).exists()})
        if self.think_mode == "auto" and self.can_think() and analysis_question(text):
            if ACTION_REQUEST.search(text):
                turn.think_next = 1
                self._note("Analiz gerektiren bir görev: planlama adımında düşünme açık.")
            else:
                turn.think_all = True
                self._note("Analiz sorusu: bu tur düşünme açık.")
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
                    self._note(f"Düşünme {self._think_budget()} token sınırını aştı; bu adım düşünmeden tekrarlanıyor.",
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
            self.thinking = self.think_mode == "on"  # turda geçici açılan düşünmeyi geri al

    def _choose_thinking(self) -> None:
        """Bu adımda düşünülsün mü: moda, analiz sorusuna ve son adımda ne olduğuna göre."""
        t = self.turn
        if t.no_think_next:
            self.thinking, t.no_think_next = False, False
            return
        base = {"on": True, "off": False}.get(self.think_mode, t.think_all)
        self.thinking = base or t.think_rest or t.think_next > 0
        if t.think_next:
            t.think_next -= 1

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
        if t.nudges >= 2:
            return False
        reason = None
        if self.last_finish == "length":
            reason = ("Cevap uzunluk sınırında kesildi; devam etmesi isteniyor.",
                      "Your last message was cut off by the output length limit. Continue exactly where it stopped, "
                      "without repeating. If you were writing a file, write it with write_file in smaller parts.")
        elif not self.use_tools:
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
        elif t.writes == 0 and "```" in text and (missing := sorted(f for f in t.missing_files if not Path(f).exists())):
            reason = (f"Model kodu dosyaya kaydetmedi ({', '.join(missing)}); kaydetmesi isteniyor.",
                      f"The user asked for {', '.join(missing)}, but it was not created: the code is only in your "
                      "message. Save it with write_file, then verify it.")
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
        if name in RUN_TOOLS and not result.startswith("Kullanıcı"):
            hints += self._command_hints(name, args, result)
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
        if not command_failed(result):
            t.same_error, t.last_error = 0, ""
            return []
        if self.think_mode == "auto" and self.can_think() and not t.think_all:
            t.think_next = 1
            self.escalations += 1
            self._note("Komut başarısız oldu: sonraki adımda düşünme açık.")
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
        key = " ".join(code.split())
        if key in t.failed_commands:
            hints.append("This exact command already failed earlier in this task. Do not repeat it; change the approach.")
        t.failed_commands.add(key)
        err = _error_line(result)
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
        if self.use_tools:
            kwargs["tools"] = tools.schemas()
        if not self.thinking and self.can_think():
            kwargs["reasoning_effort"] = "none"  # LM Studio'da düşünmeyi gerçekten kapatan ayar
        if self.cfg.get("temperature") is not None:
            kwargs["temperature"] = self.cfg["temperature"]

        piece, color, _ = self.piece()
        out = StreamPrinter(self.show_thinking, Spinner(piece, color, self.animate), self.fancy(),
                            self.cfg.get("markdown", True))
        calls: dict[int, dict] = {}
        usage = None
        first = None
        budget = self._think_budget() if self.thinking and self.can_think() else 0
        self.last_finish = None
        out.show_status("bağlam işleniyor")
        # Akış ayrı bir iş parçacığında okunur; böylece model bir süre hiçbir şey göndermediğinde (ör. LM Studio araç
        # çağrısını tamamlanana kadar tutarken) ekranda ne olduğu ve geçen süre gösterilebilir.
        chunks: queue.Queue = queue.Queue()
        holder: dict = {}

        def pump() -> None:
            try:
                holder["stream"] = self.client.chat.completions.create(**kwargs)
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
            self._note("└ ✗ argümanlar okunamadı", "red")
            return f"Hata: argümanlar geçerli bir JSON nesnesi değil ({e})."
        if tool is None:
            self._tool_header(name, {}, ok=False)
            self._note("└ ✗ bilinmeyen araç", "red")
            return f"Hata: '{name}' adında bir araç yok. Kullanılabilir araçlar: {', '.join(tools.TOOLS)}"
        if missing := [k for k in tool.parameters.get("required", []) if k not in args]:
            self._tool_header(name, args, ok=False)
            self._note(f"└ ✗ eksik argüman: {', '.join(missing)}", "red")
            return (f"Hata: {name} için zorunlu argüman eksik: {', '.join(missing)}. Gönderilen argümanlar: "
                    f"{', '.join(args) or 'yok'}. Aracı tüm zorunlu argümanlarla tekrar çağır.")

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
            case "/think":
                choices = {"on": "on", "aç": "on", "ac": "on", "off": "off", "kapat": "off",
                           "auto": "auto", "otomatik": "auto"}
                if arg and arg.lower() not in choices:
                    console.print("[red]Kullanım: /think, /think on, /think off ya da /think auto[/]")
                else:
                    self.set_think_mode(choices[arg.lower()] if arg else ("off" if self.think_mode == "on" else "on"))
                    self._note("Düşünme " + {"on": "açık.", "off": "kapalı.", "auto": (
                        "otomatik: varsayılan kapalı; analiz sorularında ve bir komut başarısız olunca açılır."
                    )}[self.think_mode])
            case "/show":
                self.show_thinking = not self.show_thinking
                self._note(f"Düşünme metni {'gösteriliyor' if self.show_thinking else 'gizli'}.")
            case "/auto":
                self.auto = not self.auto
                if self.auto:
                    self._note("Onay sorulmayacak: model doğrudan dosya yazıp komut çalıştırabilir.", "yellow")
                else:
                    self._note("Onay yeniden soruluyor.")
            case "/model":
                models = server_models(self.base_url)
                if arg:
                    if self.set_model(arg, models):
                        self._note(f"Model: {self.name()}")
                else:
                    self.show_models(models)
            case "/load":
                self.load_preset(arg)
            case "/unload":
                if self._lms("unload", "--all"):
                    self.model, self.ctx = None, None
            case _:
                console.print(f"[red]Bilinmeyen komut: {escape(cmd)}[/] [dim](/help)[/]")
        return True

    def show_models(self, models: list[dict] | None) -> None:
        if models is None:
            console.print("[red]Sunucuya ulaşılamadı.[/]")
            return
        info = {m["id"]: m for m in models}
        table = Table(box=None, padding=(0, 2))
        for col in ("", "Model", "Durum", "Bağlam", ""):
            table.add_column(col)
        for alias, p in self.cfg.get("presets", {}).items():
            m = info.get(p["model"], {})
            loaded = m.get("state") == "loaded"
            glyph, color, _ = PIECES.get(alias, DEFAULT_PIECE)
            table.add_row(
                "→" if p["model"] == self.model else "", Text(f"{glyph} {alias}", style=f"bold {color}"),
                "[green]yüklü[/]" if loaded else ("[dim]yüklü değil[/]" if m else "[red]bulunamadı[/]"),
                str(m.get("loaded_context_length") or "") if loaded else "",
                f"[dim]{escape(p.get('desc', ''))}[/]",
            )
        console.print(table)
        self._note("/load <ad> ile yükle · /model <ad> ile yüklü olana geç")

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
        glyph, color, _ = PIECES.get(name, DEFAULT_PIECE)
        spinner = Spinner(glyph, color, self.animate)
        spinner.set(f"{name} yükleniyor", "diğer modeller boşaltılıyor")
        with Live(spinner, console=console, refresh_per_second=12.5, transient=True):
            ok = self._lms("unload", "--all") and self._lms("load", p["model"], *p.get("args", []), "-y")
        if not ok:
            return
        models = server_models(self.base_url) or []
        if self.set_model(name, models):
            console.print(Text.assemble(("  ✓ ", "green"), (f"{glyph} {name}", f"bold {color}"), " hazır",
                                        (f" · bağlam {self.ctx}" if self.ctx else "", MUTED)))

    def _lms(self, *args: str) -> bool:
        """lms'i çalıştırır; çıktısı (model kimlikleri içerir) ekrana basılmaz."""
        lms = lms_path(self.cfg)
        if not lms:
            console.print("[red]lms bulunamadı; config.json'daki lms_path ayarını kontrol et.[/]")
            return False
        r = subprocess.run([lms, *args], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            console.print(f"[red]LM Studio işlemi başarısız oldu ({escape(args[0])}, çıkış kodu {r.returncode}). "
                          "Model dosyası silinmiş ya da bellek yetersiz olabilir.[/]")
        return r.returncode == 0

    def _think_state(self) -> str:
        return {"on": "açık", "off": "kapalı", "auto": "otomatik"}[self.think_mode] if self.can_think() else "yok"

    def toolbar(self) -> FormattedText:
        glyph, color, _ = self.piece()
        parts = [f"düşünme {self._think_state()}", f"araçlar {'açık' if self.use_tools else 'kapalı'}",
                 f"onay {'otomatik' if self.auto else 'sorulur'}"]
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
    for part in ([f"bağlam {chat.ctx // 1024}k"] if chat.ctx else []) + [
            f"düşünme {chat._think_state()}", f"araçlar {'açık' if chat.use_tools else 'kapalı'}"]:
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
    ap.add_argument("-m", "--model", help="kullanılacak model: knight, rook, queen, bishop, king "
                                          "(varsayılan: LM Studio'da yüklü olan)")
    ap.add_argument("--url", help="sunucu adresi (varsayılan: config.json'daki base_url)")
    ap.add_argument("--no-tools", action="store_true", help="araçları kapat, sadece sohbet")
    ap.add_argument("--think", action=argparse.BooleanOptionalAction, default=None,
                    help="düşünmeyi aç/kapat (varsayılan: config.json'daki thinking)")
    ap.add_argument("--auto-think", action="store_true",
                    help="otomatik düşünme: analiz sorularında ve bir komut başarısız olunca açılır")
    ap.add_argument("--show-think", action="store_true", help="düşünme metnini ekranda göster")
    ap.add_argument("--no-anim", action="store_true", help="animasyonları kapat")
    ap.add_argument("-y", "--yes", action="store_true", help="dosya yazma/komut onayı sorma (dikkat!)")
    args = ap.parse_args()

    cfg = load_config()
    base_url = args.url or cfg["base_url"]
    client = OpenAI(base_url=base_url, api_key=cfg.get("api_key") or "lm-studio", timeout=3600, max_retries=0)
    chat = Chat(client, cfg, base_url, args)

    models = ensure_server(cfg, base_url)
    if models is None:
        console.print(f"[red]Sunucuya ulaşılamadı: {escape(base_url)}[/]\nLM Studio'yu aç ya da şunu çalıştır: lms server start")
        return 1
    wanted = args.model or cfg.get("model")
    if wanted:
        chat.set_model(wanted, models)
    else:
        # yüklü modellerden araç kullanabilenler önce
        loaded = sorted((m for m in models if m.get("state") == "loaded"),
                        key=lambda m: "tool_use" not in m.get("capabilities", []))
        if loaded:
            chat.set_model(loaded[0]["id"], models)

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
