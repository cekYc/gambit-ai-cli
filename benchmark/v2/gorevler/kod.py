"""Kod yazma: model çözümü istenen dosyaya yazar (gambit'in write_file aracıyla), gizli testlerle puanlanır.
Testlerin ağırlıkları farklıdır: temel davranış az, zor kenar durumları çok puan getirir."""

from pathlib import Path

from core import code, grade_code, task, write

PY_NOTE = ("Fonksiyon(lar)ı `{f}` dosyasına yaz (bu klasörde). Sadece standart kütüphaneyi kullan. "
           "Çözümün gizli testlerle (kenar durumları dahil) puanlanacak.")
JS_NOTE = ("Kodu `{f}` dosyasına yaz (bu klasörde, Node.js CommonJS: `module.exports`). Harici paket kullanma. "
           "Çözümün gizli testlerle (kenar durumları dahil) puanlanacak.")

RAISES_PY = code("""
    def raises(exc, f, *a, **k):
        try:
            f(*a, **k)
        except exc:
            return True
        except BaseException:
            return False
        return False
""")


def _ref(filename: str, text: str):
    def apply(d: Path) -> str:
        write(d / filename, text)
        return f"{filename} yazıldı ve doğrulandı."
    return apply


# ---------------------------------------------------------------- semver

SEMVER_REF = code(r'''
    import re

    _RX = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
                     r"(?:-((?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\.(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*))?"
                     r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$")


    def _key(v):
        m = _RX.match(v) if isinstance(v, str) else None
        if not m:
            raise ValueError(v)
        core = tuple(int(x) for x in m.group(1, 2, 3))
        pre = m.group(4)
        if pre is None:
            return core, 1, ()
        ids = tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre.split("."))
        return core, 0, ids


    def compare(a, b):
        ka, kb = _key(a), _key(b)
        return (ka > kb) - (ka < kb)


    def sort_versions(versions):
        return sorted(versions, key=_key)
''')
SEMVER_ORDER = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta", "1.0.0-beta.2", "1.0.0-beta.11",
                "1.0.0-rc.1", "1.0.0"]

task(
    id="kod-semver", category="Kod yazma", title="SemVer 2.0 karşılaştırma", level=3,
    prompt=code("""
        Python'da Semantic Versioning 2.0.0 kurallarına uyan iki fonksiyon yaz:
        - `compare(a: str, b: str) -> int`: a < b ise -1, eşit öncelikteyse 0, a > b ise 1.
        - `sort_versions(versions: list[str]) -> list[str]`: önceliğe göre artan sıralı yeni liste. Eşit öncelikli
          sürümler girdideki sıralarını korusun.
        Kurallar: MAJOR.MINOR.PATCH sayısaldır ve baştaki sıfıra izin verilmez (0 hariç). İsteğe bağlı ön sürüm
        (`-alpha.1`) ve derleme bilgisi (`+build.5`) olabilir; derleme bilgisi önceliği etkilemez. Başta isteğe
        bağlı tek bir `v` olabilir (`v1.2.3`). Ön sürüm kimlikleri SemVer'deki gibi karşılaştırılır. Geçersiz
        bir sürüm metninde (her iki fonksiyonda da) ValueError fırlat.
    """) + "\n" + PY_NOTE.format(f="semver.py"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="py", filename="semver.py", defines=r"^\s*def\s+compare\b", prelude=RAISES_PY, tests=[
            (1, 'M.compare("1.0.0", "2.0.0") == -1'),
            (1, 'M.compare("2.1.0", "2.0.9") == 1'),
            (2, 'M.compare("1.10.0", "1.9.0") == 1', "sayısal karşılaştırma (1.10 > 1.9)"),
            (0.5, 'M.compare("1.2.3", "1.2.3") == 0'),
            (2, 'M.compare("1.0.0-alpha", "1.0.0") == -1', "ön sürüm < normal sürüm"),
            (3, f'M.sort_versions({list(reversed(SEMVER_ORDER))!r}) == {SEMVER_ORDER!r}', "SemVer örnek sıralaması"),
            (1, 'M.compare("1.0.0-2", "1.0.0-10") == -1', "sayısal ön sürüm kimliği"),
            (1, 'M.compare("1.0.0-alpha", "1.0.0-1") == 1', "sayısal kimlik < alfanümerik"),
            (1, 'M.compare("1.0.0-alpha.1", "1.0.0-alpha.1.0") == -1', "kısa kimlik kümesi önce"),
            (1, 'M.compare("1.0.0+build.1", "1.0.0+build.2") == 0', "derleme bilgisi yok sayılır"),
            (0.5, 'M.compare("1.0.0-rc.1+x.7", "1.0.0-rc.1") == 0'),
            (0.5, 'M.compare("v1.2.3", "1.2.3") == 0', "v öneki"),
            (0.5, 'M.compare("1.0.0-x-y-z.1", "1.0.0-x-y-z.2") == -1', "kimlikte tire"),
            (1, 'M.sort_versions(["1.0.0+b", "0.9.0", "1.0.0+a"]) == ["0.9.0", "1.0.0+b", "1.0.0+a"]', "kararlı sıralama"),
            (0.5, 'raises(ValueError, M.compare, "1.2", "1.2.0")'),
            (0.5, 'raises(ValueError, M.compare, "1.02.3", "1.2.3")', "baştaki sıfır geçersiz"),
            (0.5, 'raises(ValueError, M.compare, "1.2.3-", "1.2.3")'),
            (0.5, 'raises(ValueError, M.compare, "1.2.3-01", "1.2.3")', "ön sürümde baştaki sıfır geçersiz"),
            (0.5, 'raises(ValueError, M.compare, "1.2.3-alpha..1", "1.2.3")'),
            (0.5, 'raises(ValueError, M.sort_versions, ["1.0.0", "a.b.c"])'),
            (0.5, 'raises(ValueError, M.compare, "1.2.3+", "1.2.3")'),
        ]),
    reference=_ref("semver.py", SEMVER_REF),
    wrong=_ref("semver.py", code('''
        def _key(v):
            v = v.lstrip("v").split("+")[0]
            core, _, pre = v.partition("-")
            return tuple(int(x) for x in core.split(".")), pre == "", pre

        def compare(a, b):
            ka, kb = _key(a), _key(b)
            return (ka > kb) - (ka < kb)

        def sort_versions(versions):
            return sorted(versions, key=_key)
    ''')),
)

