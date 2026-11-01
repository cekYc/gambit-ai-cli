"""Mantık ve matematik: araçlar kapalı; çok parçalı sorular, cevap JSON. Her alt soru ayrı puanlanır; sayısal
cevaplarda yakın değer (≤ %2 hata) yarım puan alır."""

from pathlib import Path

from core import Rubric, code, extract_json, number_credit, task

JSON_NOTE = ("Cevabının SONUNDA tüm cevapları tek bir ```json bloğunda ver: anahtarlar soru numaraları (\"1\", \"2\", ...), "
             "değerler sayı (ondalıklı cevaplarda en az 4 anlamlı basamak ya da \"5/12\" gibi kesir) ya da istenen metin.")


def _answers(answer: str) -> dict:
    data = extract_json(answer)
    if isinstance(data, list):
        data = {str(i + 1): v for i, v in enumerate(data)}
    return {str(k).strip().rstrip(".)"): v for k, v in data.items()} if isinstance(data, dict) else {}


def numeric_task(id_: str, title: str, level: int, intro: str, questions: list[tuple[str, float, float]]) -> None:
    """questions: (soru metni, doğru değer, ağırlık)."""
    text = intro + "\n\n" + "\n".join(f"{i}. {q}" for i, (q, _, _) in enumerate(questions, 1)) + "\n\n" + JSON_NOTE

    def grade(d: Path, answer: str, trace) -> Rubric:
        got = _answers(answer)
        r = Rubric()
        if not got:
            r.note("JSON cevap bulunamadı")
        for i, (q, want, w) in enumerate(questions, 1):
            v = got.get(str(i))
            c = number_credit(v, want)
            r.add(f"{i}. soru", w, c, "" if c == 1 else f"beklenen {want:.6g}, cevap {v!r}")
        return r

    def reference(d: Path) -> str:
        return "```json\n{" + ", ".join(f'"{i}": {want!r}' for i, (_, want, _) in enumerate(questions, 1)) + "}\n```"

    def wrong(d: Path) -> str:
        vals = {str(i): (want if i % 2 else want * 1.5) for i, (_, want, _) in enumerate(questions, 1)}
        return "```json\n" + __import__("json").dumps(vals) + "\n```"

    task(id=id_, category="Mantık", title=title, level=level, tools=False, prompt=text, grade=grade,
         reference=reference, wrong=wrong)


numeric_task("mantik-olasilik", "Olasılık ve kombinatorik", 3, "Aşağıdaki soruları çöz (adım adım düşünebilirsin).", [
    ("İki adil zar atılıyor. Üst yüzlerin toplamının asal sayı olma olasılığı nedir?", 15 / 36, 1),
    ("İyi karıştırılmış 52'lik bir desteden 5 kart çekiliyor. Tam olarak 2 as gelme olasılığı nedir?", 103776 / 2598960, 1.5),
    ("MISSISSIPPI kelimesinin harfleriyle kaç farklı dizilim yazılabilir?", 34650, 1),
    ("1'den 1000'e kadar (ikisi dahil) olan tam sayılardan kaç tanesi 3'e ya da 5'e bölünür ama 15'e bölünmez?", 401, 1),
    ("Bir hastalığın toplumdaki yaygınlığı %1. Testin duyarlılığı %99 (hastaların %99'u pozitif çıkar), özgüllüğü %95 "
     "(sağlıklıların %95'i negatif çıkar). Testi pozitif çıkan rastgele birinin gerçekten hasta olma olasılığı nedir?", 1 / 6, 1.5),
    ("Bir torbada 3 kırmızı ve 5 mavi top var. Geri koymadan 3 top çekiliyor. En az bir kırmızı top çekilme olasılığı nedir?",
     46 / 56, 1),
    ("Adil bir zar, art arda iki kez 6 gelene kadar atılıyor. Beklenen atış sayısı nedir?", 42, 2),
])



def _py(src: str) -> str:
    return "\n   ```python\n" + "\n".join("   " + ln for ln in code(src).split("\n")) + "\n   ```\n   "


