"""Kod okuma: araçlar kapalı (gambit --no-tools); model kodun çıktısını kafasında çalıştırır. Beklenen çıktı kod
gerçekten çalıştırılarak üretilir. Puan satır satır verilir (core.output_similarity): doğru satır tam puan, kısmen
doğru satır kısmi puan alır."""

from pathlib import Path

import grading
from core import Rubric, code, extract_text_answer, output_similarity, task

_cache: dict[str, str] = {}


def expected(snippet: str, lang: str) -> str:
    if snippet not in _cache:
        _cache[snippet] = grading.run_snippet(snippet, lang)
    return _cache[snippet]


def prompt(lang: str, snippet: str) -> str:
    name, fence = ("Python 3.14", "python") if lang == "python" else ("JavaScript (Node.js, CommonJS modülü olarak çalışan bir .js dosyası)", "javascript")
    return (f"Aşağıdaki {name} kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda adım adım çalıştır. "
            f"Cevabının sonunda çıktıyı birebir (her satır ayrı) tek bir ```text bloğu içinde ver.\n\n"
            f"```{fence}\n{snippet}\n```")


def make(id_: str, title: str, level: int, lang: str, snippet: str) -> None:
    def grade(d: Path, answer: str, trace) -> Rubric:
        score, detail = output_similarity(extract_text_answer(answer), expected(snippet, lang))
        return Rubric().add("çıktı satırları", 1, score).note(detail)

    def reference(d: Path) -> str:
        return f"```text\n{expected(snippet, lang)}```"

    def wrong(d: Path) -> str:
        lines = expected(snippet, lang).rstrip("\n").split("\n")
        lines[len(lines) // 2] = "yanlış satır"
        return "```text\n" + "\n".join(lines[:-1]) + "\n```"

    task(id=id_, category="Kod okuma", title=title, level=level, tools=False, prompt=prompt(lang, snippet),
         grade=grade, reference=reference, wrong=wrong)


make("okuma-mro", "Çoklu kalıtım ve super()", 3, "python", code('''
    class A:
        def kim(self):
            return "A"

        def zincir(self):
            return ["A"]


    class B(A):
        def kim(self):
            return "B" + super().kim()

        def zincir(self):
            return ["B"] + super().zincir()


    class C(A):
        def kim(self):
            return "C" + super().kim()

        def zincir(self):
            return ["C"] + super().zincir()


    class D(B, C):
        sayac = 0

        def __init__(self):
            D.sayac += 1
            self.sayac += 10


    print(D().kim())
    print(D().zincir())
    print([k.__name__ for k in D.__mro__])
    d = D()
    print(D.sayac, d.sayac)
    print(isinstance(d, C), issubclass(C, B))
'''))

make("okuma-uretec", "Üreteçler, send ve yield from", 4, "python", code('''
    def sayac():
        toplam = 0
        while True:
            x = yield toplam
            if x is None:
                return toplam
            toplam += x


    def sarici():
        sonuc = yield from sayac()
        yield f"bitti:{sonuc}"


    g = sarici()
    print(next(g))
    print(g.send(5))
    print(g.send(10))
    print(next(g))
    print(list(g))
    h = (i * i for i in range(5) if i % 2)
    print(sum(h), sum(h))
    it = iter([1, 2, 3, 4, 5])
    print(list(zip(it, it)))
'''))

make("okuma-dekorator", "Dekoratör sırası ve geç bağlama", 3, "python", code('''
    import functools

    kayit = []


    def izle(etiket):
        def dekorator(f):
            kayit.append(f"tanim:{etiket}:{f.__name__}")

            @functools.wraps(f)
            def sarmal(*a, **k):
                kayit.append(f"cagri:{etiket}")
                return f(*a, **k) + 1
            return sarmal
        return dekorator


    @izle("dis")
    @izle("ic")
    def topla(x, y=10):
        return x + y


    print(topla(1), topla.__name__)
    print(kayit)


    def ekle(x, liste=[]):
        liste.append(x)
        return len(liste)


    print(ekle(1), ekle(2), ekle(3, []), ekle(4))
    carpanlar = {k: (lambda v: v * k) for k in range(3)}
    print([f(10) for f in carpanlar.values()])
    print({**{"a": 1, "b": 2}, **{"b": 3}, "a": 0})
'''))

make("okuma-asyncio", "asyncio görev sırası", 4, "python", code('''
    import asyncio

    sira = []


    async def is_(ad, bekle):
        sira.append(f"{ad}-basla")
        await asyncio.sleep(bekle)
        sira.append(f"{ad}-bitir")
        return ad.upper()


    async def main():
        t1 = asyncio.create_task(is_("a", 0.3))
        sira.append("gorev-olustu")
        r = await asyncio.gather(is_("b", 0.1), is_("c", 0))
        sira.append("gather-bitti")
        print(r, await t1)
        print(sira)


    asyncio.run(main())
'''))

make("okuma-js-this", "this, kapsam ve hoisting (JS)", 3, "js", code('''
    var x = "global";
    const obj = {
      x: "obj",
      normal() { return this.x; },
      ok: () => typeof this,
      icFonksiyon() {
        return [1].map(function () { return this === undefined ? "undef" : typeof this; })[0];
      },
      icOk() {
        return [1].map(() => this.x)[0];
      },
    };
    const f = obj.normal;
    console.log(obj.normal());
    console.log(obj.ok());
    console.log(obj.icFonksiyon());
    console.log(obj.icOk());
    try { console.log(f()); } catch (e) { console.log(e.constructor.name); }
    const fs = [];
    for (var i = 0; i < 3; i++) fs.push(() => i);
    const gs = [];
    for (let j = 0; j < 3; j++) gs.push(() => j);
    console.log(fs.map((g) => g()).join(","), gs.map((g) => g()).join(","));
    console.log(typeof kaldirilan, typeof kaldirilmayan);
    function kaldirilan() {}
    var kaldirilmayan = function () {};
'''))

make("okuma-js-tip", "Tür dönüşümleri (JS)", 2, "js", code('''
    console.log([10, 9, 1, 100].sort());
    console.log("5" - 2, "5" + 2, 5 + +"2", "b" + "a" + +"a" + "a");
    console.log(null == undefined, null === undefined, NaN === NaN, [1] == 1);
    console.log(typeof null, typeof [], Array.isArray([]));
    console.log(0.1 + 0.2 === 0.3, (0.1 + 0.2).toFixed(2));
    console.log([1, 2, 3].map(parseInt));
    console.log([..."aşk"].length, "😀".length, [..."😀"].length);
    console.log(Math.max() < Math.min(), [] + [] === "", typeof ([] + {}));
'''))
