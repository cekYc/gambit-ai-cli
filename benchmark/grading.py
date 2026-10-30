"""Notlandırıcılar: cevaptan kod bloğu çıkarma, kodu ayrı bir süreçte test etme, SQL ve PowerShell
çalıştırma ve model çıktısını çalıştırmadan önce yapılan güvenlik kontrolleri."""

import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

CODE_BLOCK = re.compile(r"```[ \t]*([\w+#.-]*)[^\n]*\n(.*?)```", re.S)
LANGS = {
    "python": {"python", "py", "python3"},
    "js": {"javascript", "js", "node", "nodejs", "jsx"},
    "sql": {"sql", "sqlite", "sqlite3"},
    "powershell": {"powershell", "ps1", "pwsh", "ps", "posh"},
    "text": {"text", "txt", "plaintext", "plain", "output", "console", ""},
}

# Görevlerin hiçbiri bunlara ihtiyaç duymuyor; geçerse kod çalıştırılmaz
DANGEROUS_PY = re.compile(r"\b(subprocess|os\.system|os\.popen|os\.remove|os\.unlink|os\.rmdir|os\.removedirs|shutil|"
                          r"socket|urllib|requests|http\.client|ctypes|winreg|webbrowser)\b")
DANGEROUS_JS = re.compile(r"child_process|require\(\s*['\"](?:fs|net|http|https|dgram|os|cluster)['\"]\s*\)|process\.kill")
# Klasör dışını etkileyebilecek PowerShell komutları; dosya işlemleri yalnızca yol kontrolünden geçerse çalışır
SHELL_DENY = re.compile(
    r"\b(Stop-Process|kill|taskkill|Restart-Computer|Stop-Computer|shutdown|Set-ExecutionPolicy|Invoke-WebRequest|iwr|"
    r"Invoke-RestMethod|irm|curl|wget|Start-BitsTransfer|Start-Process|saps|Invoke-Expression|iex|Invoke-Command|icm|"
    r"Set-ItemProperty|New-ItemProperty|Remove-ItemProperty|reg|regedit|schtasks|Register-ScheduledTask|Set-Service|"
    r"Stop-Service|Restart-Service|New-Service|Format-Volume|Clear-Disk|Clear-RecycleBin|net|netsh|winget|choco|"
    r"Install-Module|Install-Package|pip|pip3|npm|npx|Set-Acl|takeown|icacls|bcdedit|diskpart|cipher)\b(?!-)", re.I)
ABS_PATH = re.compile(r"(?<![\w$])([A-Za-z]:[\\/][^\s'\"`|;,)}]*)")


def extract_code(answer: str, lang: str, prefer: str = "", longest: bool = False) -> str:
    """Cevaptan istenen dildeki kod bloğunu çıkarır. Birden fazla blok varsa `prefer` regex'ine uyan sonuncuyu
    (ör. fonksiyon tanımı olan blok), yoksa o dildeki son bloğu (`longest` ile en uzununu; kullanım örnekleri
    genelde çözümden kısadır), o dilde blok yoksa herhangi bir bloğu aynı kuralla seçer."""
    blocks = CODE_BLOCK.findall(answer)
    if prefer:
        preferred = [body for _, body in blocks if re.search(prefer, body, re.M)]
        if preferred:
            return preferred[-1].strip("\n")
    pool = [body for tag, body in blocks if tag.lower() in LANGS[lang]] or [body for _, body in blocks]
    if pool:
        return (max(pool, key=len) if longest else pool[-1]).strip("\n")
    unclosed = re.search(r"```[^\n]*\n(.*)$", answer, re.S)  # token sınırında kesilmiş blok
    return (unclosed.group(1) if unclosed else answer).strip()


def python_danger(code: str) -> str | None:
    m = DANGEROUS_PY.search(code)
    return f"güvenlik filtresi: {m.group(0)}" if m else None


