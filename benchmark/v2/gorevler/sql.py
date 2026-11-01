"""SQL: klasörde bir SQLite veritabanı (magaza.db) var; model sorguyu (araçlarla deneyerek) `cevap.sql` dosyasına yazar.
Sorgu hem bu veritabanında hem de aynı şemaya sahip, farklı verili GİZLİ bir veritabanında çalıştırılır (sonucu
ezberleyip yazmak işe yaramaz). Puan: sütun sayısı + satırların F1 benzerliği + sıralama doğruluğu."""

import random
import sqlite3
import time
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from core import Rubric, code, code_blocks, locate, read, task, write

SCHEMA = code("""
    CREATE TABLE musteriler (id INTEGER PRIMARY KEY, ad TEXT NOT NULL, sehir TEXT NOT NULL, kayit_tarihi TEXT NOT NULL);
    CREATE TABLE urunler (id INTEGER PRIMARY KEY, ad TEXT NOT NULL, kategori TEXT NOT NULL, fiyat REAL NOT NULL);
    CREATE TABLE siparisler (id INTEGER PRIMARY KEY, musteri_id INTEGER NOT NULL REFERENCES musteriler(id),
                             tarih TEXT NOT NULL);  -- 'YYYY-MM-DD'
    CREATE TABLE siparis_kalemleri (siparis_id INTEGER NOT NULL REFERENCES siparisler(id),
                                    urun_id INTEGER NOT NULL REFERENCES urunler(id),
                                    adet INTEGER NOT NULL, birim_fiyat REAL NOT NULL);
    CREATE TABLE iadeler (id INTEGER PRIMARY KEY, siparis_id INTEGER NOT NULL REFERENCES siparisler(id),
                          urun_id INTEGER NOT NULL REFERENCES urunler(id), adet INTEGER NOT NULL);
""")

NAMES = ["Ayşe", "Mehmet", "Zeynep", "Can", "Elif", "Burak", "Deniz", "Ece", "Emre", "Selin", "Kerem", "Derya",
         "Onur", "Melis", "Arda", "Gizem", "Tolga", "Buse", "Umut", "İrem", "Oğuz", "Şule"]
CITIES = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Trabzon"]
PRODUCTS = [("Laptop", "Elektronik", 32000), ("Mouse", "Elektronik", 450), ("Kulaklık", "Elektronik", 1800),
            ("Klavye", "Elektronik", 1200), ("Kitap", "Kırtasiye", 180), ("Defter", "Kırtasiye", 60),
            ("Kalem", "Kırtasiye", 25), ("Ajanda", "Kırtasiye", 180), ("Kupa", "Mutfak", 150),
            ("Termos", "Mutfak", 600), ("Tava", "Mutfak", 900), ("Yoga Matı", "Spor", 400),
            ("Dambıl", "Spor", 750), ("Çadır", "Kamp", 4200)]


def build_db(path: Path | None, seed: int) -> sqlite3.Connection:
    rnd = random.Random(seed)
    conn = sqlite3.connect(":memory:" if path is None else str(path))
    conn.executescript(SCHEMA)
    names = rnd.sample(NAMES, 18)
    for i, n in enumerate(names, 1):
        city = CITIES[i % len(CITIES)] if i <= 15 else rnd.choice(CITIES[:4])
        reg = date(2023, 1, 1) + timedelta(days=rnd.randrange(700))
        conn.execute("INSERT INTO musteriler VALUES (?,?,?,?)", (i, n, city, reg.isoformat()))
    # 'Kamp' kategorisindeki ürün hiç satılmaz (LEFT JOIN tuzağı); Trabzon'daki müşteriler sipariş vermez
    for i, (n, c, p) in enumerate(PRODUCTS, 1):
        conn.execute("INSERT INTO urunler VALUES (?,?,?,?)", (i, n, c, float(p)))
    buyers = [i for i in range(1, 19) if conn.execute("SELECT sehir FROM musteriler WHERE id=?", (i,)).fetchone()[0]
              != "Trabzon"]
    sid = 0
    for cust in buyers:
        # bazı müşteriler art arda aylarda alışveriş yapar (ardışık ay sorusu için)
        months = sorted(rnd.sample(range(24), rnd.randint(1, 7)))
        if rnd.random() < 0.45:
            start = rnd.randrange(20)
            months = sorted(set(months) | set(range(start, start + rnd.randint(3, 5))))
        for m in months:
            for _ in range(rnd.choice([1, 1, 1, 2])):
                sid += 1
                y, mo = 2024 + m // 12, m % 12 + 1
                day = rnd.randint(1, 28)
                conn.execute("INSERT INTO siparisler VALUES (?,?,?)", (sid, cust, f"{y}-{mo:02d}-{day:02d}"))
                for pid in rnd.sample(range(1, 14), rnd.randint(1, 3)):
                    base = PRODUCTS[pid - 1][2]
                    price = round(base * rnd.choice([1, 1, 0.9, 0.85, 1.1]), 2)
                    conn.execute("INSERT INTO siparis_kalemleri VALUES (?,?,?,?)", (sid, pid, rnd.randint(1, 4), price))
    rid = 0
    for s, u, a in conn.execute("SELECT siparis_id, urun_id, adet FROM siparis_kalemleri").fetchall():
        if rnd.random() < 0.12:
            for part in ([a] if a == 1 or rnd.random() < 0.6 else [1, a - 1]):  # bazen iki ayrı iade satırı
                rid += 1
                conn.execute("INSERT INTO iadeler VALUES (?,?,?,?)", (rid, s, u, part))
    conn.commit()
    return conn


