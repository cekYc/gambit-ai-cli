"""Gambit CLI: LM Studio'daki (ya da OpenAI uyumlu herhangi bir sunucudaki) yerel modellerle terminalden
sohbet eder. Model dosya okuyup arayabilir; dosya yazma ve komut çalıştırma senin onayınla olur.
Modeller ekranda config.json'daki hazır ayar adlarıyla (knight, rook, queen, bishop, king) görünür."""

import argparse
import json
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
from datetime import date
from pathlib import Path

from openai import APIConnectionError, APIStatusError, OpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

import tools

HERE = Path(__file__).resolve().parent
HISTORY_FILE = Path.home() / ".ai_cli_history"
# Bazı modeller (ör. Gemma 4) araç çağrısını bazen sunucunun ayrıştıramadığı ham işaretlerle metne yazıyor
BROKEN_TOOL_CALL = re.compile(r"<\|?tool_call|tool_call\|?>|<function=|\[TOOL_CALLS\]")
# Otomatik düşünme modunda düşünmeyi açan soru kalıpları: kodun ne yaptığını, nedenini soran analiz soruları
ANALYSIS_QUESTION = re.compile(
    r"\bne (?:yazdır|döndür|yap|üret|çıkar)|çıktı(?:s[ıi])? ne|\bneden\b|\bniçin\b|\bniye\b|açıkla|analiz|"
    r"karşılaştır|nasıl çalış|hangisi daha|ne olur\b|ne fark|\bwhy\b|\bexplain\b|what does|what is the output|\bcompare\b",
    re.I)
console = Console(highlight=False)