def shell_safety(cmd: str, sandbox: Path) -> str | None:
    """Komut sandbox klasörü dışını etkileyebilecekse nedenini döndürür, güvenliyse None."""
    m = SHELL_DENY.search(cmd)
    if m:
        return f"izin verilmeyen komut: {m.group(0)}"
    if re.search(r"(?:^|[\s'\"(=,])\\\\", cmd):
        return "ağ yolu"
    if re.search(r"(?:^|[\s'\"(=,\\/])\.\.(?:[\\/'\"\s;)]|$)", cmd):
        return "üst klasöre çıkış"
    if re.search(r"(?:^|[\s'\"(=,])~|\$HOME\b|\$env:|\$PSHOME|\$PROFILE|\[(?:System\.)?Environment\]", cmd, re.I):
        return "ev/ortam yolu"
    root = str(sandbox.resolve()).lower()
    for m in ABS_PATH.finditer(cmd):
        raw = m.group(1).rstrip(".\\/")
        try:
            resolved = str(Path(raw).resolve()).lower()
        except (OSError, ValueError):
            return f"geçersiz yol: {raw}"
        if resolved != root and not resolved.startswith(root + os.sep):
            return f"klasör dışı yol: {raw}"
    return None


def _env() -> dict:
    return dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")


def run(cmd: list[str], cwd: Path | str, timeout: float) -> tuple[int, str, str, bool]:
    """(çıkış kodu, stdout, stderr, zaman aşımı mı). Zaman aşımında süreç ağacının tamamı kapatılır."""
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace", env=_env())
    try:
        out, err = p.communicate(timeout=timeout)
        return p.returncode, out, err, False
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else:
            p.kill()
        out, err = p.communicate()
        return -1, out, err, True


def run_powershell(cmd: str, cwd: Path, timeout: float = 60) -> tuple[int, str, str, bool]:
    exe = shutil.which("pwsh") or shutil.which("powershell")
    prefix = ("[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8; "
              "$ProgressPreference = 'SilentlyContinue'; ")
    return run([exe, "-NoProfile", "-NonInteractive", "-Command", prefix + cmd], cwd, timeout)


def _run_harness(cmd: list[str], files: dict[str, str], timeout: float = 30) -> tuple[float, str]:
    with tempfile.TemporaryDirectory(prefix="bench_", ignore_cleanup_errors=True) as d:
        for name, text in files.items():
            Path(d, name).write_text(text, encoding="utf-8")
        _, out, err, timed_out = run(cmd, d, timeout)
    if timed_out:
        return 0.0, "zaman aşımı"
    for line in reversed(out.strip().splitlines()):
        try:
            data = json.loads(line)
        except ValueError:
            continue
        if isinstance(data, dict) and "passed" in data:
            detail = f"{data['passed']}/{data['total']} test"
            if data.get("errors"):
                detail += "; başarısız: " + " | ".join(data["errors"])[:400]
            return data["passed"] / max(data["total"], 1), detail
    return 0.0, "çalışmadı: " + (err or out).strip()[-300:]


def grade_python(code: str, tests: list[str], prelude: str = "", forbid: str = "") -> tuple[float, str]:
    """Kodu solution.py olarak kaydedip testleri ayrı bir Python sürecinde çalıştırır; puan = geçen test oranı."""
    if not code.strip():
        return 0.0, "cevapta kod yok"
    if forbid and (m := re.search(forbid, code)):
        return 0.0, f"yasaklanan yapı kullanılmış: {m.group(0)}"
    if reason := python_danger(code):
        return 0.0, reason
    lines = [
        "import json, sys",
        "passed, errors = 0, []",
        "try:",
        "    import solution as S",
        "except BaseException as e:",
        f"    print(json.dumps({{'passed': 0, 'total': {len(tests)}, 'errors': ['import: ' + repr(e)[:300]]}}))",
        "    sys.exit(0)",
        prelude,
    ]
    for t in tests:
        lines += [
            "try:",
            f"    ok = bool({t})",
            "except BaseException as e:",
            f"    ok = False; errors.append({t!r} + ' -> ' + repr(e)[:200])",
            "else:",
            f"    if not ok: errors.append({t!r})",
            "passed += ok",
        ]
    lines.append(f"print(json.dumps({{'passed': passed, 'total': {len(tests)}, 'errors': errors[:5]}}))")
    return _run_harness([sys.executable, "harness.py"], {"solution.py": code, "harness.py": "\n".join(lines)})


