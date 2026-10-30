"""Benchmark görevleri.

Her görevin modele giden promptu, notlandırma bilgisi ve notlandırıcıyı sınamak için bir referans
çözümü var (referanslar modellere gösterilmez). Kategoriler radar grafiğinin eksenleridir."""

import hashlib
import json
import re
import sqlite3
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import grading

CATEGORIES = ["Kod yazma", "Hata ayıklama", "Kod okuma", "SQL", "Terminal", "Ajan (araçlar)"]

PY_ONLY = "Sadece Python kodunu tek bir ```python bloğu içinde ver."
JS_ONLY = "Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver."


@dataclass
class Task:
    id: str
    category: str
    kind: str  # python | js | output | sql | shell | agent
    title: str
    prompt: str
    entry: str = ""  # python/js: tanımlanması gereken fonksiyon/sınıf adı (birden fazla kod bloğu varsa seçim için)
    tests: list[str] = field(default_factory=list)  # python/js: doğru dönmesi gereken ifadeler
    prelude: str = ""  # python/js: testlerden önce çalışan yardımcı kod
    forbid: str = ""  # python: çözümde geçerse puan 0 olan yapı (regex)
    reference: str = ""  # python/js/sql/shell: doğru çözüm
    buggy: str = ""  # hata ayıklama: hatalı kod; testlerden tam puan almamalı
    snippet: str = ""  # kod okuma: çıktısı sorulan kod
    lang: str = ""  # kod okuma: python | js
    setup: Callable[[Path], None] | None = None  # shell/agent: çalışma klasörünü hazırlar
    check: Callable[[Path, str], tuple[float, str]] | None = None  # shell/agent: (klasör, çıktı/cevap) -> puan
    apply_reference: Callable[[Path], None] | None = None  # agent: doğru sonucu elle uygular (öz-sınama için)


def code(s: str) -> str:
    return textwrap.dedent(s).strip("\n")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def fraction(checks: dict[str, bool]) -> tuple[float, str]:
    failed = [name for name, ok in checks.items() if not ok]
    score = (len(checks) - len(failed)) / len(checks)
    return score, "tamam" if not failed else "eksik: " + "; ".join(failed)


TASKS: list[Task] = []


def task(**kwargs) -> None:
    TASKS.append(Task(**kwargs))


# ---------------------------------------------------------------- Kod yazma

task(
    id="kod-slug", category="Kod yazma", kind="python", title="Türkçe slug", entry="tr_slug",
    prompt=code("""
        Python'da `tr_slug(text: str) -> str` fonksiyonunu yaz. Metni URL'de kullanılacak kısa ada (slug) çevirsin:
        - Türkçe harfler dönüşsün: ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u; büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü) de aynı şekilde.
        - Sonuç tamamen küçük harf olsun.
        - Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun.
        - Baştaki ve sondaki '-' karakterleri silinsin.
        Örnek: tr_slug("Merhaba Dünya!") == "merhaba-dunya"
    """) + "\n" + PY_ONLY,
    tests=[
        'S.tr_slug("Merhaba Dünya!") == "merhaba-dunya"',
        "S.tr_slug(\"  İstanbul'da Çay Saati  \") == \"istanbul-da-cay-saati\"",
        'S.tr_slug("ŞEKER  --  ĞÜÖ") == "seker-guo"',
        'S.tr_slug("Iğdır ve Ilgın") == "igdir-ve-ilgin"',
        'S.tr_slug("2026 Yılı: %50 İndirim!") == "2026-yili-50-indirim"',
        'S.tr_slug("a__b..c") == "a-b-c"',
        'S.tr_slug("---") == ""',
        'S.tr_slug("") == ""',
    ],
    reference=code('''
        import re

        def tr_slug(text):
            text = text.translate(str.maketrans("çğıöşüÇĞIİÖŞÜ", "cgiosucgiiosu")).lower()
            return re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    '''),
)

task(
    id="kod-roma", category="Kod yazma", kind="python", title="Roma rakamı", entry="int_to_roman",
    prompt=code("""
        Python'da `int_to_roman(n: int) -> str` fonksiyonunu yaz: 1 ile 3999 arasındaki tam sayıyı Roma rakamına
        çevirsin (ör. 1994 → "MCMXCIV"). Bu aralığın dışındaki değerlerde ValueError fırlatsın.
    """) + "\n" + PY_ONLY,
    prelude=code("""
        def raises(f, *args):
            try:
                f(*args)
            except ValueError:
                return True
            except BaseException:
                return False
            return False
    """),
    tests=[
        'S.int_to_roman(1) == "I"', 'S.int_to_roman(4) == "IV"', 'S.int_to_roman(9) == "IX"',
        'S.int_to_roman(14) == "XIV"', 'S.int_to_roman(40) == "XL"', 'S.int_to_roman(90) == "XC"',
        'S.int_to_roman(400) == "CD"', 'S.int_to_roman(1994) == "MCMXCIV"', 'S.int_to_roman(2026) == "MMXXVI"',
        'S.int_to_roman(3999) == "MMMCMXCIX"', "raises(S.int_to_roman, 0)", "raises(S.int_to_roman, 4000)",
    ],
    reference=code('''
        def int_to_roman(n):
            if not 1 <= n <= 3999:
                raise ValueError(n)
            out = ""
            for value, sym in [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
                               (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
                while n >= value:
                    out += sym
                    n -= value
            return out
    '''),
)