VISIBLE_SEED, HIDDEN_SEED = 2026, 917

SQL_NOTE = code("""
    Bu klasördeki `magaza.db` SQLite veritabanının şeması:
    ```sql
    {schema}
    ```
    Soru: {q}
    Tek bir SQL sorgusu yaz (WITH/CTE ve pencere fonksiyonları kullanılabilir; SQLite 3.50) ve sorguyu bu klasörde
    `cevap.sql` dosyasına kaydet. Sorguyu veritabanında deneyebilirsin (ör. Python'un sqlite3 modülüyle küçük bir
    betik yazarak). Sorgun aynı şemaya sahip ama verisi farklı başka bir veritabanında da çalıştırılıp puanlanacak;
    sonuçları elle yazma. Sütunların sırası ve sayısı istendiği gibi olmalı; sütun adları önemli değil.
""")


def _norm(row) -> tuple:
    return tuple(round(float(v), 2) if isinstance(v, (int, float)) and not isinstance(v, bool) else
                 (v.strip() if isinstance(v, str) else v) for v in row)


def _execute(conn: sqlite3.Connection, query: str) -> list[tuple]:
    allowed = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION, getattr(sqlite3, "SQLITE_RECURSIVE", 33)}
    conn.set_authorizer(lambda action, *_: sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY)
    deadline = time.monotonic() + 15
    conn.set_progress_handler(lambda: int(time.monotonic() > deadline), 10_000)
    try:
        return [_norm(r) for r in conn.execute(query).fetchall()]
    finally:
        conn.set_authorizer(None)
        conn.set_progress_handler(None, 0)


def compare_rows(got: list[tuple], want: list[tuple], ordered: bool) -> tuple[float, str]:
    if got == want:
        return 1.0, ""
    cols = 0.15 if (got and want and len(got[0]) == len(want[0])) or (not got and not want) else 0.0
    cg, cw = Counter(got), Counter(want)
    common = sum((cg & cw).values())
    f1 = 2 * common / (len(got) + len(want)) if got or want else 1.0
    order = 0.2 if (not ordered and cg == cw) else 0.0
    note = f"beklenen {len(want)} satır (ilk: {want[:2]}), sonuç {len(got)} satır (ilk: {got[:2]})"
    return min(0.95, cols + 0.65 * f1 + order), note


def extract_query(d: Path, answer: str) -> tuple[str, float, str]:
    f, factor, where = locate(d, "cevap.sql")
    if f and read(f).strip():
        text = read(f)
        fenced = [b for _, b in code_blocks(text)]
        return (fenced[-1] if fenced else text), factor, where
    blocks = [b for tag, b in code_blocks(answer) if tag in ("sql", "sqlite")]
    if blocks:
        return blocks[-1], 0.7, "cevap.sql yok; cevaptaki sorgu kullanıldı"
    return "", 0.0, "cevap.sql yok"