numeric_task("mantik-algoritma", "Algoritma analizi", 3, "Aşağıdaki soruları kodu çalıştırmadan, analiz ederek cevapla (Python).", [
    (_py("""
        def f(n):
            c, i = 0, 1
            while i < n:
                i *= 3
                c += 1
            return c
    """) + "f(1000) kaçtır?", 7, 1),
    (_py("""
        def g(n):
            c = 0
            for i in range(n):
                for j in range(i, n, 3):
                    c += 1
            return c
    """) + "g(10) kaçtır?", 22, 1.5),
    (_py("""
        def fib(n):
            return n if n < 2 else fib(n - 1) + fib(n - 2)
    """) + "fib(10) çağrıldığında fib fonksiyonu toplam kaç kez çağrılır (ilk çağrı dahil)?", 177, 1.5),
    ("0'dan 255'e kadar (ikisi dahil) tüm tam sayıların ikili gösterimlerindeki 1 bitlerinin toplam sayısı kaçtır?", 1024, 1),
    ("1.000.000 elemanlı sıralı bir dizide klasik ikili arama, en kötü durumda en fazla kaç kez ortadaki elemanla "
     "karşılaştırma (döngü adımı) yapar?", 20, 1),
    ("5×5 hücreli bir ızgarada sol üst hücreden sağ alt hücreye yalnızca sağa ya da aşağı hareket ederek kaç farklı "
     "yoldan gidilir?", 70, 1),
    (_py("""
        def h(a):
            i, s = 1, 0
            while i < len(a):
                for x in a[:i]:
                    s += x
                i *= 2
            return s
    """) + "n = 1024 elemanlı bir liste için `s += x` satırı toplam kaç kez çalışır?", 1023, 1.5),
])

# ---------------------------------------------------------------- bulmaca

PUZZLE = {
    "Ali": {"sehir": "İzmir", "meslek": "öğretmen", "icecek": "kahve"},
    "Berk": {"sehir": "Van", "meslek": "doktor", "icecek": "ayran"},
    "Cem": {"sehir": "Ankara", "meslek": "avukat", "icecek": "su"},
    "Deniz": {"sehir": "Bursa", "meslek": "mühendis", "icecek": "çay"},
}


def _fold(s) -> str:
    return str(s).strip().replace("İ", "i").replace("I", "ı").lower().replace("ı", "i").replace("ö", "o").replace("ü", "u").replace("ç", "c").replace("ğ", "g").replace("ş", "s")


def grade_puzzle(d: Path, answer: str, trace) -> Rubric:
    data = extract_json(answer)
    r = Rubric()
    if not isinstance(data, dict):
        r.note("JSON cevap bulunamadı")
        data = {}
    norm = {_fold(k): v for k, v in data.items()}
    for person, attrs in PUZZLE.items():
        got = norm.get(_fold(person), {})
        got = {_fold(k): v for k, v in got.items()} if isinstance(got, dict) else {}
        for key, want in attrs.items():
            r.add(f"{person}.{key}", 1, _fold(got.get(key, "")) == _fold(want))
    return r


task(
    id="mantik-bulmaca", category="Mantık", title="Mantık bulmacası", level=3, tools=False,
    prompt=code("""
        Ali, Berk, Cem ve Deniz farklı şehirlerde (Ankara, Bursa, İzmir, Van) yaşıyor, farklı mesleklere (doktor,
        mühendis, öğretmen, avukat) sahip ve farklı içecekler (çay, kahve, su, ayran) seviyorlar. İpuçları:
        1. Doktor Van'da yaşıyor.
        2. Ali ne doktor ne de avukat.
        3. Kahve seven kişi İzmir'de yaşıyor.
        4. Cem su seviyor.
        5. Mühendis çay seviyor ve Ankara'da yaşamıyor.
        6. Deniz İzmir'de yaşamıyor; avukat da doktor da değil.
        7. Ayran seven kişi doktor.
        8. Ankara'da yaşayan kişi avukat.
        9. Berk Bursa'da yaşamıyor.
        Herkesin şehrini, mesleğini ve içeceğini bul. Cevabının sonunda tek bir ```json bloğu ver:
        {"Ali": {"sehir": "...", "meslek": "...", "icecek": "..."}, "Berk": {...}, "Cem": {...}, "Deniz": {...}}
    """),
    grade=grade_puzzle,
    reference=lambda d: "```json\n" + __import__("json").dumps(PUZZLE, ensure_ascii=False) + "\n```",
    wrong=lambda d: "```json\n" + __import__("json").dumps(
        {**PUZZLE, "Ali": PUZZLE["Deniz"], "Deniz": PUZZLE["Ali"]}, ensure_ascii=False) + "\n```",
)
