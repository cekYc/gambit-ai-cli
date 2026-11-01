"""Gambit Bench v2 çekirdeği: görev tanımı, kısmi puanlama (rubrik), gizli test koşucuları ve cevap ayrıştırıcıları.

Puanlama ilkeleri
- Her görev bir rubrikle puanlanır: her maddenin bir ağırlığı ve 0..1 arası bir değeri vardır; görev puanı
  ağırlıklı ortalamadır. Böylece kısmen doğru bir çözüm kısmen puan alır (0 ya da 100'e sıkışmaz).
- Her görevin bir zorluk seviyesi vardır (1 kolay … 4 çok zor); seviye görevin genel puana katkı ağırlığıdır.
  Genel puan = Σ(ağırlık × görev puanı) / Σ ağırlık.
"""

from __future__ import annotations

import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
sys.path.append(str(HERE.parent))  # benchmark/ (grading.py: güvenlik filtreleri); v2 modülleri önce gelir

import grading  # noqa: E402

CATEGORIES = ["Kod yazma", "Hata ayıklama", "Kod okuma", "SQL", "Terminal", "Ajan", "Mantık", "Talimat", "Kod inceleme"]
LEVELS = {1: "kolay", 2: "orta", 3: "zor", 4: "çok zor"}
LEVEL_WEIGHT = {1: 1.0, 2: 2.0, 3: 3.0, 4: 4.0}


# ---------------------------------------------------------------- rubrik

@dataclass
class Item:
    name: str
    weight: float
    value: float  # 0..1
    note: str = ""


class Rubric:
    """Ağırlıklı kontrol listesi. `gate` çarpanları (ör. dosya yanlış yerde: ×0.75) tüm puana uygulanır."""

    def __init__(self) -> None:
        self.items: list[Item] = []
        self.gates: list[tuple[str, float]] = []
        self.notes: list[str] = []  # puanı etkilemeyen açıklamalar (ör. başarısız testlerin hata mesajları)

    def add(self, name: str, weight: float, value: float | bool, note: str = "") -> "Rubric":
        v = float(value)
        self.items.append(Item(name, weight, max(0.0, min(1.0, v)), note))
        return self

    def gate(self, reason: str, factor: float) -> "Rubric":
        self.gates.append((reason, factor))
        return self

    def note(self, text: str) -> "Rubric":
        if text:
            self.notes.append(text)
        return self

    def extend(self, items: list[Item]) -> "Rubric":
        self.items.extend(items)
        return self

    @property
    def score(self) -> float:
        total = sum(i.weight for i in self.items)
        if total <= 0:
            return 0.0
        s = sum(i.weight * i.value for i in self.items) / total
        for _, f in self.gates:
            s *= f
        return max(0.0, min(1.0, s))

    def detail(self, limit: int = 600) -> str:
        bad = [f"{i.name}{' (' + format(i.value, '.2f') + ')' if 0 < i.value < 1 else ''}"
               + (f" [{i.note}]" if i.note else "") for i in self.items if i.value < 0.999]
        parts = [f"{r} ×{f:g}" for r, f in self.gates]
        if bad:
            parts.append("eksik: " + "; ".join(bad))
        parts += self.notes
        text = " | ".join(parts) if parts else "tam"
        return text[:limit]

    def to_json(self) -> list[list]:
        return [[i.name, i.weight, round(i.value, 4), i.note] for i in self.items]


# ---------------------------------------------------------------- görev

@dataclass
class Trace:
    """Bir görev çalıştırmasının izi: ajanın araç çağrıları (ad, argümanlar, sonuç) ve son cevabı."""
    events: list[dict] = field(default_factory=list)
    final: str = ""

    def commands(self) -> list[str]:
        return [str(e["args"].get("command", "")) for e in self.events if e["name"] == "run_command"]

    def verified_after_write(self, *names: str) -> bool:
        """Verilen dosyalardan birine son yazmadan sonra en az bir komut çalıştırılmış mı (kendi kendini doğrulama)."""
        last_write = -1
        for i, e in enumerate(self.events):
            if e["name"] in ("write_file", "edit_file"):
                p = str(e["args"].get("path", "")).replace("\\", "/").lower()
                if not names or any(p.endswith(n.lower()) for n in names):
                    last_write = i
        if last_write < 0:
            return False
        return any(e["name"] == "run_command" and not str(e.get("result", "")).startswith("Kullanıcı")
                   for e in self.events[last_write + 1:])


@dataclass
class Task:
    id: str
    category: str
    title: str
    level: int
    prompt: str
    grade: Callable[[Path, str, Trace], Rubric]
    tools: bool = True
    setup: Callable[[Path], None] = lambda d: None
    reference: Callable[[Path], str] | None = None  # doğru çözümü klasöre uygular; son cevap metnini döndürür
    wrong: Callable[[Path], str] | None = None  # öz-sınama: kısmen yanlış bir çözüm (ara puan beklenir)

    @property
    def weight(self) -> float:
        return LEVEL_WEIGHT[self.level]