def make(id_: str, title: str, level: int, question: str, reference: str, ordered: bool = True,
         wrong_sql: str = "") -> None:
    def grade(d: Path, answer: str, trace) -> Rubric:
        r = Rubric()
        query, factor, note = extract_query(d, answer)
        query = query.strip().rstrip(";").strip()
        if note:
            r.gate(note, factor)
        for label, seed, w in (("bu veritabanı", VISIBLE_SEED, 1.0), ("gizli veritabanı", HIDDEN_SEED, 1.5)):
            conn = build_db(None, seed)
            try:
                want = [_norm(x) for x in conn.execute(reference).fetchall()]
                if not query:
                    r.add(label, w, 0)
                    continue
                try:
                    got = _execute(conn, query)
                except (sqlite3.Error, sqlite3.Warning) as e:
                    r.add(label, w, 0, f"SQL hatası: {str(e)[:120]}")
                    continue
                score, why = compare_rows(got, want, ordered)
                r.add(label, w, score, why[:200])
            finally:
                conn.close()
        return r

    def apply_ref(d: Path) -> str:
        write(d / "cevap.sql", reference + "\n")
        return "cevap.sql yazıldı."

    def wrong(d: Path) -> str:
        bad = wrong_sql or (reference.replace("DESC", "ASC") if "DESC" in reference else reference + " LIMIT 2")
        write(d / "cevap.sql", bad + "\n")
        return "cevap.sql yazıldı."

    def setup(d: Path) -> None:
        build_db(d / "magaza.db", VISIBLE_SEED).close()

    task(id=id_, category="SQL", title=title, level=level, setup=setup, grade=grade, reference=apply_ref, wrong=wrong,
         prompt=SQL_NOTE.format(schema=SCHEMA, q=question))


REVENUE = "SUM(k.adet * k.birim_fiyat)"

make("sql-sehir-ciro", "Şehir cirosu (sıfırlar dahil)", 2, code("""
    Her şehir için: şehir adı, o şehirden EN AZ BİR sipariş vermiş farklı müşteri sayısı ve şehrin toplam cirosu
    (ciro = siparis_kalemleri.adet × siparis_kalemleri.birim_fiyat toplamı, 2 ondalığa yuvarlanmış; iadeleri dikkate
    alma). Müşterisi olup hiç sipariş gelmemiş şehirler de 0 müşteri ve 0 ciroyla listede olsun. Ciroya göre azalan,
    eşitlikte şehir adına göre artan sırala.
"""), code(f"""
    SELECT m.sehir, COUNT(DISTINCT s.musteri_id), ROUND(COALESCE({REVENUE}, 0), 2) AS ciro
    FROM musteriler m LEFT JOIN siparisler s ON s.musteri_id = m.id LEFT JOIN siparis_kalemleri k ON k.siparis_id = s.id
    GROUP BY m.sehir ORDER BY ciro DESC, m.sehir
"""))

make("sql-net-satis", "İade düşülmüş net satış", 3, code("""
    Her ürün için net satış adedini ve net ciroyu hesapla: net adet = satılan toplam adet − iade edilen toplam adet;
    net ciro = her sipariş kaleminin (adet − o sipariş ve ürün için iade edilen adet) × birim_fiyat toplamı
    (bir sipariş kalemine ait birden fazla iade satırı olabilir). En yüksek net ciroya sahip 5 ürünü listele.
    Sütunlar: ürün adı, net adet, net ciro (2 ondalık). Net ciroya göre azalan, eşitlikte ürün adına göre artan sırala.
"""), code("""
    WITH iade AS (SELECT siparis_id, urun_id, SUM(adet) AS adet FROM iadeler GROUP BY siparis_id, urun_id)
    SELECT u.ad, SUM(k.adet - COALESCE(i.adet, 0)) AS net_adet,
           ROUND(SUM((k.adet - COALESCE(i.adet, 0)) * k.birim_fiyat), 2) AS net_ciro
    FROM siparis_kalemleri k JOIN urunler u ON u.id = k.urun_id
    LEFT JOIN iade i ON i.siparis_id = k.siparis_id AND i.urun_id = k.urun_id
    GROUP BY u.id ORDER BY net_ciro DESC, u.ad LIMIT 5
"""))