task(
    id="kod-aralik", category="Kod yazma", kind="python", title="Aralık birleştirme", entry="merge_intervals",
    prompt=code("""
        Python'da `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` fonksiyonunu yaz. Çakışan ya da
        uç uca değen aralıkları birleştirsin ([1, 3] ve [3, 5] → [1, 5]). Girdi sıralı olmayabilir; sonuç başlangıç
        değerine göre sıralı olsun. Girdi listesi (ve içindeki listeler) değiştirilmesin.
    """) + "\n" + PY_ONLY,
    prelude=code("""
        def norm(result):
            return [list(x) for x in result]

        def not_mutated():
            data = [[5, 7], [1, 3], [2, 4]]
            S.merge_intervals(data)
            return data == [[5, 7], [1, 3], [2, 4]]
    """),
    tests=[
        "norm(S.merge_intervals([])) == []",
        "norm(S.merge_intervals([[1, 3]])) == [[1, 3]]",
        "norm(S.merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])) == [[1, 6], [8, 10], [15, 18]]",
        "norm(S.merge_intervals([[1, 4], [4, 5]])) == [[1, 5]]",
        "norm(S.merge_intervals([[5, 7], [1, 2], [2, 3]])) == [[1, 3], [5, 7]]",
        "norm(S.merge_intervals([[1, 10], [2, 3], [4, 5]])) == [[1, 10]]",
        "norm(S.merge_intervals([[6, 8], [1, 9], [2, 4], [4, 7]])) == [[1, 9]]",
        "not_mutated()",
    ],
    reference=code('''
        def merge_intervals(intervals):
            merged = []
            for start, end in sorted(intervals):
                if merged and start <= merged[-1][1]:
                    merged[-1][1] = max(merged[-1][1], end)
                else:
                    merged.append([start, end])
            return merged
    '''),
)

task(
    id="kod-kelime", category="Kod yazma", kind="python", title="En sık kelimeler", entry="top_k_words",
    prompt=code("""
        Python'da `top_k_words(text: str, k: int) -> list[tuple[str, int]]` fonksiyonunu yaz. Metinde en sık geçen
        k kelimeyi (kelime, sayı) çiftleri olarak döndürsün.
        - Büyük/küçük harf farkı önemsiz; kelimeler küçük harfe çevrilsin.
        - Kelime ardışık harflerden oluşur (Türkçe harfler dahil); rakamlar ve noktalama işaretleri kelimeye dahil değildir.
        - Sıralama: sayıya göre azalan; sayılar eşitse kelimeye göre alfabetik (Python'un normal string sıralaması).
        - k, farklı kelime sayısından büyükse hepsini döndürsün.
    """) + "\n" + PY_ONLY,
    prelude="def norm(result):\n    return [tuple(x) for x in result]",
    tests=[
        'norm(S.top_k_words("elma armut elma kiraz armut elma", 2)) == [("elma", 3), ("armut", 2)]',
        'norm(S.top_k_words("Çay, çay! ÇAY kahve?", 1)) == [("çay", 3)]',
        'norm(S.top_k_words("b a c b a c d", 3)) == [("a", 2), ("b", 2), ("c", 2)]',
        'norm(S.top_k_words("yıl 2026 yıl 2025 ay", 5)) == [("yıl", 2), ("ay", 1)]',
        'norm(S.top_k_words("göğüs-ağrısı göğüs", 2)) == [("göğüs", 2), ("ağrısı", 1)]',
        'norm(S.top_k_words("bir iki", 10)) == [("bir", 1), ("iki", 1)]',
        'norm(S.top_k_words("", 3)) == []',
    ],
    reference=code('''
        import re
        from collections import Counter

        def top_k_words(text, k):
            counts = Counter(re.findall(r"[^\\W\\d_]+", text.lower()))
            return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:k]
    '''),
)

task(
    id="kod-lru", category="Kod yazma", kind="python", title="LRU önbellek", entry="LRUCache",
    prompt=code("""
        Python'da bir `LRUCache` sınıfı yaz. `LRUCache(capacity)` ile oluşturulsun; `get(key)` anahtar yoksa -1
        döndürsün; `put(key, value)` eklesin ya da güncellesin. Kapasite aşılınca en uzun süredir kullanılmayan anahtar
        silinsin. `get` ve `put` çağrıları anahtarı "kullanılmış" sayar. İki işlem de O(1) olsun.
    """) + "\n" + PY_ONLY,
    prelude=code("""
        def lru_basic():
            c = S.LRUCache(2)
            c.put(1, 1); c.put(2, 2)
            first = c.get(1)
            c.put(3, 3)
            return (first, c.get(2), c.get(3)) == (1, -1, 3)

        def lru_update():
            c = S.LRUCache(2)
            c.put(1, 1); c.put(2, 2); c.put(1, 10)
            c.put(3, 3)
            return (c.get(1), c.get(2), c.get(3)) == (10, -1, 3)

        def lru_capacity_one():
            c = S.LRUCache(1)
            c.put("a", 1); c.put("b", 2)
            return (c.get("a"), c.get("b")) == (-1, 2)

        def lru_get_refreshes():
            c = S.LRUCache(3)
            for i in range(3):
                c.put(i, i)
            c.get(0)
            c.put(3, 3)
            return (c.get(1), c.get(0), c.get(2), c.get(3)) == (-1, 0, 2, 3)

        def lru_missing():
            return S.LRUCache(2).get(42) == -1

        def lru_fast():
            import time
            c = S.LRUCache(1000)
            start = time.perf_counter()
            for i in range(200_000):
                c.put(i % 5000, i)
                c.get((i * 7) % 5000)
                if i % 1000 == 0 and time.perf_counter() - start > 3:
                    return False
            return True
    """),
    tests=["lru_basic()", "lru_update()", "lru_capacity_one()", "lru_get_refreshes()", "lru_missing()", "lru_fast()"],
    reference=code('''
        from collections import OrderedDict

        class LRUCache:
            def __init__(self, capacity):
                self.capacity = capacity
                self.data = OrderedDict()

            def get(self, key):
                if key not in self.data:
                    return -1
                self.data.move_to_end(key)
                return self.data[key]

            def put(self, key, value):
                self.data[key] = value
                self.data.move_to_end(key)
                if len(self.data) > self.capacity:
                    self.data.popitem(last=False)
    '''),
)

