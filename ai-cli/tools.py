"""Modelin kullanabileceği araçlar: JSON şema tanımları ve uygulamaları."""

import difflib
import fnmatch
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

MAX_OUTPUT = 20_000  # modele dönen tek bir araç çıktısının üst sınırı (karakter)
MAX_FILE_BYTES = 2_000_000
MAX_ENTRIES = 500
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".mypy_cache", ".pytest_cache", "dist", "build"}
CODE_EXTS = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".ps1", ".sh", ".go", ".rs", ".java", ".c", ".cpp",
             ".cs", ".php", ".rb"}
CHECK_COMMANDS = {".py": 'python -m py_compile "{p}"', ".js": 'node --check "{p}"', ".mjs": 'node --check "{p}"',
                  ".cjs": 'node --check "{p}"'}


class ToolError(Exception):
    """Modele hata mesajı olarak dönen, beklenen hatalar."""


@dataclass
class Tool:
    description: str
    parameters: dict
    run: Callable[..., str]
    needs_approval: bool = False
    preview: Callable[..., str] | None = None
    preview_lexer: str = "diff"
    echo_lines: int = 1  # sonuçtan ekranda gösterilecek satır sayısı


def truncate(text: str, limit: int = MAX_OUTPUT) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [kesildi, {len(text) - limit} karakter daha var]"


def _path(path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(path))).resolve()


def _size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def _is_binary(p: Path) -> bool:
    with open(p, "rb") as f:
        return b"\0" in f.read(8192)


def _read_raw(p: Path, strict: bool = False) -> str:
    if not p.is_file():
        raise ToolError(f"dosya bulunamadı: {p}")
    if p.stat().st_size > MAX_FILE_BYTES:
        raise ToolError(f"dosya çok büyük ({_size(p.stat().st_size)}): {p}")
    if _is_binary(p):
        raise ToolError(f"ikili (binary) dosya, metin olarak okunamaz: {p}")
    try:
        with open(p, encoding="utf-8", errors="strict" if strict else "replace", newline="") as f:
            return f.read()
    except UnicodeDecodeError:
        raise ToolError(f"dosya UTF-8 değil, bozulmaması için düzenlenmedi: {p}")


def _write(p: Path, text: str, crlf: bool) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    text = text.replace("\r\n", "\n")
    if crlf:
        text = text.replace("\n", "\r\n")
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def _diff(p: Path, old: str, new: str) -> str:
    lines = difflib.unified_diff(old.splitlines(), new.splitlines(), f"a/{p.name}", f"b/{p.name}", n=2, lineterm="")
    return "\n".join(lines) or "(değişiklik yok)"


def _verify_hint(p: Path) -> str:
    """Kod dosyası yazıldıysa modele doğrulama hatırlatması (küçük modeller sistem mesajındaki kuralı unutuyor)."""
    ext = p.suffix.lower()
    if ext not in CODE_EXTS:
        return ""
    check = CHECK_COMMANDS.get(ext)
    example = f" (e.g. {check.format(p=p)})" if check else ""
    return (f"\nNext step: before finishing, verify this code yourself with run_command{example}, and run its tests "
            "if it has any. Do not ask the user to run it. Do not start servers or other commands that never finish.")