def grade_js(code: str, tests: list[str], prelude: str, entry: str) -> tuple[float, str]:
    """Kodu Node.js'te solution.js olarak yükleyip testleri çalıştırır."""
    if not code.strip():
        return 0.0, "cevapta kod yok"
    if m := DANGEROUS_JS.search(code):
        return 0.0, f"güvenlik filtresi: {m.group(0)}"
    code = re.sub(r"^\s*export\s+(?:default\s+)?", "", code, flags=re.M)  # ESM yazılmışsa CommonJS'e çevir
    code += (f"\n;try {{ if (typeof {entry} === 'function' && !(module.exports && module.exports.{entry})) "
             f"module.exports.{entry} = {entry}; }} catch (e) {{}}\n")
    lines = [
        "let S;",
        f"try {{ S = require('./solution.js'); }} catch (e) {{ console.log(JSON.stringify({{passed: 0, total: {len(tests)}, "
        "errors: ['require: ' + String(e).slice(0, 300)]})); process.exit(0); }",
        "let passed = 0; const errors = [];",
        prelude,
    ]
    for t in tests:
        lines.append(f"try {{ if ({t}) passed++; else errors.push({json.dumps(t)}); }} "
                     f"catch (e) {{ errors.push({json.dumps(t)} + ' -> ' + String(e).slice(0, 200)); }}")
    lines.append(f"console.log(JSON.stringify({{passed, total: {len(tests)}, errors: errors.slice(0, 5)}}));")
    return _run_harness([shutil.which("node"), "harness.js"], {"solution.js": code, "harness.js": "\n".join(lines)})


def run_snippet(code: str, lang: str) -> str:
    """Kod okuma görevlerinin beklenen çıktısını kodu gerçekten çalıştırarak üretir."""
    name = "snippet.py" if lang == "python" else "snippet.js"
    with tempfile.TemporaryDirectory(prefix="bench_", ignore_cleanup_errors=True) as d:
        Path(d, name).write_text(code, encoding="utf-8")
        cmd = [sys.executable, name] if lang == "python" else [shutil.which("node"), name]
        rc, out, err, timed_out = run(cmd, d, 30)
    if rc != 0 or timed_out:
        raise RuntimeError(f"örnek kod çalışmadı: {err}")
    return out


def normalize_output(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def grade_output(answer: str, expected: str) -> tuple[float, str]:
    got = normalize_output(extract_code(answer, "text"))
    want = normalize_output(expected)
    if got == want:
        return 1.0, "doğru"
    return 0.0, f"beklenen {want!r}, cevap {got[:200]!r}"


_SQL_ALLOWED = {getattr(sqlite3, name, code) for name, code in
                [("SQLITE_SELECT", 21), ("SQLITE_READ", 20), ("SQLITE_FUNCTION", 31), ("SQLITE_RECURSIVE", 33)]}


def _sql_authorizer(action, *_):
    return sqlite3.SQLITE_OK if action in _SQL_ALLOWED else sqlite3.SQLITE_DENY


def _norm_rows(rows) -> list[tuple]:
    return [tuple(round(float(v), 2) if isinstance(v, (int, float)) else v for v in row) for row in rows]


def grade_sql(query: str, reference: str, make_db) -> tuple[float, str]:
    """Sorguyu yalnızca okuma izni olan bir bellek içi veritabanında çalıştırıp referans sonuçla karşılaştırır."""
    query = query.strip().rstrip(";").strip()
    if not query:
        return 0.0, "cevapta sorgu yok"
    conn = make_db()
    try:
        expected = _norm_rows(conn.execute(reference).fetchall())
        conn.set_authorizer(_sql_authorizer)
        deadline = time.monotonic() + 10
        conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 10_000)
        try:
            got = _norm_rows(conn.execute(query).fetchall())
        except (sqlite3.Error, sqlite3.Warning) as e:
            return 0.0, f"SQL hatası: {e}"
    finally:
        conn.close()
    if got == expected:
        return 1.0, "doğru"
    return 0.0, f"beklenen {expected[:4]}, sonuç {got[:4]}"