make("sql-kategori-pay", "Kategori payı ve sıralama", 3, code("""
    2025 yılındaki siparişler için (siparisler.tarih 2025 ile başlayan) her kategorinin cirosunu, toplam 2025
    cirosu içindeki yüzde payını (1 ondalığa yuvarlanmış, ör. 23.4) ve ciroya göre sırasını (DENSE_RANK; en yüksek
    ciro 1) listele. 2025'te hiç satışı olmayan kategoriler de 0 ciro ve 0.0 payla listede olsun (sıraları da
    DENSE_RANK ile verilsin). Sütunlar: kategori, ciro (2 ondalık), yüzde, sıra. Sıraya, eşitlikte kategori adına
    göre artan sırala.
"""), code(f"""
    WITH c AS (
      SELECT u.kategori, COALESCE(SUM(CASE WHEN s.tarih LIKE '2025%' THEN k.adet * k.birim_fiyat END), 0) AS ciro
      FROM urunler u LEFT JOIN siparis_kalemleri k ON k.urun_id = u.id LEFT JOIN siparisler s ON s.id = k.siparis_id
      GROUP BY u.kategori)
    SELECT kategori, ROUND(ciro, 2), ROUND(100.0 * ciro / (SELECT SUM(ciro) FROM c), 1),
           DENSE_RANK() OVER (ORDER BY ciro DESC) AS sira
    FROM c ORDER BY sira, kategori
"""))

ARDISIK_REF = code("""
    WITH ay AS (
      SELECT DISTINCT musteri_id, CAST(substr(tarih, 1, 4) AS INTEGER) * 12 + CAST(substr(tarih, 6, 2) AS INTEGER) - 1 AS n
      FROM siparisler),
    grp AS (
      SELECT musteri_id, n, n - ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY n) AS g FROM ay),
    seri AS (
      SELECT musteri_id, COUNT(*) AS uzunluk, MIN(n) AS bas FROM grp GROUP BY musteri_id, g),
    enuzun AS (
      SELECT musteri_id, uzunluk, bas,
             ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY uzunluk DESC, bas) AS r FROM seri)
    SELECT m.ad, e.uzunluk, printf('%04d-%02d', e.bas / 12, e.bas % 12 + 1)
    FROM enuzun e JOIN musteriler m ON m.id = e.musteri_id
    WHERE e.r = 1 AND e.uzunluk >= 3
    ORDER BY e.uzunluk DESC, m.ad
""")
make("sql-ardisik-ay", "Ardışık aylar (gaps & islands)", 4, code("""
    Her müşteri için, sipariş verdiği takvim aylarından oluşan EN UZUN ardışık ay serisini bul (ör. 2024-11,
    2024-12, 2025-01 üç aylık seridir; aynı ay içindeki birden fazla sipariş tek ay sayılır). En uzun serisi en az
    3 ay olan müşterileri listele. Sütunlar: müşteri adı, seri uzunluğu (ay), serinin başladığı ay ('YYYY-MM').
    Bir müşterinin aynı uzunlukta birden fazla en uzun serisi varsa en erken başlayanı ver. Seri uzunluğuna göre
    azalan, eşitlikte müşteri adına göre artan sırala.
"""), ARDISIK_REF,
     wrong_sql=ARDISIK_REF.replace("e.uzunluk >= 3", "e.uzunluk >= 4"))

make("sql-medyan", "Şehir bazında medyan sipariş", 4, code("""
    Her siparişin tutarı, kalemlerinin adet × birim_fiyat toplamıdır (iadeleri dikkate alma). Her şehir için o
    şehirdeki müşterilerin siparişlerinin sipariş sayısını ve sipariş tutarlarının MEDYANINI hesapla (çift sayıda
    siparişte ortadaki iki değerin ortalaması). SQLite'ta hazır MEDIAN fonksiyonu yok. Yalnızca en az 2 siparişi olan
    şehirleri listele. Sütunlar: şehir, sipariş sayısı, medyan (2 ondalık). Medyana göre azalan, eşitlikte şehir
    adına göre artan sırala.
"""), code("""
    WITH t AS (
      SELECT m.sehir, s.id, SUM(k.adet * k.birim_fiyat) AS tutar
      FROM siparisler s JOIN musteriler m ON m.id = s.musteri_id JOIN siparis_kalemleri k ON k.siparis_id = s.id
      GROUP BY s.id),
    r AS (
      SELECT sehir, tutar, ROW_NUMBER() OVER (PARTITION BY sehir ORDER BY tutar) AS rn,
             COUNT(*) OVER (PARTITION BY sehir) AS n FROM t)
    SELECT sehir, n, ROUND(AVG(tutar), 2) AS medyan FROM r
    WHERE n >= 2 AND rn IN ((n + 1) / 2, (n + 2) / 2)
    GROUP BY sehir ORDER BY medyan DESC, sehir
"""))