task(
    id="kod-ifade", category="Kod yazma", kind="python", title="İfade hesaplayıcı", entry="eval_expr",
    prompt=code("""
        Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
        işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
        ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
    """) + "\n" + PY_ONLY,
    forbid=r"\b(eval|exec|compile)\s*\(",
    prelude="def close(a, b):\n    return isinstance(a, (int, float)) and abs(a - b) < 1e-9",
    tests=[
        'close(S.eval_expr("2+3*4"), 14)', 'close(S.eval_expr("(2+3)*4"), 20)', 'close(S.eval_expr("-3+5"), 2)',
        'close(S.eval_expr("2*(3+(4-1))/3"), 4)', 'close(S.eval_expr("10/4"), 2.5)',
        'close(S.eval_expr("-(2+3)*-2"), 10)', 'close(S.eval_expr(" 7 - 2 - 1 "), 4)',
        'close(S.eval_expr("2*-3"), -6)', 'close(S.eval_expr("1.5*4"), 6)', 'close(S.eval_expr("8/2/2"), 2)',
        'close(S.eval_expr("3-(-2)"), 5)',
    ],
    reference=code('''
        import re

        def eval_expr(s):
            tokens = re.findall(r"\\d+\\.\\d+|\\d+|[-+*/()]", s)
            pos = 0

            def peek():
                return tokens[pos] if pos < len(tokens) else None

            def take():
                nonlocal pos
                pos += 1
                return tokens[pos - 1]

            def expr():
                value = term()
                while peek() in ("+", "-"):
                    value = value + term() if take() == "+" else value - term()
                return value

            def term():
                value = factor()
                while peek() in ("*", "/"):
                    value = value * factor() if take() == "*" else value / factor()
                return value

            def factor():
                tok = take()
                if tok == "-":
                    return -factor()
                if tok == "+":
                    return factor()
                if tok == "(":
                    value = expr()
                    take()
                    return value
                return float(tok)

            return expr()
    '''),
)

task(
    id="kod-sure-js", category="Kod yazma", kind="js", title="Süre ayrıştırma (JS)", entry="parseDuration",
    prompt=code("""
        JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
        metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
        bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
        sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
        Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
    """) + "\n" + JS_ONLY,
    prelude="function throws(f) { try { f(); return false; } catch (e) { return true; } }",
    tests=[
        'S.parseDuration("1h 30m 15s") === 5415', 'S.parseDuration("45m") === 2700', 'S.parseDuration("2h") === 7200',
        'S.parseDuration("90s") === 90', 'S.parseDuration("1h15s") === 3615', 'S.parseDuration("1h 0m") === 3600',
        'throws(() => S.parseDuration(""))', 'throws(() => S.parseDuration("5x"))', 'throws(() => S.parseDuration("m"))',
        'throws(() => S.parseDuration("10s 5m"))', 'throws(() => S.parseDuration("1h 2h"))',
    ],
    reference=code('''
        function parseDuration(str) {
          const m = /^\\s*(?:(\\d+)\\s*h)?\\s*(?:(\\d+)\\s*m)?\\s*(?:(\\d+)\\s*s)?\\s*$/.exec(str);
          if (!m || (m[1] === undefined && m[2] === undefined && m[3] === undefined)) throw new Error("geçersiz süre");
          return Number(m[1] || 0) * 3600 + Number(m[2] || 0) * 60 + Number(m[3] || 0);
        }
        module.exports = { parseDuration };
    '''),
)

# ---------------------------------------------------------------- Hata ayıklama


def bug_prompt(description: str, buggy: str) -> str:
    return (f"Aşağıdaki Python kodunda hata var. {description}\nHatayı düzelt ve kodun düzeltilmiş tam halini ver. "
            f"{PY_ONLY}\n\n```python\n{buggy}\n```")


BUGGY_SEARCH = code('''
    def binary_search(arr, target):
        """Sıralı listede target'ın indeksini, yoksa -1 döndürür."""
        lo, hi = 0, len(arr) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                lo = mid + 1
            else:
                hi = mid - 1
        return -1
''')
task(
    id="hata-ikili-arama", category="Hata ayıklama", kind="python", title="İkili arama", entry="binary_search",
    buggy=BUGGY_SEARCH,
    prompt=bug_prompt("Örneğin binary_search([1, 3, 5], 5) 2 döndürmesi gerekirken -1 döndürüyor.", BUGGY_SEARCH),
    tests=[
        "S.binary_search([1, 3, 5], 5) == 2", "S.binary_search([1, 3, 5], 1) == 0", "S.binary_search([1, 3, 5], 3) == 1",
        "S.binary_search([7], 7) == 0", "S.binary_search([], 1) == -1", "S.binary_search([1, 3, 5], 4) == -1",
        "S.binary_search([1, 3, 5], 6) == -1", "S.binary_search([1, 3, 5], 0) == -1",
        "all(S.binary_search(list(range(0, 40, 2)), v) == v // 2 for v in range(0, 40, 2))",
    ],
    reference=BUGGY_SEARCH.replace("while lo < hi:", "while lo <= hi:"),
)