# ---------------------------------------------------------------- mini dil yorumlayıcı

CALC_REF = code(r'''
    import re

    _TOKEN = re.compile(r"\s*(?:(\d+\.\d+|\d+)|([A-Za-z_]\w*)|(\*\*|[-+*/%(),=]))")
    _FUNCS = {"min": min, "max": max, "abs": abs}


    def _tokens(src):
        pos, out = 0, []
        src = src.rstrip()
        while pos < len(src):
            m = _TOKEN.match(src, pos)
            if not m or m.end() == pos:
                raise SyntaxError(f"beklenmeyen karakter: {src[pos:pos + 1]!r}")
            num, name, op = m.groups()
            if num is not None:
                out.append(("num", float(num) if "." in num else int(num)))
            elif name is not None:
                out.append(("name", name))
            else:
                out.append(("op", op))
            pos = m.end()
            while pos < len(src) and src[pos].isspace():
                pos += 1
        return out


    class _P:
        def __init__(self, toks, env):
            self.t, self.i, self.env = toks, 0, env

        def peek(self, k=0):
            return self.t[self.i + k] if self.i + k < len(self.t) else (None, None)

        def take(self, val=None):
            tok = self.peek()
            if tok[0] is None or (val is not None and tok != ("op", val)):
                raise SyntaxError(f"beklenen {val!r}, bulunan {tok[1]!r}")
            self.i += 1
            return tok

        def expr(self):
            v = self.term()
            while self.peek() in (("op", "+"), ("op", "-")):
                v = v + self.term() if self.take()[1] == "+" else v - self.term()
            return v

        def term(self):
            v = self.unary()
            while self.peek() in (("op", "*"), ("op", "/"), ("op", "%")):
                op = self.take()[1]
                r = self.unary()
                v = v * r if op == "*" else (v / r if op == "/" else v % r)
            return v

        def unary(self):
            if self.peek() == ("op", "-"):
                self.take()
                return -self.unary()
            if self.peek() == ("op", "+"):
                self.take()
                return +self.unary()
            return self.power()

        def power(self):
            base = self.atom()
            if self.peek() == ("op", "**"):
                self.take()
                return base ** self.unary()
            return base

        def atom(self):
            kind, val = self.take()
            if kind == "num":
                return val
            if kind == "name":
                if self.peek() == ("op", "("):
                    self.take("(")
                    args = [self.expr()]
                    while self.peek() == ("op", ","):
                        self.take(",")
                        args.append(self.expr())
                    self.take(")")
                    if val not in _FUNCS:
                        raise NameError(val)
                    return _FUNCS[val](*args) if val != "abs" else abs(*args)
                if val not in self.env:
                    raise NameError(val)
                return self.env[val]
            if (kind, val) == ("op", "("):
                v = self.expr()
                self.take(")")
                return v
            raise SyntaxError(f"beklenmeyen {val!r}")


    def calistir(program):
        env, result = {}, None
        for line in program.split("\n"):
            line = line.split("#", 1)[0]
            for stmt in line.split(";"):
                if not stmt.strip():
                    continue
                toks = _tokens(stmt)
                target = None
                if len(toks) >= 2 and toks[0][0] == "name" and toks[1] == ("op", "="):
                    target, toks = toks[0][1], toks[2:]
                p = _P(toks, env)
                value = p.expr()
                if p.i != len(toks):
                    raise SyntaxError("fazla simge")
                if target is not None:
                    env[target] = value
                result = value
        return result
''')