COMMANDS = {
    "/help": "Komutları gösterir",
    "/model": "Modelleri listeler; /model <ad> ile yüklü olana geçer",
    "/load": "Modeli kendi ayarlarıyla yükler, ör. /load queen (diğer modelleri boşaltır)",
    "/unload": "Yüklü tüm modelleri boşaltır",
    "/clear": "Yeni sohbet başlatır",
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
        console.print("[dim]LM Studio sunucusu kapalı, başlatılıyor…[/]")
        subprocess.run([lms_path(cfg), "server", "start"], capture_output=True)
        models = server_models(base_url)
    return models


def analysis_question(text: str) -> bool:
    """Otomatik düşünme modunda bu mesaj düşünerek cevaplanmalı mı (kodun ne yaptığı, neden, açıklama...)."""
    return bool(ANALYSIS_QUESTION.search(text))


def command_failed(result: str) -> bool:
    """run_command sonucu başarısız mı (sıfır olmayan çıkış kodu ya da araç hatası)."""
    m = re.match(r"çıkış kodu: (-?\d+)", result)
    return bool(m and m.group(1) != "0") or result.startswith("Hata:")


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


def _short_args(args: dict) -> str:
    parts = []
    for k, v in args.items():
        if isinstance(v, str) and "\n" in v:
            v = f"<{v.count(chr(10)) + 1} satır>"
        elif isinstance(v, str) and len(v) > 80:
            v = v[:77] + "…"
        parts.append(f"{k}={v}")
    return escape(" ".join(parts))


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


class StreamPrinter:
    """Akan cevabı ekrana yazar. Düşünme kısmı (reasoning_content alanı ya da <think> etiketi) soluk
    gösterilir ya da gizlenir; geçmişe yalnızca asıl cevap (answer) kaydedilir."""

    def __init__(self, status, show_thinking: bool):
        self.status = status
        self.show_thinking = show_thinking
        self.answer = ""
        self.thought = ""
        self._buf = ""
        self._pending_ws = ""  # sondaki boşluklar; arkasından metin gelirse yazılır
        self._in_tag = False  # <think> ... </think> arasında mıyız
        self._mode = None  # en son ekrana yazılan tür: "think" | "text"
        self.active = False  # durum göstergesi (spinner) çalışıyor mu
        self.label = ""
        self._since = 0.0

    def show_status(self, label: str) -> None:
        """Ekrana bir şey akmıyorken ne olduğunu ve ne kadar süredir beklendiğini gösterir."""
        if self.label != label or not self.active:
            self._since = time.perf_counter()
        self.label = label
        if not self.active:
            if self._mode:  # yarım kalan satırı bitir; gösterge yeni satırda dursun
                console.out("")
                self._mode = None
            self.status.start()
            self.active = True
        self.tick()

    def tick(self) -> None:
        if self.active:
            self.status.update(f"[dim]{escape(self.label)} {time.perf_counter() - self._since:.0f} sn[/]")

    def stop_status(self) -> None:
        if self.active:
            self.status.stop()
            self.active = False

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
        if self._mode:
            console.out("")
        self._mode = None
        self.answer = self.answer.rstrip()

    def _emit(self, kind: str, s: str) -> None:
        if kind == "think":
            self.thought += s
        if kind == "think" and not self.show_thinking:
            if s:
                self.show_status("düşünüyor…")
            return
        if kind != self._mode:
            s = s.lstrip()
            if not s:
                return
            self.stop_status()
            if self._mode:
                console.out("\n")
            self._mode = kind
            self._pending_ws = ""
        s = self._pending_ws + s
        visible = s.rstrip()
        self._pending_ws = s[len(visible) :]
        if kind == "text":
            self.answer += visible
            console.out(visible, end="", highlight=False)
        else:
            console.out(visible, end="", style="dim italic", highlight=False)


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
        self.escalations = 0  # otomatik modda doğrulama başarısız olduğu için düşünmenin açıldığı tur sayısı
        self.show_thinking = args.show_think or cfg.get("show_thinking", False)
        self.auto = args.yes
        self.always: set[str] = set()  # bu oturumda hep onaylanan araçlar
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
            lines += [
                "You have tools to list, read, search, create and edit files and to run shell commands"
                + (" (PowerShell)." if os.name == "nt" else "."),
                "Use them whenever you need real information; never invent file contents or command output.",
                "Relative paths are relative to the current directory.",
                "Read a file before editing it. Use edit_file for small changes, write_file for new files or full rewrites.",
                "When the user asks you to write or create a program, script or file, save it with write_file; do not "
                "paste the whole file into the chat instead. If they also ask you to run it, run it with run_command.",
                "Never say that you created a file, ran a command or verified something unless a tool result in this "
                "conversation confirms it.",
                "write_file, edit_file and run_command ask the user for approval. If the user rejects, "
                "follow their note or ask what they want instead.",
                "After writing or changing code you MUST verify it yourself with run_command before finishing; "
                "never ask the user to run it for you. Syntax-check it (python -m py_compile file.py, "
                "node --check file.js), run its tests, or exercise it with a short one-off script (for a web app, "
                "call it through its test client, e.g. Flask's app.test_client()). If the check fails, fix the code "
                "and check again. Briefly tell the user what you verified.",
                "Never run commands that do not finish on their own (web servers, watchers, interactive programs that "
                "wait for keyboard input); they hang until the timeout. Check those another way (syntax check, a short "
                "script that imports and tests the logic) and tell the user the command to start them themselves.",
                "Never remove or weaken a requested feature just to make a check pass (for example deleting input() "
                "calls so a game exits cleanly). If something cannot be verified here, keep it and say so honestly.",
            ]
        return "\n".join(lines)

    def reset(self) -> None:
        self.messages = [{"role": "system", "content": self.system_prompt()}]

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

    def can_think(self) -> bool:
        """Model düşünme modunu destekliyor mu (hazır ayarda "thinking": false ise hayır)."""
        preset = self.cfg.get("presets", {}).get(self.name(), {})
        return preset.get("thinking", True)

    # --- sohbet / ajan döngüsü ---

    def set_think_mode(self, mode: str) -> None:
        """on / off / auto. auto: varsayılan kapalı; analiz sorularında ya da doğrulama başarısız olunca o tur açık."""
        self.think_mode = mode
        self.thinking = mode == "on"

    def ask(self, text: str) -> None:
        start = len(self.messages)
        self.messages.append({"role": "user", "content": text})
        retries = 0
        empty_retry = False
        if self.think_mode == "auto":
            self.thinking = analysis_question(text)
            if self.thinking and self.can_think():
                console.print("[dim]Analiz sorusu: bu tur düşünme açık.[/]")
        try:
            for _ in range(self.cfg.get("max_steps", 25)):
                calls = self._complete()
                if not calls:
                    last = self.messages[-1]
                    if last["role"] != "assistant" and not self.thinking and not empty_retry and self.can_think():
                        # Bazı modeller (ör. bazı Gemma ince ayarları) düşünme kapalıyken araç sonucundan sonra boş dönüyor
                        empty_retry = True
                        self.thinking = True
                        console.print("[dim]Model boş cevap verdi; bu adım düşünme açık olarak tekrarlanıyor.[/]")
                        continue
                    if last["role"] == "assistant" and BROKEN_TOOL_CALL.search(last["content"] or "") and retries < 2:
                        retries += 1
                        console.print("[yellow]Model bozuk bir araç çağrısı üretti; tekrar denemesi isteniyor.[/]")
                        self.messages.append({"role": "user", "content": (
                            "Son mesajındaki araç çağrısı bozuk biçimde geldi ve çalıştırılmadı. Aracı doğru biçimde "
                            "tekrar çağır; iş bittiyse sonucu yaz.")})
                        continue
                    return
                for call in calls:
                    result = self._run_tool(call)
                    self.messages.append({"role": "tool", "tool_call_id": call["id"], "content": result})
                    if (self.think_mode == "auto" and not self.thinking and self.can_think()
                            and call["function"]["name"] == "run_command" and command_failed(result)):
                        self.thinking = True
                        self.escalations += 1
                        console.print("[dim]Komut başarısız oldu: bu turun geri kalanında düşünme açık.[/]")
            console.print("[yellow]Adım sınırına ulaşıldı, durduruldu.[/]")
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

        status = console.status("", spinner="dots")
        out = StreamPrinter(status, self.show_thinking)
        calls: dict[int, dict] = {}
        usage = None
        first = None
        out.show_status("bekleniyor…")
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

        threading.Thread(target=pump, daemon=True).start()
        last = time.perf_counter()
        try:
            while True:
                try:
                    chunk = chunks.get(timeout=0.25)
                except queue.Empty:
                    if not out.active and time.perf_counter() - last > 2:
                        name = next((c["name"] for c in calls.values() if c["name"]), "")
                        out.show_status(f"{name} hazırlanıyor…" if name else
                                        "model yazmaya devam ediyor (araç çağrısı hazırlıyor olabilir)…")
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
                delta = chunk.choices[0].delta
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
                        out.show_status(f"{slot['name']} hazırlanıyor…")
                    if tc.function and tc.function.arguments:
                        slot["arguments"] += tc.function.arguments
        except KeyboardInterrupt:
            try:
                holder["stream"].close()  # sunucunun üretmeyi bırakması için bağlantıyı kapat
            except Exception:
                pass
            out.finish()
            self._save_assistant(out.answer, [])
            raise
        finally:
            out.stop_status()
        out.finish()

        tool_calls = [
            {"id": c["id"] or f"call_{i}_{len(self.messages)}", "type": "function",
             "function": {"name": c["name"], "arguments": c["arguments"] or "{}"}}
            for i, c in sorted(calls.items())
        ]
        if not out.answer and not tool_calls and out.thought.strip():
            # Bazı modeller (ör. Qwen3.5) araç kullandıktan sonra cevabın tamamını düşünme kısmına yazıyor
            out.answer = out.thought.strip()
            if not self.show_thinking:
                console.out(out.answer)
        if not out.answer and not tool_calls:
            console.print("[dim](boş cevap)[/]")
        self._save_assistant(out.answer, tool_calls)
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
        if not usage or not first:
            return
        elapsed = time.perf_counter() - first
        parts = [f"{usage.completion_tokens} token"]
        if elapsed > 0:
            parts.append(f"{usage.completion_tokens / elapsed:.1f} tok/s")
        if self.ctx:
            parts.append(f"bağlam {usage.total_tokens / 1000:.1f}k/{self.ctx / 1000:.1f}k")
        console.print(f"[dim]  {' · '.join(parts)}[/]")
        if self.ctx and usage.total_tokens > 0.8 * self.ctx:
            console.print("[yellow]  Bağlam dolmak üzere; /clear ile yeni sohbet başlatabilirsin.[/]")

    def _run_tool(self, call: dict) -> str:
        name = call["function"]["name"]
        tool = tools.TOOLS.get(name)
        try:
            args = json.loads(call["function"]["arguments"] or "{}")
            if not isinstance(args, dict):
                raise ValueError("JSON nesnesi bekleniyordu")
        except ValueError as e:
            console.print(f"[red]✗ {escape(name)}: argümanlar okunamadı[/]")
            return f"Hata: argümanlar geçerli bir JSON nesnesi değil ({e})."
        if tool is None:
            console.print(f"[red]✗ bilinmeyen araç: {escape(name)}[/]")
            return f"Hata: '{name}' adında bir araç yok. Kullanılabilir araçlar: {', '.join(tools.TOOLS)}"

        console.print(f"[cyan]→ {name}[/] [dim]{_short_args(args)}[/]")
        try:
            if tool.needs_approval and not self.auto and name not in self.always:
                if tool.preview:
                    console.print(Syntax(_clip(tool.preview(**args), 80), tool.preview_lexer,
                                         theme="ansi_dark", background_color="default", word_wrap=True))
                verdict = self._approve(name)
                if verdict is not True:
                    console.print("[yellow]  reddedildi[/]")
                    return "Kullanıcı bu işlemi reddetti." + (f" Kullanıcının notu: {verdict}" if verdict else "")
            result = tool.run(**args)
        except TypeError as e:
            result = f"Hata: geçersiz argümanlar ({e})."
        except tools.ToolError as e:
            result = f"Hata: {e}"
        except Exception as e:
            result = f"Hata: {type(e).__name__}: {e}"

        lines = result.splitlines() or [""]
        style = "red" if result.startswith("Hata") else "dim"
        for line in lines[: tool.echo_lines]:
            console.print(f"  {escape(line[:200])}", style=style)
        if len(lines) > tool.echo_lines:
            console.print(f"  … (+{len(lines) - tool.echo_lines} satır)", style="dim")
        return tools.truncate(result)

    def _approve(self, name: str) -> bool | str:
        """True: onaylandı. str: reddedildi (boş değilse kullanıcının modele notu)."""
        try:
            ans = console.input(
                "  [bold yellow]Onaylıyor musun?[/] [dim]e = evet · t = bu oturumda hep evet · h = hayır · "
                "ya da modele ne yapmasını istediğini yaz[/]\n  › "
            ).strip()
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
                    table.add_row(f"[cyan]{c}[/]", desc)
                console.print(table)
                console.print("[dim]Alt+Enter: yeni satır · Ctrl+C: cevabı durdurur · ↑/↓: önceki mesajlar[/]")
            case "/clear":
                self.reset()
                console.print("[dim]Yeni sohbet başladı.[/]")
            case "/tools":
                self.use_tools = not self.use_tools
                self.messages[0]["content"] = self.system_prompt()
                console.print(f"[dim]Araçlar {'açık' if self.use_tools else 'kapalı'}.[/]")
            case "/think":
                choices = {"on": "on", "aç": "on", "ac": "on", "off": "off", "kapat": "off",
                           "auto": "auto", "otomatik": "auto"}
                if arg and arg.lower() not in choices:
                    console.print("[red]Kullanım: /think, /think on, /think off ya da /think auto[/]")
                else:
                    self.set_think_mode(choices[arg.lower()] if arg else ("off" if self.think_mode == "on" else "on"))
                    console.print("[dim]Düşünme " + {"on": "açık.", "off": "kapalı.", "auto": (
                        "otomatik: varsayılan kapalı; analiz sorularında ve bir komut başarısız olunca o tur açılır."
                    )}[self.think_mode] + "[/]")
            case "/show":
                self.show_thinking = not self.show_thinking
                console.print(f"[dim]Düşünme metni {'gösteriliyor' if self.show_thinking else 'gizli'}.[/]")
            case "/auto":
                self.auto = not self.auto
                console.print("[yellow]Onay sorulmayacak: model doğrudan dosya yazıp komut çalıştırabilir.[/]"
                              if self.auto else "[dim]Onay yeniden soruluyor.[/]")
            case "/model":
                models = server_models(self.base_url)
                if arg:
                    if self.set_model(arg, models):
                        console.print(f"[dim]Model: {escape(self.name())}[/]")
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
            table.add_row(
                "→" if p["model"] == self.model else "", f"[cyan]{escape(alias)}[/]",
                "[green]yüklü[/]" if loaded else ("[dim]yüklü değil[/]" if m else "[red]bulunamadı[/]"),
                str(m.get("loaded_context_length") or "") if loaded else "",
                f"[dim]{escape(p.get('desc', ''))}[/]",
            )
        console.print(table)
        console.print("[dim]/load <ad> ile yükle · /model <ad> ile yüklü olana geç[/]")

    def load_preset(self, name: str) -> None:
        presets = self.cfg.get("presets", {})
        if name not in presets:
            if name:
                console.print(f"[red]'{escape(name)}' adında hazır ayar yok.[/]")
            table = Table(show_header=False, box=None, padding=(0, 2))
            for key, p in presets.items():
                table.add_row(f"[cyan]/load {key}[/]", f"[dim]{escape(p.get('desc', ''))}[/]")
            console.print(table)
            return
        p = presets[name]
        with console.status(f"[dim]{escape(name)} yükleniyor (diğer modeller boşaltılıyor)…[/]", spinner="dots"):
            ok = self._lms("unload", "--all") and self._lms("load", p["model"], *p.get("args", []), "-y")
        if not ok:
            return
        models = server_models(self.base_url) or []
        if self.set_model(name, models):
            console.print(f"[green]Hazır:[/] {escape(name)}" + (f" [dim](bağlam {self.ctx})[/]" if self.ctx else ""))

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

    def toolbar(self) -> str:
        state = {"on": "açık", "off": "kapalı", "auto": "otomatik"}[self.think_mode] if self.can_think() else "yok"
        return (f" Gambit · {self.name()} · düşünme {state}"
                f" · araçlar {'açık' if self.use_tools else 'kapalı'}"
                f" · onay {'otomatik' if self.auto else 'sorulur'} · /help")


def repl(chat: Chat) -> None:
    keys = KeyBindings()

    @keys.add("escape", "enter")
    def _newline(event):
        event.current_buffer.insert_text("\n")

    session = PromptSession(
        history=FileHistory(str(HISTORY_FILE)), key_bindings=keys,
        completer=WordCompleter(list(COMMANDS), sentence=True), bottom_toolbar=chat.toolbar,
    )
    while True:
        try:
            text = session.prompt("› ").strip()
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

    ctx = f" [dim](bağlam {chat.ctx})[/]" if chat.ctx else ""
    console.print(Panel.fit(
        f"[bold]Gambit CLI[/] · model: [cyan]{escape(chat.name() if chat.model else 'yok, /load queen ile yükle')}[/]{ctx}\n"
        f"[dim]{escape(os.getcwd())} · /help komutlar · Alt+Enter yeni satır · Ctrl+C durdurur[/]",
        border_style="blue",
    ))
    repl(chat)
    return 0


if __name__ == "__main__":
    sys.exit(main())