BUGGY_TAGS = code('''
    def add_tag(tag, tags=[]):
        """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
        tags.append(tag)
        return tags
''')
task(
    id="hata-varsayilan", category="Hata ayıklama", kind="python", title="Değişken varsayılan argüman", entry="add_tag",
    buggy=BUGGY_TAGS,
    prompt=bug_prompt("add_tag('a') ve ardından add_tag('b') çağrılınca ikinci çağrı ['b'] döndürmeli, ama ['a', 'b'] "
                      "döndürüyor.", BUGGY_TAGS),
    prelude=code("""
        def fresh_lists():
            return S.add_tag("a") == ["a"] and S.add_tag("b") == ["b"]

        def given_list():
            tags = ["z"]
            result = S.add_tag("y", tags)
            return result == ["z", "y"] and tags == ["z", "y"]

        def many_calls():
            return all(S.add_tag(str(i)) == [str(i)] for i in range(5))
    """),
    tests=["fresh_lists()", "given_list()", "many_calls()"],
    reference=code('''
        def add_tag(tag, tags=None):
            if tags is None:
                tags = []
            tags.append(tag)
            return tags
    '''),
)

BUGGY_CHUNKS = code('''
    def chunks(items, size):
        """Listeyi size uzunluğunda parçalara böler; son parça daha kısa olabilir."""
        return [items[i:i + size] for i in range(0, len(items) - size, size)]
''')
task(
    id="hata-parcalama", category="Hata ayıklama", kind="python", title="Parçalara bölme", entry="chunks",
    buggy=BUGGY_CHUNKS,
    prompt=bug_prompt("Örneğin chunks([1, 2, 3, 4, 5], 2) [[1, 2], [3, 4], [5]] döndürmeli.", BUGGY_CHUNKS),
    tests=[
        "S.chunks([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]", "S.chunks([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]",
        "S.chunks([], 3) == []", "S.chunks([1, 2], 5) == [[1, 2]]", "S.chunks([1, 2, 3], 1) == [[1], [2], [3]]",
        'S.chunks("abcde", 2) == ["ab", "cd", "e"]',
    ],
    reference=BUGGY_CHUNKS.replace("len(items) - size", "len(items)"),
)

BUGGY_CART = code('''
    class Cart:
        items = []

        def add(self, name, price, qty=1):
            self.items.append((name, price, qty))

        def total(self, discount_percent=0):
            """İndirimli toplam tutar; indirim yüzde olarak verilir (ör. 10 → %10)."""
            subtotal = sum(price * qty for _, price, qty in self.items)
            return round(subtotal - subtotal * discount_percent, 2)
''')
task(
    id="hata-sepet", category="Hata ayıklama", kind="python", title="Alışveriş sepeti", entry="Cart",
    buggy=BUGGY_CART,
    prompt=bug_prompt("Bu sınıfta iki hata var: farklı Cart nesneleri birbirinin ürünlerini görüyor ve indirim yanlış "
                      "hesaplanıyor (total(10) %10 indirim uygulamalı).", BUGGY_CART),
    prelude=code("""
        def separate_carts():
            a, b = S.Cart(), S.Cart()
            a.add("x", 10)
            return b.total() == 0 and a.total() == 10

        def plain_total():
            c = S.Cart()
            c.add("kalem", 12.5, 2)
            c.add("defter", 30)
            return abs(c.total() - 55) < 0.01

        def discount_total():
            c = S.Cart()
            c.add("kalem", 12.5, 2)
            c.add("defter", 30)
            return abs(c.total(10) - 49.5) < 0.01

        def empty_cart():
            return S.Cart().total() == 0

        def discount_rounding():
            c = S.Cart()
            c.add("a", 19.99, 3)
            return abs(c.total(15) - 50.97) < 0.011
    """),
    tests=["separate_carts()", "plain_total()", "discount_total()", "empty_cart()", "discount_rounding()"],
    reference=code('''
        class Cart:
            def __init__(self):
                self.items = []

            def add(self, name, price, qty=1):
                self.items.append((name, price, qty))

            def total(self, discount_percent=0):
                subtotal = sum(price * qty for _, price, qty in self.items)
                return round(subtotal - subtotal * discount_percent / 100, 2)
    '''),
)

# ---------------------------------------------------------------- Kod okuma


def output_prompt(lang: str, snippet: str) -> str:
    name, fence = ("Python", "python") if lang == "python" else ("JavaScript (Node.js)", "javascript")
    return (f"Aşağıdaki {name} kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. "
            f"Sadece çıktıyı tek bir ```text bloğu içinde ver.\n\n```{fence}\n{snippet}\n```")