task(
    id="kod-yorumlayici", category="Kod yazma", title="Mini dil yorumlayıcısı", level=4,
    prompt=code("""
        Python'da `calistir(program: str)` fonksiyonunu yaz: küçük bir hesap dilini yorumlasın ve son ifadenin
        değerini döndürsün. `eval`, `exec`, `compile` ve `ast` kullanmak YASAK.
        Dil:
        - İfadeler satır sonu ya da `;` ile ayrılır; boş ifadeler yok sayılır. `#` satırın kalanını yorum yapar.
        - Atama: `ad = ifade` (ad harf ya da _ ile başlar). Atamanın değeri atanan değerdir.
        - Sayılar: tam sayı (`42`) ya da ondalıklı (`3.5`). Aritmetik sonuçları Python'daki gibidir
          (int * int int kalır, `/` her zaman float).
        - İşleçler, öncelik düşükten yükseğe: `+ -`, `* / %`, tekli `-`/`+`, `**`. `**` sağdan birleşir ve solundaki
          tekli eksiden önce uygulanır (Python'daki gibi: `-2 ** 2` = -4, `2 ** -1` = 0.5). Parantez kullanılabilir.
        - Fonksiyonlar: `min(...)`, `max(...)` (bir ya da daha çok argüman), `abs(x)`.
        - Dönüş: son çalıştırılan ifadenin (ya da atamanın) değeri; hiç ifade yoksa None.
        - Hatalar: tanımsız değişken ya da bilinmeyen fonksiyon → NameError; sıfıra bölme → ZeroDivisionError;
          söz dizimi hatası (ör. `2 +`, `(1`, `3 4`, `2 $ 3`) → SyntaxError.
    """) + "\n" + PY_NOTE.format(f="hesap.py"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="py", filename="hesap.py", defines=r"^\s*def\s+calistir\b", prelude=RAISES_PY,
        forbid=r"(?<![.\w])(?:eval|exec|compile)\s*\(|^\s*(?:import|from)\s+ast\b", tests=[
            (1, 'M.calistir("1 + 2 * 3") == 7'),
            (0.5, 'M.calistir("(1 + 2) * 3") == 9'),
            (0.5, 'M.calistir("10 - 2 - 3") == 5', "soldan birleşme"),
            (1.5, 'M.calistir("2 ** 3 ** 2") == 512', "** sağdan birleşir"),
            (1.5, 'M.calistir("-2 ** 2") == -4', "tekli eksi ve **"),
            (1, 'M.calistir("2 ** -1") == 0.5'),
            (1, 'M.calistir("7 % 3 + 10 / 4") == 3.5'),
            (1, 'M.calistir("1 - - 1") == 2', "art arda tekli eksi"),
            (1, 'M.calistir("2 * (3 + 4) ** 2 / 7") == 14.0'),
            (0.5, 'type(M.calistir("6 / 3")) is float and type(M.calistir("6 * 3")) is int', "int/float türleri"),
            (1.5, 'M.calistir("x = 4; y = x * 2\\ny - 1") == 7', "değişkenler"),
            (1.5, 'M.calistir("a = 3\\nb = a ** 2 # kare\\nmin(a, b, 2) + max(1, b) + abs(-a)") == 14', "fonksiyon ve yorum"),
            (0.5, 'M.calistir("x = 5") == 5', "atamanın değeri"),
            (0.5, 'M.calistir("") is None and M.calistir("  ;  # yalnız yorum") is None', "boş program"),
            (0.5, 'M.calistir(" ; ; 3 ; ") == 3'),
            (0.5, 'M.calistir("max(1.5, 2) * 2") == 4'),
            (1, 'raises(NameError, M.calistir, "y + 1")', "tanımsız değişken"),
            (0.5, 'raises(NameError, M.calistir, "foo(1)")', "bilinmeyen fonksiyon"),
            (0.5, 'raises(ZeroDivisionError, M.calistir, "1 / 0")'),
            (0.5, 'raises(SyntaxError, M.calistir, "2 +")'),
            (0.5, 'raises(SyntaxError, M.calistir, "(1 + 2")'),
            (0.5, 'raises(SyntaxError, M.calistir, "3 4")'),
            (0.5, 'raises(SyntaxError, M.calistir, "2 $ 3")'),
        ]),
    reference=_ref("hesap.py", CALC_REF),
    wrong=_ref("hesap.py", CALC_REF.replace("return base ** self.unary()", "return base ** self.atom()")
               .replace('if self.peek() == ("op", "-"):\n            self.take()\n            return -self.unary()',
                        'if self.peek() == ("op", "-"):\n            self.take()\n            return -self.power()')
               .replace("raise NameError(val)\n                return self.env[val]", "return self.env.get(val, 0)")),
)

# ---------------------------------------------------------------- CSV ayrıştırıcı

CSV_REF = code(r'''
    def parse_csv(text, delimiter=","):
        rows, row, field = [], [], []
        i, n = 0, len(text)
        if n == 0:
            return []
        quoted = False
        while i < n:
            c = text[i]
            if quoted:
                if c == '"':
                    if i + 1 < n and text[i + 1] == '"':
                        field.append('"')
                        i += 2
                        continue
                    quoted = False
                    i += 1
                    if i < n and text[i] not in (delimiter, "\n", "\r"):
                        raise ValueError("tırnaktan sonra beklenmeyen karakter")
                    continue
                field.append(c)
                i += 1
                continue
            if c == '"' and not field:
                quoted = True
                field = []
                i += 1
                continue
            if c == delimiter:
                row.append("".join(field))
                field = []
                i += 1
                continue
            if c in "\r\n":
                row.append("".join(field))
                rows.append(row)
                row, field = [], []
                i += 2 if c == "\r" and i + 1 < n and text[i + 1] == "\n" else 1
                continue
            field.append(c)
            i += 1
        if quoted:
            raise ValueError("kapanmamış tırnak")
        if field or row or (text and text[-1] not in "\r\n"):
            row.append("".join(field))
            rows.append(row)
        return rows
''')