TASKS: list[Task] = []


def task(**kwargs) -> Task:
    t = Task(**kwargs)
    assert t.category in CATEGORIES, t.category
    assert t.id not in {x.id for x in TASKS}, t.id
    TASKS.append(t)
    return t


# ---------------------------------------------------------------- dosya yardımcıları

def code(s: str) -> str:
    return textwrap.dedent(s).strip("\n")


def write(path: Path, text: str, newline: str = "\n", bom: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = text.replace("\r\n", "\n").replace("\n", newline).encode("utf-8")
    path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)


def read(path: Path) -> str:
    try:
        data = path.read_bytes()
    except OSError:
        return ""
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):  # Windows PowerShell 5'in Out-File / > varsayılanı UTF-16
        return data.decode("utf-16", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


CODE_BLOCK = re.compile(r"```[ \t]*([\w+#.-]*)[^\n]*\n(.*?)```", re.S)


def code_blocks(answer: str) -> list[tuple[str, str]]:
    return [(tag.lower(), body) for tag, body in CODE_BLOCK.findall(answer or "")]


def locate(d: Path, name: str) -> tuple[Path | None, float, str]:
    """İstenen çıktı dosyası: önce görev klasöründe, yoksa alt klasörlerde ("bu klasörde" bazen alt klasör diye
    anlaşılıyor; yanlış yer küçük bir cezayla kabul edilir)."""
    p = d / name
    if p.is_file():
        return p, 1.0, ""
    hits = sorted((q for q in d.rglob(name) if q.is_file() and "__pycache__" not in q.parts), key=lambda q: len(q.parts))
    if hits:
        return hits[0], 0.9, f"{name} alt klasöre yazılmış: {hits[0].relative_to(d).as_posix()}"
    return None, 0.0, f"{name} yok"


def find_source(d: Path, filename: str, defines: str, answer: str) -> tuple[str, float, str]:
    """Çözümün kaynağını bulur: (kod, çarpan, not). İstenen dosya yoksa klasördeki başka bir dosyada ya da
    cevaptaki kod bloğunda tanımı arar ve ceza çarpanı uygular (yanlış yere kaydetmek sıfır demek değildir)."""
    target, factor, note = locate(d, filename)
    if target:
        return read(target), factor, note
    ext = Path(filename).suffix
    for p in sorted(d.rglob(f"*{ext}")):
        if "__pycache__" in p.parts or p.name.startswith(("_bench", "test")):
            continue
        text = read(p)
        if re.search(defines, text, re.M):
            return text, 0.75, f"dosya adı yanlış: {p.relative_to(d).as_posix()}"
    blocks = [b for _, b in code_blocks(answer)]
    # Model aracı çağırmak yerine "write_file(path=..., content='''...''')" yazdıysa içeriği o bloktan çıkar.
    blocks += [m.group(2) for b in blocks for m in re.finditer(r"content\s*=\s*('''|\"\"\")(.*?)\1", b, re.S)]
    blocks = [b for b in blocks if re.search(defines, b, re.M)]

    def usable(b: str) -> bool:
        if re.search(r"^\s*(write_file|edit_file|run_command)\s*\(", b, re.M):
            return False
        if ext == ".py":
            try:
                compile(b, "<cevap>", "exec")
            except (SyntaxError, ValueError):
                return False
        return True

    if blocks:
        return max(blocks, key=lambda b: (usable(b), len(b))), 0.6, "dosyaya kaydedilmemiş; cevaptaki kod kullanıldı"
    return "", 0.0, f"{filename} yok"


# ---------------------------------------------------------------- gizli test koşucuları

def _env() -> dict:
    return dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")


MARK = "@@GB2@@"  # sonuç satırı öneki (çözümün kendi çıktısıyla karışmasın)
PY_HARNESS = r'''
import json, sys
sys.setrecursionlimit(5000)
START = int(sys.argv[1])
TESTS = json.load(open("_tests.json", encoding="utf-8"))
ns = {}
try:
    import importlib
    ns["M"] = importlib.import_module(MODULE)
    exec(open("_prelude.py", encoding="utf-8").read(), ns)
except BaseException as e:
    print(json.dumps({"import_error": repr(e)[:300]}), flush=True)
    sys.exit(0)
for i in range(START, len(TESTS)):
    try:
        ok, err = bool(eval(TESTS[i], ns)), None
    except BaseException as e:
        ok, err = False, repr(e)[:160]
    print("@@GB2@@" + json.dumps({"i": i, "ok": ok, "err": err}), flush=True)
'''

JS_HARNESS = r'''
process.on("unhandledRejection", () => {});
const START = Number(process.argv[2]);
const TESTS = __TESTS__;
let M;
try { M = require(__MODULE__); } catch (e) {
  console.log(JSON.stringify({ import_error: String(e).slice(0, 300) })); process.exit(0);
}
__PRELUDE__
(async () => {
  for (let i = START; i < TESTS.length; i++) {
    let ok = false, err = null;
    try { ok = !!(await eval(TESTS[i])); } catch (e) { err = String(e).slice(0, 160); }
    process.stdout.write("@@GB2@@" + JSON.stringify({ i, ok, err }) + "\n");
  }
})();
'''


def _run(cmd: list[str], cwd: Path, timeout: float) -> tuple[str, str, bool]:
    p = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace", env=_env())
    try:
        out, err = p.communicate(timeout=timeout)
        return out, err, False
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else:
            p.kill()
        out, err = p.communicate()
        return out, err, True


def run_tests(lang: str, files: dict[str, str], module: str, tests: list[tuple[float, str] | tuple[float, str, str]],
              prelude: str = "", timeout: float = 20) -> tuple[list[Item], str]:
    """Gizli testleri ayrı bir süreçte çalıştırır. tests: (ağırlık, ifade[, ad]). Bir test takılırsa (sonsuz döngü)
    yalnızca o test başarısız sayılır, kalanlar kaldığı yerden yeniden çalıştırılır. (maddeler, hata özeti)"""
    exprs = [t[1] for t in tests]
    results: dict[int, tuple[bool, str | None]] = {}
    fatal = ""
    with tempfile.TemporaryDirectory(prefix="gb2_", ignore_cleanup_errors=True) as tmp:
        d = Path(tmp)
        for name, text in files.items():
            write(d / name, text)
        if lang == "py":
            write(d / "_tests.json", json.dumps(exprs, ensure_ascii=False))
            write(d / "_prelude.py", prelude)
            write(d / "_harness.py", PY_HARNESS.replace("MODULE", repr(module)))
            base = [sys.executable, "_harness.py"]
        else:
            js = (JS_HARNESS.replace("__TESTS__", json.dumps(exprs, ensure_ascii=False))
                  .replace("__MODULE__", json.dumps("./" + module)).replace("__PRELUDE__", prelude))
            write(d / "_harness.js", js)
            base = [shutil.which("node") or "node", "_harness.js"]
        start, rounds = 0, 0
        while start < len(exprs) and rounds < 6:
            rounds += 1
            out, err, timed_out = _run(base + [str(start)], d, timeout)
            got = 0
            for line in out.splitlines():
                if line.startswith(MARK):
                    r = json.loads(line[len(MARK):])
                    results[r["i"]] = (r["ok"], r["err"])
                    got = max(got, r["i"] + 1)
                elif line.startswith('{"import_error"'):
                    fatal = json.loads(line)["import_error"]
            if fatal:
                break
            if got >= len(exprs):
                break
            nxt = max(got, start)
            if nxt < len(exprs):
                results[nxt] = (False, "zaman aşımı" if timed_out else ("süreç çöktü: " + (err or "")[-120:]))
            start = nxt + 1
    items, errors = [], []
    for i, t in enumerate(tests):
        ok, e = results.get(i, (False, fatal or "çalışmadı"))
        name = t[2] if len(t) > 2 else t[1]
        items.append(Item(name[:90], t[0], 1.0 if ok else 0.0))
        if not ok and len(errors) < 4:
            errors.append(f"{name[:70]}" + (f" -> {e}" if e else ""))
    summary = ("içe aktarma hatası: " + fatal[:200]) if fatal else "; ".join(errors)
    return items, summary


def danger(code_text: str, lang: str = "py") -> str | None:
    if lang == "py":
        return grading.python_danger(code_text)
    m = grading.DANGEROUS_JS.search(code_text)
    return f"güvenlik filtresi: {m.group(0)}" if m else None


def grade_code(d: Path, answer: str, trace: Trace, *, lang: str, filename: str, defines: str,
               tests: list, prelude: str = "", forbid: str = "", verify_weight: float = 0.6,
               extra_files: dict[str, str] | None = None, timeout: float = 20) -> Rubric:
    """Kod yazma görevlerinin ortak notlandırması: gizli testler + kendi kendini doğrulama maddesi."""
    r = Rubric()
    src, factor, note = find_source(d, filename, defines, answer)
    if note and factor > 0:
        r.gate(note, factor)
    if not src.strip():
        for w, expr, *name in tests:
            r.add((name[0] if name else expr)[:90], w, 0)
        r.add("kodu kendisi doğruladı", verify_weight, 0)
        r.gate(f"{filename} yok", 0.0)
        return r
    if forbid and (m := re.search(forbid, src, re.M)):
        r.gate(f"yasak yapı: {m.group(0).strip()}", 0.3)
    if reason := danger(src, lang):
        r.gate(reason, 0.0)
        r.add("güvenlik", 1, 0)
        return r
    module = Path(filename).stem if lang == "py" else filename
    items, summary = run_tests(lang, {filename: src, **(extra_files or {})}, module, tests, prelude, timeout)
    r.extend(items)
    r.add("kodu kendisi doğruladı", verify_weight, trace.verified_after_write(filename) if factor == 1.0 else False)
    r.note(f"hatalar: {summary[:250]}" if summary else "")
    return r


# ---------------------------------------------------------------- metin cevapları

def normalize_lines(text: str) -> list[str]:
    lines = [ln.rstrip() for ln in (text or "").replace("\r\n", "\n").split("\n")]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def _tokens(s: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", s)


def output_similarity(got: str, want: str) -> tuple[float, str]:
    """Beklenen çıktıyla satır satır karşılaştırma. Birebir aynı satır 1, kısmen benzeyen satır en fazla 0,4
    (simge düzeyinde benzerlikle) puan alır; eksik/fazla satırlar 0. Puan = toplam / max(satır sayıları)."""
    w, g = normalize_lines(want), normalize_lines(got)
    if not g:
        return 0.0, "cevap boş"
    if w == g:
        return 1.0, "birebir doğru"
    sm = difflib.SequenceMatcher(a=w, b=g, autojunk=False)
    total = 0.0
    wrong = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            total += i2 - i1
        elif op == "replace":
            for k in range(min(i2 - i1, j2 - j1)):
                a, b = w[i1 + k], g[j1 + k]
                total += 0.4 * difflib.SequenceMatcher(a=_tokens(a), b=_tokens(b), autojunk=False).ratio()
                wrong.append(f"{i1 + k + 1}. satır: beklenen {a!r}, cevap {b!r}")
            for k in range(min(i2 - i1, j2 - j1), i2 - i1):
                wrong.append(f"{i1 + k + 1}. satır eksik: {w[i1 + k]!r}")
        elif op == "delete":
            wrong += [f"{k + 1}. satır eksik: {w[k]!r}" for k in range(i1, i2)]
        else:
            wrong.append(f"fazla satır: {g[j1]!r}")
    return total / max(len(w), len(g)), "; ".join(wrong)[:400]


def extract_text_answer(answer: str) -> str:
    blocks = code_blocks(answer)
    texty = [b for tag, b in blocks if tag in ("text", "txt", "plaintext", "output", "console", "")]
    if texty:
        return texty[-1]
    if blocks:
        return blocks[-1][1]
    return answer or ""


def extract_json(answer: str):
    """Cevaptaki JSON'u bulur: önce ```json bloğu, sonra herhangi bir blok, sonra metindeki ilk { ... } / [ ... ]."""
    candidates = [b for tag, b in code_blocks(answer) if tag in ("json", "")] + [b for _, b in code_blocks(answer)]
    candidates.append(answer or "")
    for c in candidates:
        c = c.strip()
        try:
            return json.loads(c)
        except ValueError:
            pass
        for open_, close in (("{", "}"), ("[", "]")):
            i, j = c.find(open_), c.rfind(close)
            if 0 <= i < j:
                chunk = c[i:j + 1]
                for attempt in (chunk, re.sub(r",\s*([}\]])", r"\1", chunk)):
                    try:
                        return json.loads(attempt)
                    except ValueError:
                        continue
    return None


def to_number(value) -> float | None:
    """'5/12', '%41,67', '0,4167', '34.650', 34650 gibi biçimleri sayıya çevirir."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):
        return None
    s = value.strip().replace(" ", "").replace(" ", "")
    pct = s.startswith("%") or s.endswith("%")
    s = s.strip("%")
    if m := re.fullmatch(r"(-?\d+)\s*/\s*(\d+)", s):
        return int(m.group(1)) / int(m.group(2)) if int(m.group(2)) else None
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):  # 34.650 → 34650
        s = s.replace(".", "")
    s = s.replace(",", ".")
    try:
        v = float(s)
    except ValueError:
        return None
    return v / 100 if pct else v


def number_credit(got, want: float, rel: float = 1e-3, near: float = 0.02) -> float:
    """Tam (göreli hata ≤ rel) 1, yakın (≤ near) 0,5, değilse 0."""
    v = to_number(got)
    if v is None:
        return 0.0
    err = abs(v - want) / max(abs(want), 1e-12)
    if err <= rel or abs(v - want) < 1e-9:
        return 1.0
    return 0.5 if err <= near else 0.0