def _walk_files(root: Path, pattern: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if fnmatch.fnmatch(name.lower(), pattern.lower()):
                yield Path(dirpath) / name


# --- okuma araçları (onay gerekmez) ---

def read_file(path: str, start_line: int = 1, max_lines: int = 400) -> str:
    p = _path(path)
    lines = _read_raw(p).replace("\r\n", "\n").split("\n")
    if len(lines) > 1 and lines[-1] == "":
        lines.pop()  # dosya sonundaki satır sonu ayrı bir satır sayılmasın
    start = max(1, int(start_line))
    end = min(len(lines), start + max(1, int(max_lines)) - 1)
    body = "\n".join(f"{i:>5}→{lines[i - 1]}" for i in range(start, end + 1))
    more = f"\n... ({len(lines) - end} satır daha var; devamı için start_line={end + 1})" if end < len(lines) else ""
    return f"{p} ({len(lines)} satır; soldaki numaralar ve → işareti dosyaya ait değildir)\n{body}{more}"


def list_dir(path: str = ".", pattern: str = "*", recursive: bool = False) -> str:
    root = _path(path)
    if not root.is_dir():
        raise ToolError(f"klasör bulunamadı: {root}")
    rows = []
    if recursive:
        for fp in _walk_files(root, pattern):
            rows.append(str(fp.relative_to(root)))
            if len(rows) >= MAX_ENTRIES:
                break
    else:
        entries = sorted(root.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        for e in entries:
            if not fnmatch.fnmatch(e.name.lower(), pattern.lower()):
                continue
            try:
                rows.append(f"{e.name}/" if e.is_dir() else f"{e.name}  ({_size(e.stat().st_size)})")
            except OSError:
                rows.append(e.name)
            if len(rows) >= MAX_ENTRIES:
                break
    if not rows:
        return f"{root}: eşleşen öğe yok"
    more = f"\n... (ilk {MAX_ENTRIES} öğe gösterildi)" if len(rows) >= MAX_ENTRIES else ""
    return f"{root} ({len(rows)} öğe)\n" + "\n".join(rows) + more


def search_files(pattern: str, path: str = ".", file_pattern: str = "*") -> str:
    try:
        rx = re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ToolError(f"geçersiz regex: {e}")
    root = _path(path)
    if root.is_file():
        candidates, root = [root], root.parent
    elif root.is_dir():
        candidates = _walk_files(root, file_pattern)
    else:
        raise ToolError(f"yol bulunamadı: {root}")
    hits = []
    for fp in candidates:
        try:
            if fp.stat().st_size > MAX_FILE_BYTES or _is_binary(fp):
                continue
            with open(fp, encoding="utf-8", errors="replace") as f:
                for n, line in enumerate(f, 1):
                    if rx.search(line):
                        hits.append(f"{fp.relative_to(root)}:{n}: {line.strip()[:200]}")
                        if len(hits) >= 200:
                            return "\n".join(hits) + "\n... (ilk 200 eşleşme gösterildi)"
        except OSError:
            continue
    return "\n".join(hits) if hits else "eşleşme yok"


# --- yazma araçları (onay gerekir) ---

def write_file_preview(path: str, content: str) -> str:
    p = _path(path)
    if p.exists():
        return _diff(p, _read_raw(p).replace("\r\n", "\n"), content)
    return f"+++ {p} (yeni dosya)\n" + "\n".join("+" + line for line in content.splitlines())


def write_file(path: str, content: str) -> str:
    p = _path(path)
    crlf = p.exists() and "\r\n" in _read_raw(p)
    _write(p, content, crlf)
    return f"yazıldı: {p} ({len(content.splitlines())} satır)" + _verify_hint(p)


def _edit_target(path: str, old_text: str, new_text: str) -> tuple[Path, str, str, bool]:
    p = _path(path)
    raw = _read_raw(p, strict=True)
    text = raw.replace("\r\n", "\n")
    old_text = old_text.replace("\r\n", "\n")
    if not old_text:
        raise ToolError("old_text boş olamaz")
    count = text.count(old_text)
    if count == 0:
        raise ToolError("old_text dosyada bulunamadı; dosyayı read_file ile tekrar oku ve metni birebir (satır numaraları olmadan) kopyala")
    if count > 1:
        raise ToolError(f"old_text dosyada {count} kez geçiyor; çevresinden birkaç satır daha ekleyerek benzersiz yap")
    return p, text, text.replace(old_text, new_text.replace("\r\n", "\n"), 1), "\r\n" in raw


def edit_file_preview(path: str, old_text: str, new_text: str) -> str:
    p, old, new, _ = _edit_target(path, old_text, new_text)
    return _diff(p, old, new)


def edit_file(path: str, old_text: str, new_text: str) -> str:
    p, _, new, crlf = _edit_target(path, old_text, new_text)
    _write(p, new, crlf)
    return f"düzenlendi: {p}" + _verify_hint(p)


def _shell_args(command: str) -> list[str]:
    if os.name == "nt":
        exe = shutil.which("pwsh") or shutil.which("powershell")
        if exe:
            utf8 = "[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8; "
            return [exe, "-NoProfile", "-NonInteractive", "-Command", utf8 + command]
        return ["cmd", "/c", command]
    return ["/bin/sh", "-c", command]


def run_command(command: str, timeout: int = 120) -> str:
    timeout = min(max(int(timeout), 1), 600)
    try:
        r = subprocess.run(
            _shell_args(command), capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        raise ToolError(f"komut {timeout} saniyede bitmedi ve durduruldu")
    parts = [f"çıkış kodu: {r.returncode}"]
    if r.stdout.strip():
        parts.append(r.stdout.strip())
    if r.stderr.strip():
        parts.append("[stderr]\n" + r.stderr.strip())
    return "\n".join(parts)


def _schema(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required}


TOOLS: dict[str, Tool] = {
    "read_file": Tool(
        "Read a text file. Each returned line starts with its line number and an arrow, like '    3→text'; "
        "the number and the arrow are NOT part of the file content.",
        _schema({
            "path": {"type": "string", "description": "File path"},
            "start_line": {"type": "integer", "description": "First line to return (1-based). Default 1"},
            "max_lines": {"type": "integer", "description": "Maximum number of lines. Default 400"},
        }, ["path"]),
        read_file,
    ),
    "list_dir": Tool(
        "List files and folders. With recursive=true, lists matching files in all subfolders "
        "(use this to find files by name).",
        _schema({
            "path": {"type": "string", "description": "Folder path. Default: current directory"},
            "pattern": {"type": "string", "description": "Name filter like *.py. Default *"},
            "recursive": {"type": "boolean", "description": "Search subfolders. Default false"},
        }, []),
        list_dir,
    ),
    "search_files": Tool(
        "Search inside files with a case-insensitive regex. Returns file:line: text matches.",
        _schema({
            "pattern": {"type": "string", "description": "Regular expression to search for"},
            "path": {"type": "string", "description": "Folder or file to search. Default: current directory"},
            "file_pattern": {"type": "string", "description": "Only search files matching this name filter, like *.py"},
        }, ["pattern"]),
        search_files,
    ),
    "write_file": Tool(
        "Create a new file or completely overwrite an existing one. Parent folders are created. "
        "Requires user approval.",
        _schema({
            "path": {"type": "string", "description": "File path"},
            "content": {"type": "string", "description": "Full file content"},
        }, ["path", "content"]),
        write_file, needs_approval=True, preview=write_file_preview,
    ),
    "edit_file": Tool(
        "Replace one exact occurrence of old_text with new_text in a file. old_text must match the file "
        "exactly (copy it from read_file output without line numbers) and be unique. Requires user approval.",
        _schema({
            "path": {"type": "string", "description": "File path"},
            "old_text": {"type": "string", "description": "Exact existing text to replace"},
            "new_text": {"type": "string", "description": "Replacement text"},
        }, ["path", "old_text", "new_text"]),
        edit_file, needs_approval=True, preview=edit_file_preview,
    ),
    "run_command": Tool(
        "Run a shell command (PowerShell on Windows) in the current directory and return its output. "
        "Requires user approval. Do not run interactive commands.",
        _schema({
            "command": {"type": "string", "description": "Command to run"},
            "timeout": {"type": "integer", "description": "Seconds before the command is stopped. Default 120"},
        }, ["command"]),
        run_command, needs_approval=True, preview=lambda command, timeout=120: command,
        preview_lexer="powershell" if os.name == "nt" else "bash", echo_lines=20,
    ),
}


def schemas() -> list[dict]:
    return [
        {"type": "function", "function": {"name": name, "description": t.description, "parameters": t.parameters}}
        for name, t in TOOLS.items()
    ]