task(
    id="kod-csv", category="Kod yazma", title="CSV ayrıştırıcı (RFC 4180)", level=3,
    prompt=code("""
        Python'da `parse_csv(text: str, delimiter: str = ",") -> list[list[str]]` fonksiyonunu yaz.
        `csv` modülünü KULLANMA. Kurallar:
        - Kayıtlar `\\n` ya da `\\r\\n` ile ayrılır. Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz;
          boş metin `[]` döndürür. Ortadaki boş bir satır tek boş alanlı kayıttır: `[""]`.
        - Çift tırnakla başlayan bir alan ayırıcı, satır sonu ve `""` (tek `"` olarak) içerebilir; tırnaklar alana
          dahil değildir.
        - Tırnaksız alanlar olduğu gibi alınır (boşluklar korunur); tırnaksız alanın ortasındaki `"` sıradan karakterdir.
        - Hatalı girdide ValueError fırlat: kapanan tırnaktan hemen sonra ayırıcı/satır sonu dışında bir karakter
          (ör. `"ab"c`) ya da hiç kapanmayan tırnak.
    """) + "\n" + PY_NOTE.format(f="csvparse.py"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="py", filename="csvparse.py", defines=r"^\s*def\s+parse_csv\b", prelude=RAISES_PY,
        forbid=r"^\s*(?:import\s+csv|from\s+csv\s+import)\b", tests=[
            (1, 'M.parse_csv("a,b,c\\n1,2,3\\n") == [["a", "b", "c"], ["1", "2", "3"]]'),
            (0.5, 'M.parse_csv("a,b") == [["a", "b"]]', "sonda satır sonu yok"),
            (0.5, 'M.parse_csv("") == []'),
            (1, 'M.parse_csv("x,,y,\\n") == [["x", "", "y", ""]]', "boş alanlar"),
            (1.5, 'M.parse_csv(\'"a,b",c\\n\') == [["a,b", "c"]]', "tırnak içinde ayırıcı"),
            (1.5, 'M.parse_csv(\'"say ""merhaba""",2\') == [[\'say "merhaba"\', "2"]]', "kaçışlı tırnak"),
            (2, 'M.parse_csv(\'"satır1\\nsatır2",x\\ny,z\') == [["satır1\\nsatır2", "x"], ["y", "z"]]', "tırnak içinde satır sonu"),
            (1, 'M.parse_csv("a,b\\r\\nc,d\\r\\n") == [["a", "b"], ["c", "d"]]', "CRLF"),
            (1, 'M.parse_csv("a\\n\\nb\\n") == [["a"], [""], ["b"]]', "ortadaki boş satır"),
            (0.5, 'M.parse_csv(" a , b ") == [[" a ", " b "]]', "boşluklar korunur"),
            (0.5, 'M.parse_csv(\'ab"c,d\') == [[\'ab"c\', "d"]]', "tırnaksız alanda tırnak"),
            (1, 'M.parse_csv(\'a;"b;c";d\', delimiter=";") == [["a", "b;c", "d"]]', "farklı ayırıcı"),
            (0.5, 'M.parse_csv(\'"",""\') == [["", ""]]', "boş tırnaklı alanlar"),
            (1, 'raises(ValueError, M.parse_csv, \'"ab"c,d\')', "tırnaktan sonra karakter"),
            (1, 'raises(ValueError, M.parse_csv, \'a,"bc\')', "kapanmayan tırnak"),
            (1, 'len(M.parse_csv("a,b\\n" * 20000)) == 20000', "büyük girdi"),
        ]),
    reference=_ref("csvparse.py", CSV_REF),
    wrong=_ref("csvparse.py", code('''
        def parse_csv(text, delimiter=","):
            if not text:
                return []
            out = []
            for line in text.splitlines():
                out.append([f.strip('"') for f in line.split(delimiter)])
            return out
    ''')),
)

# ---------------------------------------------------------------- bağımlılık sırası

TOPO_REF = code(r'''
    import heapq


    class DonguHatasi(ValueError):
        def __init__(self, dongu):
            super().__init__(" -> ".join(dongu))
            self.dongu = dongu


    def _find_cycle(graph, nodes):
        color = {n: 0 for n in nodes}
        stack = []

        def dfs(u):
            color[u] = 1
            stack.append(u)
            for v in sorted(graph.get(u, ())):
                if color[v] == 1:
                    return stack[stack.index(v):]
                if color[v] == 0:
                    found = dfs(v)
                    if found:
                        return found
            stack.pop()
            color[u] = 2
            return None

        for n in sorted(nodes):
            if color[n] == 0:
                c = dfs(n)
                if c:
                    k = c.index(min(c))
                    return c[k:] + c[:k]
        return None


    def kurulum_sirasi(deps):
        graph = {k: set(v) for k, v in deps.items()}
        nodes = set(graph)
        for v in graph.values():
            nodes |= v
        indeg = {n: 0 for n in nodes}
        users = {n: [] for n in nodes}
        for pkg, ds in graph.items():
            for dep in ds:
                indeg[pkg] += 1
                users[dep].append(pkg)
        heap = [n for n in nodes if indeg[n] == 0]
        heapq.heapify(heap)
        order = []
        while heap:
            n = heapq.heappop(heap)
            order.append(n)
            for u in users[n]:
                indeg[u] -= 1
                if indeg[u] == 0:
                    heapq.heappush(heap, u)
        if len(order) != len(nodes):
            rest = {n for n in nodes if n not in set(order)}
            raise DonguHatasi(_find_cycle({k: v & rest for k, v in graph.items() if k in rest}, rest))
        return order
''')
TOPO_PRELUDE = RAISES_PY + "\n" + code('''
    def cycle_of(deps):
        try:
            M.kurulum_sirasi(deps)
        except ValueError as e:
            return getattr(e, "dongu", None)
        return "hata yok"

    def big_chain():
        import time
        n = 6000
        deps = {f"p{i:05d}": [f"p{i + 1:05d}"] for i in range(n)}
        t = time.perf_counter()
        order = M.kurulum_sirasi(deps)
        return order[0] == f"p{n:05d}" and order[-1] == "p00000" and len(order) == n + 1 and time.perf_counter() - t < 3

    def valid(order, deps):
        pos = {p: i for i, p in enumerate(order)}
        return all(pos[d] < pos[p] for p, ds in deps.items() for d in ds)
''')
DIAMOND = {"uygulama": ["web", "veri"], "web": ["cekirdek"], "veri": ["cekirdek", "surucu"], "cekirdek": []}