for _id, _title, _lang, _snippet in [
    ("okuma-takma-ad", "Liste takma adları", "python", code("""
        a = [1, 2, 3]
        b = a
        b += [4]
        c = a[:]
        c.append(5)
        print(a, b, c)
    """)),
    ("okuma-kapanis", "Kapanış (closure)", "python", code("""
        fs = [lambda: i for i in range(3)]
        print([f() for f in fs])
        gs = [lambda i=i: i for i in range(3)]
        print([g() for g in gs])
    """)),
    ("okuma-siralama", "Sıralama anahtarı", "python", code("""
        data = {"elma": 3, "armut": 1, "kiraz": 3, "muz": 2}
        order = sorted(data, key=lambda k: (-data[k], k))
        print(order)
        print(sum(v for k, v in data.items() if "a" in k))
    """)),
    ("okuma-sayilar", "Bölme ve yuvarlama", "python", code("""
        print(7 // -2, -7 % 3, round(2.5), round(3.5), int(-2.7))
        print("a,b,,c".split(","), "  x  y ".split())
    """)),
    ("okuma-uretec", "Üreteç ve finally", "python", code("""
        def gen():
            try:
                yield 1
                yield 2
            finally:
                print("bitti")

        for x in gen():
            print(x)
            break
        print("son")
    """)),
    ("okuma-olay-dongusu", "Olay döngüsü (JS)", "js", code("""
        console.log("A");
        setTimeout(() => console.log("B"), 0);
        Promise.resolve().then(() => console.log("C"));
        (async () => {
          console.log("D");
          await null;
          console.log("E");
        })();
        console.log("F");
    """)),
]:
    task(id=_id, category="Kod okuma", kind="output", title=_title, lang=_lang, snippet=_snippet,
         prompt=output_prompt(_lang, _snippet))

# ---------------------------------------------------------------- SQL

SQL_SCHEMA = code("""
    CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
    CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
    CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER REFERENCES customers(id),
                         product_id INTEGER REFERENCES products(id), quantity INTEGER,
                         order_date TEXT);  -- 'YYYY-MM-DD'
""")
SQL_DATA = {
    "customers": [(1, "Ayşe", "İstanbul"), (2, "Mehmet", "Ankara"), (3, "Zeynep", "İzmir"), (4, "Can", "İstanbul"),
                  (5, "Elif", "Ankara"), (6, "Burak", "Bursa"), (7, "Deniz", "İstanbul"), (8, "Ece", "İzmir")],
    "products": [(1, "Laptop", "Elektronik", 25000), (2, "Mouse", "Elektronik", 450), (3, "Kitap", "Kırtasiye", 180),
                 (4, "Defter", "Kırtasiye", 60), (5, "Kulaklık", "Elektronik", 1800), (6, "Kalem", "Kırtasiye", 25),
                 (7, "Ajanda", "Kırtasiye", 180), (8, "Kupa", "Mutfak", 150), (9, "Termos", "Mutfak", 600)],
    "orders": [(1, 1, 1, 1, "2026-01-15"), (2, 1, 2, 2, "2026-02-03"), (3, 2, 3, 3, "2026-02-10"),
               (4, 3, 5, 1, "2025-12-28"), (5, 3, 9, 2, "2026-03-05"), (6, 4, 1, 1, "2026-04-20"),
               (7, 4, 5, 2, "2026-05-11"), (8, 5, 4, 10, "2026-06-01"), (9, 7, 8, 4, "2026-06-15"),
               (10, 2, 1, 1, "2025-11-30"), (11, 7, 2, 1, "2026-07-07"), (12, 5, 7, 3, "2026-08-19")],
}


def make_sql_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SQL_SCHEMA)
    for table, rows in SQL_DATA.items():
        conn.executemany(f"INSERT INTO {table} VALUES ({', '.join('?' * len(rows[0]))})", rows)
    return conn


def sql_prompt(question: str) -> str:
    return (f"SQLite veritabanında şu tablolar var:\n```sql\n{SQL_SCHEMA}\n```\n{question}\n"
            "Tek bir SELECT sorgusu yaz. Sadece sorguyu tek bir ```sql bloğu içinde ver.")


for _id, _title, _question, _reference in [
    ("sql-sehir", "Gruplama", "Her şehirdeki müşteri sayısını listele. Sütunlar: şehir, müşteri sayısı. Müşteri "
     "sayısına göre azalan, eşitlikte şehir adına göre artan sırala.",
     "SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY COUNT(*) DESC, city"),
    ("sql-harcama", "Join ve toplam", "2026 yılında (order_date '2026' ile başlayan siparişler) en çok harcama yapan "
     "3 müşteriyi listele. Harcama, products.price * orders.quantity değerlerinin toplamıdır. Sütunlar: müşteri adı, "
     "toplam harcama. Toplam harcamaya göre azalan sırala.",
     "SELECT c.name, SUM(p.price * o.quantity) AS total FROM orders o JOIN customers c ON c.id = o.customer_id "
     "JOIN products p ON p.id = o.product_id WHERE o.order_date LIKE '2026%' GROUP BY c.id ORDER BY total DESC LIMIT 3"),
    ("sql-siparissiz", "Eksik kayıtlar", "Hiç sipariş vermemiş müşterilerin adlarını alfabetik sırayla listele. "
     "Tek sütun: müşteri adı.",
     "SELECT name FROM customers WHERE id NOT IN (SELECT customer_id FROM orders) ORDER BY name"),
    ("sql-en-pahali", "Grup içi en büyük", "Her kategorideki en pahalı ürünü listele; aynı en yüksek fiyata sahip "
     "birden fazla ürün varsa hepsini göster. Sütunlar: kategori, ürün adı, fiyat. Kategoriye, sonra ürün adına göre "
     "artan sırala.",
     "SELECT category, name, price FROM products p WHERE price = (SELECT MAX(price) FROM products "
     "WHERE category = p.category) ORDER BY category, name"),
]:
    task(id=_id, category="SQL", kind="sql", title=_title, prompt=sql_prompt(_question), reference=_reference)