task(
    id="kod-bagimlilik", category="Kod yazma", title="Bağımlılık sırası ve döngü", level=3,
    prompt=code("""
        Python'da `kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]` fonksiyonunu yaz. `deps` her paketin
        kurulmadan önce kurulması gereken paketlerini verir. Tüm paketleri (yalnızca bağımlılık olarak geçenler
        dahil) her paket kendi bağımlılıklarından sonra gelecek şekilde sırala. O an kurulabilecek birden fazla
        paket varsa alfabetik olarak en küçüğü önce gelsin (sonuç tek ve belirli olmalı). Aynı bağımlılık iki kez
        yazılmış olabilir.
        Döngü varsa `DonguHatasi` fırlat: bunu `ValueError`'dan türeyen bir sınıf olarak aynı dosyada tanımla.
        İstisnanın `dongu` özniteliği döngüyü oluşturan paketlerin listesi olsun: her paket listede kendisinden
        sonraki pakete bağımlıdır, sonuncusu ilkine; liste döngüdeki alfabetik olarak en küçük paketle başlar
        (ör. a→b→c→a ise `["a", "b", "c"]`; kendine bağımlı x için `["x"]`). Binlerce paketle de hızlı çalışmalı.
    """) + "\n" + PY_NOTE.format(f="bagimlilik.py"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="py", filename="bagimlilik.py", defines=r"^\s*def\s+kurulum_sirasi\b", prelude=TOPO_PRELUDE,
        tests=[
            (1, 'M.kurulum_sirasi({"b": ["a"], "c": ["b"]}) == ["a", "b", "c"]'),
            (1, f'valid(M.kurulum_sirasi({DIAMOND!r}), {DIAMOND!r})', "geçerli sıra"),
            (1.5, f'M.kurulum_sirasi({DIAMOND!r}) == ["cekirdek", "surucu", "veri", "web", "uygulama"]', "alfabetik seçim"),
            (1, 'M.kurulum_sirasi({"z": [], "y": [], "x": ["z"]}) == ["y", "z", "x"]', "bağımsız paketler"),
            (1, 'M.kurulum_sirasi({"a": ["x", "x"], "b": []}) == ["b", "x", "a"]', "tekrarlı bağımlılık + yalnız bağımlılık"),
            (0.5, 'M.kurulum_sirasi({}) == []'),
            (1, 'raises(ValueError, M.kurulum_sirasi, {"a": ["b"], "b": ["a"]})', "döngüde ValueError"),
            (1, 'raises(M.DonguHatasi, M.kurulum_sirasi, {"a": ["b"], "b": ["a"]}) and issubclass(M.DonguHatasi, ValueError)',
             "DonguHatasi sınıfı"),
            (1.5, 'cycle_of({"c": ["a"], "a": ["b"], "b": ["c"], "d": ["a"]}) == ["a", "b", "c"]', "dongu listesi"),
            (1, 'cycle_of({"x": ["x"], "y": []}) == ["x"]', "kendine bağımlılık"),
            (1, 'cycle_of({"m": ["n"], "n": ["k"], "k": ["n"], "a": []}) == ["k", "n"]', "döngü en küçükten başlar"),
            (1, "big_chain()", "6000 paketlik zincir < 3 sn"),
        ]),
    reference=_ref("bagimlilik.py", TOPO_REF),
    wrong=_ref("bagimlilik.py", code('''
        class DonguHatasi(ValueError):
            pass

        def kurulum_sirasi(deps):
            order, seen = [], set()
            def visit(p, path=()):
                if p in path:
                    raise DonguHatasi(p)
                if p in seen:
                    return
                for d in deps.get(p, []):
                    visit(d, path + (p,))
                seen.add(p)
                order.append(p)
            for p in deps:
                visit(p)
            return order
    ''')),
)

# ---------------------------------------------------------------- token bucket (JS)

BUCKET_REF = code(r'''
    class TokenBucket {
      constructor({ capacity, refillPerSecond, now = Date.now } = {}) {
        if (typeof capacity !== "number" || !(capacity > 0) || !Number.isFinite(capacity)) throw new RangeError("capacity");
        if (typeof refillPerSecond !== "number" || !(refillPerSecond >= 0) || !Number.isFinite(refillPerSecond))
          throw new RangeError("refillPerSecond");
        this.capacity = capacity;
        this.rate = refillPerSecond;
        this.now = now;
        this.tokens = capacity;
        this.last = now();
      }
      _refill() {
        const t = this.now();
        if (t > this.last) {
          this.tokens = Math.min(this.capacity, this.tokens + ((t - this.last) / 1000) * this.rate);
        }
        if (t > this.last) this.last = t;
      }
      _check(n) {
        if (typeof n !== "number" || !(n > 0) || !Number.isFinite(n)) throw new RangeError("n");
      }
      tryTake(n = 1) {
        this._check(n);
        this._refill();
        if (this.tokens + 1e-9 >= n) {
          this.tokens = Math.max(0, this.tokens - n);
          return true;
        }
        return false;
      }
      available() {
        this._refill();
        return this.tokens;
      }
      msUntil(n = 1) {
        this._check(n);
        if (n > this.capacity) return Infinity;
        this._refill();
        if (this.tokens >= n) return 0;
        if (this.rate === 0) return Infinity;
        return Math.ceil(((n - this.tokens) / this.rate) * 1000);
      }
    }
    module.exports = { TokenBucket };
''')
BUCKET_PRELUDE = code('''
    const { TokenBucket } = M;
    function clock(start = 1000) { const c = { t: start }; c.fn = () => c.t; return c; }
    function throws(f, type) { try { f(); return false; } catch (e) { return !type || e instanceof type; } }
    function near(a, b) { return Math.abs(a - b) < 1e-6; }
''')

task(
    id="kod-kova-js", category="Kod yazma", title="Token bucket hız sınırlayıcı (JS)", level=3,
    prompt=code("""
        JavaScript'te (Node.js) bir `TokenBucket` sınıfı yaz:
        - `new TokenBucket({ capacity, refillPerSecond, now })`: `now` isteğe bağlı, milisaniye döndüren bir
          fonksiyondur (varsayılan `Date.now`); testler sahte saat verir. Kova dolu başlar.
        - Jetonlar zamanla sürekli (kesirli olarak) dolar: geçen her saniye için `refillPerSecond` jeton, en fazla
          `capacity`'ye kadar. Saat geri giderse jeton eklenmez/çıkarılmaz; dolum hesabında o ana kadar görülen
          en büyük zaman referans kalır.
        - `tryTake(n = 1)`: yeterli jeton varsa n jetonu düşer ve true döner; yoksa hiçbir şey düşmeden false.
        - `available()`: o anki jeton sayısı (kesirli olabilir).
        - `msUntil(n = 1)`: n jetonun kullanılabilir olmasına kaç ms kaldığı (yukarı yuvarlanmış tam sayı; şimdi
          yeterliyse 0). n > capacity ya da dolum hızı 0 iken jeton yetmiyorsa `Infinity`.
        - Geçersiz değerlerde `RangeError` fırlat: capacity pozitif sonlu sayı değilse, refillPerSecond negatif ya da
          sayı değilse; tryTake/msUntil için n pozitif sonlu sayı değilse.
        `module.exports = { TokenBucket };` ile dışa aktar.
    """) + "\n" + JS_NOTE.format(f="kova.js"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="js", filename="kova.js", defines=r"class\s+TokenBucket\b", prelude=BUCKET_PRELUDE, tests=[
            (1, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 3, refillPerSecond: 1, now: c.fn }); '
                'return b.tryTake() && b.tryTake() && b.tryTake() && !b.tryTake(); })()', "dolu başlar, boşalır"),
            (1.5, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 2, refillPerSecond: 2, now: c.fn }); '
                  'b.tryTake(2); c.t += 250; return near(b.available(), 0.5); })()', "kesirli dolum"),
            (1, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 5, refillPerSecond: 10, now: c.fn }); '
                'b.tryTake(5); c.t += 10000; return near(b.available(), 5); })()', "kapasitede durur"),
            (1.5, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 4, refillPerSecond: 1, now: c.fn }); '
                  'b.tryTake(3); const r = b.tryTake(2); return r === false && near(b.available(), 1); })()',
             "başarısız tryTake jeton düşmez"),
            (1, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 2, refillPerSecond: 1, now: c.fn }); '
                'b.tryTake(2); c.t -= 5000; const a = b.available(); c.t += 6000; '
                'return near(a, 0) && near(b.available(), 1); })()', "saat geri gidince"),
            (1, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 3, refillPerSecond: 2, now: c.fn }); '
                'b.tryTake(3); return b.msUntil(1) === 500 && b.msUntil(3) === 1500; })()', "msUntil"),
            (0.5, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 3, refillPerSecond: 3, now: c.fn }); '
                  'b.tryTake(2); return b.msUntil(1) === 0; })()', "msUntil 0"),
            (1, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 3, refillPerSecond: 3, now: c.fn }); '
                'b.tryTake(3); c.t += 100; return b.msUntil(1) === 234; })()', "msUntil yukarı yuvarlar"),
            (1, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 2, refillPerSecond: 0, now: c.fn }); '
                'b.tryTake(2); return b.msUntil(5) === Infinity && b.msUntil(1) === Infinity; })()', "Infinity durumları"),
            (0.5, '(() => { const c = clock(); const b = new TokenBucket({ capacity: 2, refillPerSecond: 1, now: c.fn }); '
                  'return b.tryTake(0.5) && near(b.available(), 1.5); })()', "kesirli n"),
            (0.5, 'throws(() => new TokenBucket({ capacity: 0, refillPerSecond: 1 }), RangeError)'),
            (0.5, 'throws(() => new TokenBucket({ capacity: 3, refillPerSecond: -1 }), RangeError)'),
            (0.5, 'throws(() => new TokenBucket({ capacity: "3", refillPerSecond: 1 }), RangeError)'),
            (0.5, 'throws(() => new TokenBucket({ capacity: 3, refillPerSecond: 1 }).tryTake(0), RangeError)'),
            (0.5, 'throws(() => new TokenBucket({ capacity: 3, refillPerSecond: 1 }).msUntil(-2), RangeError)'),
            (0.5, '(() => { const b = new TokenBucket({ capacity: 1, refillPerSecond: 1 }); return b.tryTake() === true; })()',
             "varsayılan saat"),
        ]),
    reference=_ref("kova.js", BUCKET_REF),
    wrong=_ref("kova.js", code('''
        class TokenBucket {
          constructor({ capacity, refillPerSecond, now = Date.now }) {
            this.capacity = capacity; this.rate = refillPerSecond; this.now = now;
            this.tokens = capacity; this.last = now();
          }
          _refill() {
            const t = this.now();
            this.tokens = Math.min(this.capacity, this.tokens + Math.floor((t - this.last) / 1000) * this.rate);
            this.last = t;
          }
          tryTake(n = 1) { this._refill(); this.tokens -= n; return this.tokens >= 0; }
          available() { this._refill(); return this.tokens; }
          msUntil(n = 1) { this._refill(); return this.tokens >= n ? 0 : ((n - this.tokens) / this.rate) * 1000; }
        }
        module.exports = { TokenBucket };
    ''')),
)