# ---------------------------------------------------------------- Terminal (PowerShell)

NOTES = "Toplantı notları\n- Benchmark sonuçlarını incele\n"
TODO = "1. Rapor yaz\n2. Testleri çalıştır\n"
SHELL_TREE = code("""
    .
    ├── logs
    │   ├── app1.log
    │   ├── app2.log
    │   └── old
    │       └── app0.log
    ├── data
    │   ├── notes.txt
    │   ├── todo.txt
    │   ├── report.csv
    │   ├── big.bin
    │   └── image.png
    └── readme.md
""")


def setup_shell(d: Path) -> None:
    write(d / "logs" / "app1.log", "2026-10-01 10:00:01 INFO Uygulama başladı\n"
                                   "2026-10-01 10:00:05 ERROR Veritabanına bağlanılamadı\n"
                                   "2026-10-01 10:00:09 WARN Yeniden deneniyor\n"
                                   "2026-10-01 10:00:15 ERROR Zaman aşımı\n"
                                   "2026-10-01 10:01:00 INFO Bağlantı kuruldu\n")
    write(d / "logs" / "app2.log", "2026-10-02 08:00:00 INFO Görev kuyruğu açıldı\n"
                                   "2026-10-02 08:05:12 ERROR Dosya bulunamadı: rapor.pdf\n"
                                   "2026-10-02 08:05:13 ERROR Görev başarısız oldu\n"
                                   "2026-10-02 08:10:00 INFO Yeniden başlatıldı\n"
                                   "2026-10-02 09:00:00 ERROR Disk dolu\n")
    write(d / "logs" / "old" / "app0.log", "2026-09-01 12:00:00 INFO Eski kayıt\n2026-09-01 12:00:01 ERROR Eski hata\n")
    write(d / "data" / "notes.txt", NOTES)
    write(d / "data" / "todo.txt", TODO)
    write(d / "data" / "report.csv", "date,product,amount\n2026-10-01,Kalem,120.5\n2026-10-02,Defter,80\n"
                                     "2026-10-03,Çanta,300.25\n2026-10-04,Silgi,49.25\n")
    (d / "data" / "big.bin").write_bytes(bytes(range(256)) * 256)
    (d / "data" / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n" + bytes(2000))
    write(d / "readme.md", "# Deneme klasörü\n")


def shell_prompt(job: str) -> str:
    return ("Windows'ta PowerShell 7 (pwsh) kullanıyorum. Bulunduğum klasörün yapısı şöyle:\n"
            f"```text\n{SHELL_TREE}\n```\ndata/report.csv dosyasının ilk satırı: date,product,amount\n\n"
            f"Görev: {job}\n\nBu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları "
            "; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.")


def _last_line(out: str) -> str:
    lines = [line.strip() for line in out.strip().splitlines() if line.strip()]
    return lines[-1] if lines else ""


def expect_text(expected: str):
    def check(d: Path, out: str) -> tuple[float, str]:
        got = _last_line(out)
        return (1.0, "doğru") if got == expected else (0.0, f"beklenen {expected!r}, çıktı {got[:80]!r}")
    return check


def expect_number(expected: float):
    def check(d: Path, out: str) -> tuple[float, str]:
        got = _last_line(out)
        try:
            ok = abs(float(got.replace(",", ".")) - expected) < 0.01
        except ValueError:
            ok = False
        return (1.0, "doğru") if ok else (0.0, f"beklenen {expected}, çıktı {got[:80]!r}")
    return check


def check_archive(d: Path, out: str) -> tuple[float, str]:
    if not any((d / "archive" / name).is_file() for name in ("app1.log", "app2.log")):
        return 0.0, "archive klasörüne dosya taşınmamış"
    return fraction({
        "archive/app1.log var": (d / "archive" / "app1.log").is_file(),
        "archive/app2.log var": (d / "archive" / "app2.log").is_file(),
        "logs/app1.log ve app2.log taşınmış": not (d / "logs" / "app1.log").exists()
                                             and not (d / "logs" / "app2.log").exists(),
        "logs/old/app0.log yerinde": (d / "logs" / "old" / "app0.log").is_file()
                                     and not (d / "archive" / "app0.log").exists(),
    })


def check_rename(d: Path, out: str) -> tuple[float, str]:
    def same(path: Path, text: str) -> bool:
        return path.is_file() and path.read_text(encoding="utf-8", errors="replace") == text
    if not any((d / "data" / name).is_file() for name in ("notes.md", "todo.md")):
        return 0.0, ".md dosyası oluşmamış"
    return fraction({
        "notes.md içeriği korunmuş": same(d / "data" / "notes.md", NOTES),
        "todo.md içeriği korunmuş": same(d / "data" / "todo.md", TODO),
        "data'da .txt kalmamış": not list((d / "data").glob("*.txt")),
        "diğer dosyalar yerinde": all((d / p).is_file() for p in ["data/report.csv", "data/big.bin", "readme.md"]),
    })


for _id, _title, _job, _check, _reference in [
    ("term-sayim", "Dosya sayma", "Bu klasörde ve tüm alt klasörlerde toplam kaç tane .log dosyası var? "
     "Komut sadece sayıyı yazdırsın.", expect_text("3"), "(Get-ChildItem -Recurse -File -Filter *.log).Count"),
    ("term-grep", "Satır arama", "logs klasöründeki (alt klasörler dahil) tüm .log dosyalarında 'ERROR' geçen "
     "satırların toplam sayısını yazdır (sadece sayı).", expect_text("6"),
     "(Get-ChildItem logs -Recurse -Filter *.log | Select-String -Pattern 'ERROR' -CaseSensitive).Count"),
    ("term-en-buyuk", "En büyük dosya", "Bu klasördeki (alt klasörler dahil) en büyük dosyanın sadece adını yazdır.",
     expect_text("big.bin"), "(Get-ChildItem -Recurse -File | Sort-Object Length -Descending | Select-Object -First 1).Name"),
    ("term-csv", "CSV toplamı", "data/report.csv dosyasındaki amount sütununun toplamını yazdır (sadece sayı).",
     expect_number(550.0), "(Import-Csv data/report.csv | Measure-Object -Property amount -Sum).Sum"),
    ("term-tasima", "Dosya taşıma", "archive adında bir klasör oluştur ve logs klasörünün doğrudan içindeki .log "
     "dosyalarını (alt klasördekiler hariç) bu klasöre taşı.", check_archive,
     "New-Item -ItemType Directory archive | Out-Null; Move-Item logs/*.log archive/"),
    ("term-uzanti", "Toplu uzantı değiştirme", "data klasöründeki tüm .txt dosyalarının uzantısını .md olarak "
     "değiştir (içerikleri aynı kalsın).", check_rename,
     "Get-ChildItem data -Filter *.txt | Rename-Item -NewName { $_.BaseName + '.md' }"),
]:
    task(id=_id, category="Terminal", kind="shell", title=_title, prompt=shell_prompt(_job), setup=setup_shell,
         check=_check, reference=_reference)

# ---------------------------------------------------------------- Ajan (CLI'ın araçlarıyla çok adımlı işler)


def setup_stock(d: Path) -> None:
    write(d / "urunler.csv", "urun,fiyat,adet\nKalem,12.5,40\nDefter,30,25\nSilgi,4.75,100\nÇanta,450,3\n")


def check_stock(d: Path, answer: str) -> tuple[float, str]:
    f = d / "ozet.txt"
    if not f.is_file():
        return 0.0, "ozet.txt oluşturulmamış"
    text = f.read_text(encoding="utf-8", errors="replace").strip()
    numbers = [float(n.replace(",", ".")) for n in re.findall(r"-?\d+(?:[.,]\d+)?", text)]
    if not any(abs(n - 3075) < 0.01 for n in numbers):
        return 0.0, f"yanlış sonuç: {text[:60]!r} (doğrusu 3075)"
    if re.fullmatch(r"\d+(?:[.,]0+)?", text):
        return 1.0, "doğru"
    return 0.5, f"sonuç doğru ama dosyada sayıdan başka metin de var: {text[:60]!r}"


CALC_PY = code('''
    def percent(part, total):
        """part'ın total içindeki yüzdesini döndürür (ör. 25, 200 → 12.5)."""
        return part / total * 10


    def average(numbers):
        """Sayıların ortalaması; boş listede 0 döndürür."""
        return sum(numbers) / len(numbers)
''') + "\n"
TESTS_PY = code('''
    from calc import average, percent

    assert percent(25, 200) == 12.5, "percent(25, 200)"
    assert percent(1, 4) == 25, "percent(1, 4)"
    assert average([2, 4, 6]) == 4, "average([2, 4, 6])"
    assert average([]) == 0, "average([])"
    print("TÜM TESTLER GEÇTİ")
''') + "\n"
CALC_CHECK = code('''
    import json
    res = {}
    try:
        import calc
        res["percent"] = abs(calc.percent(25, 200) - 12.5) < 1e-9 and abs(calc.percent(1, 4) - 25) < 1e-9
    except BaseException:
        res["percent"] = False
    try:
        res["average"] = calc.average([2, 4, 6]) == 4 and calc.average([]) == 0
    except BaseException:
        res["average"] = False
    print(json.dumps(res))
''')


def setup_calc(d: Path) -> None:
    write(d / "calc.py", CALC_PY)
    write(d / "tests.py", TESTS_PY)


def check_calc(d: Path, answer: str) -> tuple[float, str]:
    tests = d / "tests.py"
    if not tests.is_file() or hashlib.sha256(tests.read_bytes()).digest() != hashlib.sha256(TESTS_PY.encode()).digest():
        return 0.0, "tests.py değiştirilmiş"
    calc = d / "calc.py"
    if not calc.is_file():
        return 0.0, "calc.py yok"
    if reason := grading.python_danger(calc.read_text(encoding="utf-8", errors="replace")):
        return 0.0, reason
    _, out, err, timed_out = grading.run([sys.executable, "-c", CALC_CHECK], d, 30)
    try:
        res = json.loads(out.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return 0.0, "calc.py çalışmadı: " + (err or out)[-200:]
    return fraction({"percent düzeltilmiş": res.get("percent", False), "average([]) düzeltilmiş": res.get("average", False)})


def apply_calc(d: Path) -> None:
    write(d / "calc.py", CALC_PY.replace("part / total * 10", "part / total * 100")
          .replace("return sum(numbers) / len(numbers)", "return sum(numbers) / len(numbers) if numbers else 0"))


def setup_todos(d: Path) -> None:
    write(d / "src" / "main.py", code('''
        import utils

        # TODO: komut satırı argümanlarını ekle
        def main():
            print(utils.greet("dünya"))


        if __name__ == "__main__":
            main()
    ''') + "\n")
    write(d / "src" / "utils.py", code('''
        def greet(name):
            return f"Merhaba, {name}!"


        def slow_sum(numbers):
            total = 0
            for n in numbers:  # TODO: sum() ile değiştir
                total += n
            return total
    ''') + "\n")
    write(d / "src" / "web" / "app.js", code('''
        const http = require("http");
        // TODO: portu ortam değişkeninden oku
        const port = 3000;
        http.createServer((req, res) => res.end("ok")).listen(port);
    ''') + "\n")


TODO_EXPECTED = {"main.py": 3, "utils.py": 7, "web/app.js": 2}


def check_todos(d: Path, answer: str) -> tuple[float, str]:
    f = d / "todo_list.md"
    if not f.is_file():
        return 0.0, "todo_list.md oluşturulmamış"
    text = f.read_text(encoding="utf-8", errors="replace").replace("\\", "/")
    return fraction({f"{path}:{line}": bool(re.search(rf"(?<![\w/])(?:\./)?(?:src/)?{re.escape(path)}:{line}\b", text))
                     for path, line in TODO_EXPECTED.items()})


def apply_todos(d: Path) -> None:
    write(d / "todo_list.md", "main.py:3: # TODO: komut satırı argümanlarını ekle\n"
                              "utils.py:7: for n in numbers:  # TODO: sum() ile değiştir\n"
                              "web/app.js:2: // TODO: portu ortam değişkeninden oku\n")


CONFIG = {"name": "demo-app", "version": "1.4.2", "debug": False, "features": ["login", "export"]}
CHANGELOG = "# Değişiklikler\n\n## 1.4.2\n- İlk sürüm\n"


def setup_release(d: Path) -> None:
    write(d / "config.json", json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n")
    write(d / "CHANGELOG.md", CHANGELOG)


def check_release(d: Path, answer: str) -> tuple[float, str]:
    try:
        cfg = json.loads((d / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        cfg = {}
    log = (d / "CHANGELOG.md").read_text(encoding="utf-8", errors="replace") if (d / "CHANGELOG.md").is_file() else ""
    new, old = log.find("## 1.5.0"), log.find("## 1.4.2")
    if cfg.get("version") != "1.5.0" and new < 0:
        return 0.0, "hiçbir dosya güncellenmemiş"
    return fraction({
        "version 1.5.0": cfg.get("version") == "1.5.0",
        "diğer alanlar aynı": {k: v for k, v in cfg.items() if k != "version"}
                              == {k: v for k, v in CONFIG.items() if k != "version"},
        "1.5.0 bölümü 1.4.2'nin üstünde": log.startswith("# Değişiklikler") and 0 <= new < old,
        "madde eklenmiş": 0 <= new < old and "Sürüm yükseltildi" in log[new:old],
    })


def apply_release(d: Path) -> None:
    write(d / "config.json", json.dumps({**CONFIG, "version": "1.5.0"}, indent=2, ensure_ascii=False) + "\n")
    write(d / "CHANGELOG.md", CHANGELOG.replace("## 1.4.2", "## 1.5.0\n- Sürüm yükseltildi\n\n## 1.4.2"))


for _id, _title, _prompt, _setup, _check, _apply in [
    ("ajan-stok", "CSV hesaplayıp dosyaya yazma",
     "Bu klasördeki urunler.csv dosyasındaki ürünlerin toplam stok değerini (her ürün için fiyat × adet, hepsinin "
     "toplamı) hesapla ve sonucu ozet.txt dosyasına sadece sayı olarak yaz.", setup_stock, check_stock,
     lambda d: write(d / "ozet.txt", "3075\n")),
    ("ajan-test-duzelt", "Testleri geçirme",
     "Bu klasördeki küçük projede tests.py çalıştırıldığında hata alınıyor. calc.py'deki hataları bul ve düzelt; "
     "tests.py'yi değiştirme. Bitirmeden önce testlerin geçtiğini doğrula.", setup_calc, check_calc, apply_calc),
    ("ajan-todo", "Kod tabanında arama",
     "src klasöründe 'TODO' geçen tüm satırları bul ve bu klasörde todo_list.md dosyasına, her biri ayrı satırda "
     "olacak şekilde `dosya:satır_no: metin` biçiminde yaz. Dosya yolları src klasörüne göre olsun "
     "(ör. web/app.js:2: ...).", setup_todos, check_todos, apply_todos),
    ("ajan-surum", "İki dosyada düzenleme",
     "config.json'daki version değerini 1.5.0 yap (diğer alanlar aynı kalsın). CHANGELOG.md'de '# Değişiklikler' "
     "başlığının altına, 1.4.2 bölümünün üstüne, '## 1.5.0' başlıklı ve '- Sürüm yükseltildi' maddesi olan yeni bir "
     "bölüm ekle.", setup_release, check_release, apply_release),
]:
    task(id=_id, category="Ajan (araçlar)", kind="agent", title=_title, prompt=_prompt, setup=_setup, check=_check,
         apply_reference=_apply)