# ---------------------------------------------------------------- Türkçe metin

TR_REF = code(r'''
    _ORDER = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
    _RANK = {c: i for i, c in enumerate(_ORDER)}


    def tr_lower(s):
        return s.replace("I", "ı").replace("İ", "i").lower()


    def tr_upper(s):
        return s.replace("i", "İ").replace("ı", "I").upper()


    def _key(word):
        return [(1, _RANK[c]) if c in _RANK else (0, ord(c)) for c in tr_lower(word)]


    def tr_sorted(words):
        return sorted(words, key=_key)
''')

task(
    id="kod-turkce", category="Kod yazma", title="Türkçe harf ve sıralama", level=2,
    prompt=code("""
        Python'da Türkçe metin için üç fonksiyon yaz:
        - `tr_lower(s)` ve `tr_upper(s)`: Türkçe kurallarıyla küçük/büyük harfe çevirsin (I↔ı, İ↔i; diğer harfler
          normal kurallarla).
        - `tr_sorted(words) -> list[str]`: kelimeleri Türk alfabesine göre, büyük/küçük harf farkı gözetmeden
          (Türkçe kurallarla küçültüp) sıralanmış yeni bir liste olarak döndürsün; girdi listesi değişmesin.
          Karakter sırası: `0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz`. Bu listede olmayan karakterler (boşluk,
          noktalama vb.) listedeki tüm karakterlerden önce gelir ve kendi aralarında Unicode kod noktasına göre
          sıralanır. Bir kelime diğerinin önekiyse kısa olan önce gelir. Eşit sayılan kelimeler girdideki sıralarını korur.
    """) + "\n" + PY_NOTE.format(f="trmetin.py"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="py", filename="trmetin.py", defines=r"^\s*def\s+tr_sorted\b", prelude=code('''
            def not_mutated():
                w = ["b", "a"]
                M.tr_sorted(w)
                return w == ["b", "a"]
        '''), tests=[
            (1, 'M.tr_lower("IĞDIR İSTANBUL") == "ığdır istanbul"'),
            (1, 'M.tr_upper("istanbul ılık şiş") == "İSTANBUL ILIK ŞİŞ"'),
            (0.5, 'M.tr_lower("ÇÖĞÜŞ") == "çöğüş" and M.tr_upper("çöğüş") == "ÇÖĞÜŞ"'),
            (1, 'M.tr_sorted(["çay", "cam", "dal", "ceviz"]) == ["cam", "ceviz", "çay", "dal"]', "ç, c'den sonra"),
            (1.5, 'M.tr_sorted(["ilik", "ılık", "ırmak", "iğne"]) == ["ılık", "ırmak", "iğne", "ilik"]', "ı, i'den önce"),
            (2, 'M.tr_sorted(["Zeytin", "armut", "Ilgaz", "İzmir", "ıhlamur"]) == '
                '["armut", "ıhlamur", "Ilgaz", "İzmir", "Zeytin"]', "büyük harfli I/İ"),
            (1, 'M.tr_sorted(["Ali", "ali", "ALİ"]) == ["Ali", "ali", "ALİ"]', "eşitlerde kararlılık"),
            (0.5, 'M.tr_sorted(["kara", "kar", "ka"]) == ["ka", "kar", "kara"]', "önek kuralı"),
            (1, 'M.tr_sorted(["b2", "b10", "b1", " a", "a-b", "ab"]) == [" a", "a-b", "ab", "b1", "b10", "b2"]',
             "rakam ve diğer karakterler"),
            (0.5, 'M.tr_sorted(["xenon", "wifi", "quiz", "pide", "vazo", "yat"]) == '
                  '["pide", "quiz", "vazo", "wifi", "xenon", "yat"]', "q, w, x"),
            (1, 'M.tr_sorted(["şeker", "son", "sabun", "Şahin", "tuz"]) == ["sabun", "son", "Şahin", "şeker", "tuz"]', "ş"),
            (0.5, "not_mutated()"),
        ]),
    reference=_ref("trmetin.py", TR_REF),
    wrong=_ref("trmetin.py", code('''
        def tr_lower(s):
            return s.lower()

        def tr_upper(s):
            return s.upper()

        def tr_sorted(words):
            return sorted(words, key=lambda w: w.lower())
    ''')),
)

# ---------------------------------------------------------------- satır farkı

DIFF_REF = code(r'''
    def _myers(A, B):
        n, m = len(A), len(B)
        v = {1: 0}
        trace = []
        for d in range(n + m + 1):
            trace.append(dict(v))
            for k in range(-d, d + 1, 2):
                if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                    x = v[k + 1]
                else:
                    x = v[k - 1] + 1
                y = x - k
                while x < n and y < m and A[x] == B[y]:
                    x += 1
                    y += 1
                v[k] = x
                if x >= n and y >= m:
                    return trace
        return trace


    def satir_farki(a, b):
        trace = _myers(a, b)
        x, y = len(a), len(b)
        out = []
        for d in range(len(trace) - 1, -1, -1):
            v = trace[d]
            k = x - y
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                pk = k + 1
            else:
                pk = k - 1
            px = v.get(pk, 0)
            py = px - pk
            while x > px and y > py:
                out.append((" ", a[x - 1]))
                x -= 1
                y -= 1
            if d > 0:
                out.append(("+", b[py]) if x == px else ("-", a[px]))
            x, y = px, py
        out.reverse()
        # her değişiklik bloğunda silmeler eklemelerden önce
        res, run = [], []
        for op in out + [None]:
            if op is None or op[0] == " ":
                res += [o for o in run if o[0] == "-"] + [o for o in run if o[0] == "+"]
                run = []
                if op:
                    res.append(op)
            else:
                run.append(op)
        return res
''')
DIFF_PRELUDE = code('''
    def lcs(a, b):
        prev = [0] * (len(b) + 1)
        for x in a:
            cur = [0]
            for j, y in enumerate(b):
                cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
            prev = cur
        return prev[-1]

    def ops(a, b):
        return [tuple(o) for o in M.satir_farki(list(a), list(b))]

    def rebuilds(a, b):
        o = ops(a, b)
        return all(k in (" ", "-", "+") for k, _ in o) and \\
            [x for k, x in o if k != "+"] == list(a) and [x for k, x in o if k != "-"] == list(b)

    def minimal(a, b):
        return rebuilds(a, b) and sum(1 for k, _ in ops(a, b) if k == " ") == lcs(a, b)

    def hunks_ok(a, b):
        o = ops(a, b)
        for x, y in zip(o, o[1:]):
            if x[0] == "+" and y[0] == "-":
                return False
        return rebuilds(a, b)

    A1 = "a b c d e f g".split()
    B1 = "a x c d y f g z".split()
    A2 = "x y z x y z".split()
    B2 = "z y x z y x".split()
    A3 = list("abcabba")
    B3 = list("cbabac")

    def big():
        import time
        a = [f"satır {i}" for i in range(3000)]
        b = list(a)
        b[100] = "değişti"; del b[2000]; b.insert(2500, "yeni")
        t = time.perf_counter()
        o = [tuple(x) for x in M.satir_farki(list(a), list(b))]
        elapsed = time.perf_counter() - t
        return (elapsed < 4 and [x for k, x in o if k != "+"] == a and [x for k, x in o if k != "-"] == b
                and sum(1 for k, _ in o if k == " ") == 2998)
''')

task(
    id="kod-fark", category="Kod yazma", title="Minimal satır farkı (diff)", level=4,
    prompt=code("""
        Python'da `satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]` fonksiyonunu yaz: a satır
        listesini b'ye çeviren minimal bir düzenleme dizisi döndürsün. Her eleman `(" ", satır)` (iki tarafta ortak),
        `("-", satır)` (a'dan silinen) ya da `("+", satır)` (b'ye eklenen) olsun.
        - " " ve "-" olanlar sırayla a'yı, " " ve "+" olanlar sırayla b'yi vermeli.
        - Ortak (" ") satır sayısı mümkün olan en fazla olmalı (en uzun ortak alt dizi).
        - Ardışık değişikliklerde silmeler eklemelerden önce gelsin: bir "+" elemanının hemen ardından "-" gelmesin.
        - Birkaç bin satırlık, az değişiklik içeren listelerde birkaç saniyeden kısa sürede çalışmalı.
    """) + "\n" + PY_NOTE.format(f="fark.py"),
    grade=lambda d, a, t: grade_code(
        d, a, t, lang="py", filename="fark.py", defines=r"^\s*def\s+satir_farki\b", prelude=DIFF_PRELUDE, timeout=40,
        tests=[
            (0.5, 'ops([], []) == []'),
            (0.5, 'ops(["a"], []) == [("-", "a")] and ops([], ["b"]) == [("+", "b")]'),
            (0.5, 'ops(["a", "b"], ["a", "b"]) == [(" ", "a"), (" ", "b")]'),
            (1, "rebuilds(A1, B1)", "a ve b yeniden kurulur (1)"),
            (1.5, "minimal(A1, B1)", "minimal (1)"),
            (1, "rebuilds(A2, B2)", "a ve b yeniden kurulur (2)"),
            (1.5, "minimal(A2, B2)", "minimal (2)"),
            (1.5, "minimal(A3, B3)", "minimal (3)"),
            (1, "hunks_ok(A1, B1) and hunks_ok(A2, B2) and hunks_ok(A3, B3)", "silmeler eklemelerden önce"),
            (1, 'minimal(["x"] * 5, ["x"] * 3) and minimal(list("aaab"), list("baaa"))', "tekrarlı satırlar"),
            (1.5, "big()", "3000 satır < 4 sn"),
        ]),
    reference=_ref("fark.py", DIFF_REF),
    wrong=_ref("fark.py", code('''
        def satir_farki(a, b):
            out = []
            for x in a:
                out.append((" ", x) if x in b else ("-", x))
            for y in b:
                if y not in a:
                    out.append(("+", y))
            return out
    ''')),
)
