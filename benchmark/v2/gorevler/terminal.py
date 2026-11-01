"""Terminal: model işi gambit'in run_command aracıyla (PowerShell) kendisi yapar; puan klasörün son durumundan
verilir. Her dosya/satır ayrı bir rubrik maddesidir; yarım iş yarım puan alır."""

import csv
import hashlib
import io
import re
from pathlib import Path

from core import Rubric, code, locate, read, task, write

TERM_NOTE = ("Windows'ta PowerShell 7 kullanıyorum; bulunduğun klasörde çalış. İşi araçlarınla (run_command, gerekirse "
             "küçük bir betik) kendin yap, sonra sonucu kontrol et. Bu klasörün dışına dokunma.")

# ---------------------------------------------------------------- log raporu

LOGS = {
    "api.log": ["# log başlangıcı", "2026-10-01 10:00:01 INFO Sunucu başladı", "2026-10-01 10:00:02 INFO ERROR sayacı sıfırlandı",
                "2026-10-01 10:00:05 ERROR Veritabanına bağlanılamadı", "2026-10-01 10:00:09 WARN Yeniden deneniyor",
                "2026-10-01 10:00:15 ERROR Zaman aşımı", "", "2026-10-01 10:01:00 INFO Bağlantı kuruldu",
                "2026-10-01 10:02:00 WARNING Eski yapılandırma", "2026-10-01 10:03:00 error küçük harfli seviye"],
    "web.log": ["2026-10-02 08:00:00 INFO İstek alındı", "2026-10-02 08:00:01 INFO İstek alındı",
                "2026-10-02 08:05:12 ERROR Dosya bulunamadı: rapor.pdf", "2026-10-02 08:05:13 WARN Yavaş yanıt (2300 ms)",
                "2026-10-02 08:06:00 WARN Yavaş yanıt (2100 ms)", "2026-10-02 08:10:00 INFO WARN eşiği güncellendi"],
    "eski/worker.log": ["2026-09-01 12:00:00 INFO Eski kayıt", "2026-09-01 12:00:01 ERROR Kuyruk dolu",
                        "2026-09-01 12:00:02 ERROR Kuyruk dolu", "2026-09-01 12:00:03 ERROR Görev düştü"],
    "eski/bos.log": [],
    "eski/derin/cron.log": ["2026-08-01 00:00:00 INFO Zamanlayıcı çalıştı", "2026-08-01 00:00:00 WARN Atlanan görev"],
}
LOG_DECOYS = {"api.log.1": ["2026-09-30 23:59:59 ERROR döndürülmüş dosya"],
              "notlar.txt": ["2026-10-01 10:00:00 ERROR bu bir log dosyası değil"]}


def _log_expected() -> list[list[str]]:
    rows = []
    for name, lines in LOGS.items():
        levels = [ln.split()[2] if len(ln.split()) > 2 else "" for ln in lines]
        rows.append([name, str(levels.count("ERROR")), str(levels.count("WARN")), str(levels.count("INFO"))])
    return sorted(rows, key=lambda r: (-int(r[1]), r[0]))


def setup_logs(d: Path) -> None:
    for name, lines in {**LOGS, **LOG_DECOYS}.items():
        write(d / "loglar" / name, "\n".join(lines) + ("\n" if lines else ""))


def grade_logs(d: Path, answer: str, trace) -> Rubric:
    r = Rubric()
    f, factor, where = locate(d, "rapor.csv")
    if not f:
        return r.add("rapor.csv var", 1, 0).gate("rapor.csv yok", 0.0)
    if where:
        r.gate(where, factor)
    rows = [[c.strip() for c in row] for row in csv.reader(io.StringIO(read(f))) if any(c.strip() for c in row)]
    expected = _log_expected()
    r.add("başlık satırı", 1, bool(rows) and [c.lower() for c in rows[0]] == ["dosya", "error", "warn", "info"])
    body = [[c.replace("\\", "/").removeprefix("./").removeprefix("loglar/") for c in row] for row in rows[1:]]
    got = {row[0]: row[1:] for row in body if row}
    for name, *counts in expected:
        have = got.get(name)
        value = sum(a == b for a, b in zip(have, counts)) / 3 if have and len(have) == 3 else 0.0
        r.add(f"{name} satırı", 1.5, value, "" if value == 1 else f"beklenen {counts}, bulunan {have}")
    r.add("fazla satır yok (.log.1/.txt dahil edilmemiş)", 1, len(body) == len(expected) and set(got) == {e[0] for e in expected})
    r.add("sıralama (error azalan, dosya artan)", 1.5, [row[0] for row in body] == [e[0] for e in expected])
    return r


def ref_logs(d: Path) -> str:
    write(d / "rapor.csv", "dosya,error,warn,info\n" + "".join(",".join(row) + "\n" for row in _log_expected()))
    return "rapor.csv oluşturuldu."


task(
    id="term-log-rapor", category="Terminal", title="Log seviyelerini sayıp CSV rapor", level=2,
    prompt=code("""
        `loglar` klasöründeki (alt klasörler dahil) her `.log` dosyası için ERROR, WARN ve INFO satırlarını say ve bu
        klasörde `rapor.csv` dosyası oluştur. Satır biçimi: `TARİH SAAT SEVİYE mesaj`; yalnızca SEVİYE alanı (3. alan)
        tam olarak ERROR, WARN ya da INFO olan satırlar sayılır (büyük/küçük harf duyarlı; mesajın içinde geçmesi
        sayılmaz). Sadece uzantısı tam olarak `.log` olan dosyalar (`.log.1` gibi döndürülmüş dosyalar hariç).
        CSV başlığı `dosya,error,warn,info` olsun; dosya sütunu `loglar` klasörüne göre göreli yol, ayırıcı `/`
        (ör. `eski/worker.log`). Boş log dosyası da 0'larla listelensin. Satırları error sayısına göre azalan,
        eşitlikte dosya yoluna göre artan sırala.
    """) + "\n" + TERM_NOTE,
    setup=setup_logs, grade=grade_logs, reference=ref_logs,
    wrong=lambda d: (write(d / "rapor.csv", "dosya,error,warn,info\napi.log,3,1,3\nweb.log,1,2,3\n"), "")[1],
)

# ---------------------------------------------------------------- fotoğraf arşivi

MEDIA = {
    "IMG_20240312_101500.jpg": "arsiv/2024/03/IMG_20240312_101500.jpg",
    "IMG_20240312_101501.jpg": "arsiv/2024/03/IMG_20240312_101501.jpg",
    "VID_20231225_200000.mp4": "arsiv/2023/12/VID_20231225_200000.mp4",
    "Screenshot_2024-01-05-10-00-00.png": "arsiv/2024/01/Screenshot_2024-01-05-10-00-00.png",
    "PXL_20250701_093000123.jpg": "arsiv/2025/07/PXL_20250701_093000123.jpg",
    "IMG_20240630_120000.JPG": "arsiv/2024/06/IMG_20240630_120000.JPG",
    "tatil/DSC_20221111.jpeg": "arsiv/2022/11/DSC_20221111.jpeg",
    "tatil/klip.mov": "arsiv/tarihsiz/klip.mov",
    "IMG_hatali.jpg": "arsiv/tarihsiz/IMG_hatali.jpg",
}
OTHERS = ["belge_20240312.pdf", "notlar.txt", "tatil/rota.txt"]


def _content(name: str) -> bytes:
    return hashlib.sha256(name.encode()).digest() * 40 + name.encode()


def setup_media(d: Path) -> None:
    for name in [*MEDIA, *OTHERS]:
        p = d / "gelen" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(_content(name))


def grade_media(d: Path, answer: str, trace) -> Rubric:
    r = Rubric()
    # arşiv kökü: ./arsiv; model onu başka bir klasörün altına (ör. gelen/arsiv) kurduysa x0,9 ile kabul
    roots = [d] + sorted({q.parent for q in d.rglob("arsiv") if q.is_dir() and q.parent != d}, key=lambda q: len(q.parts))
    count = lambda root: sum((root / dst).is_file() for dst in MEDIA.values())  # noqa: E731
    root = max(roots, key=count)
    if root != d and count(root) > count(d):
        r.gate(f"arşiv alt klasöre kurulmuş: {(root / 'arsiv').relative_to(d).as_posix()}", 0.9)
    else:
        root = d
    for src, dst in MEDIA.items():
        p = root / dst
        ok = p.is_file() and p.read_bytes() == _content(src)
        moved = not (d / "gelen" / src).exists()
        r.add(f"{Path(src).name} → {dst}", 1, 1.0 if ok and moved else (0.5 if ok else 0.0))
    if not count(root):
        r.gate("hiçbir medya dosyası arşivlenmemiş", 0.0)
    others_ok = all((d / "gelen" / o).is_file() and (d / "gelen" / o).read_bytes() == _content(o) for o in OTHERS)
    r.add("medya olmayan dosyalar yerinde", 1.5, others_ok)
    expected = {_content(n) for n in [*MEDIA, *OTHERS]}
    found = [p.read_bytes() for p in d.rglob("*") if p.is_file() and p.suffix.lower() not in (".ps1", ".py")]
    found = [b for b in found if b in expected]
    r.add("hiçbir dosya kaybolmamış/çoğalmamış", 1.5, len(found) == len(expected) and set(found) == expected)
    return r


def ref_media(d: Path) -> str:
    for src, dst in MEDIA.items():
        (d / dst).parent.mkdir(parents=True, exist_ok=True)
        (d / "gelen" / src).rename(d / dst)
    return "Taşındı."


task(
    id="term-arsiv", category="Terminal", title="Fotoğrafları tarihe göre arşivleme", level=3,
    prompt=code("""
        `gelen` klasöründeki (alt klasörler dahil) fotoğraf ve videoları tarihe göre arşivle. Medya dosyası: uzantısı
        .jpg, .jpeg, .png, .mp4 ya da .mov olan dosya (büyük/küçük harf fark etmez). Dosyanın tarihi ADINDAN çıkar:
        addaki ilk `YYYYMMDD` (8 rakam, 20 ile başlayan) ya da `YYYY-MM-DD` kalıbı. Tarihli medya dosyalarını
        `arsiv/YYYY/MM/` klasörüne (bu klasörün altında), tarihi bulunamayanları `arsiv/tarihsiz/` klasörüne aynı
        adla TAŞI. Medya olmayan dosyalar (adında tarih olsa bile) yerinde kalsın. Dosya içerikleri değişmemeli.
    """) + "\n" + TERM_NOTE,
    setup=setup_media, grade=grade_media, reference=ref_media,
    wrong=lambda d: (ref_media(d), (d / "arsiv/2024/06/IMG_20240630_120000.JPG").rename(d / "gelen/IMG_20240630_120000.JPG"),
                     (d / "gelen/belge_20240312.pdf").rename(d / "arsiv/2024/03/belge_20240312.pdf"), "")[-1],
)

# ---------------------------------------------------------------- ini güncelleme

INI_FILES = {
    "servisler/api.ini": ("\n", False, code("""
        [genel]
        ad=api
        port=5432

        [veritabani]
        host=db.local
        port=5432
        kullanici=api

        [onbellek]
        port=5432
    """) + "\n"),
    "servisler/odeme/odeme.ini": ("\r\n", False, code("""
        ; ödeme servisi
        [veritabani]
        host = db2.local
        port = 5432

        [kuyruk]
        port = 5432
    """) + "\n"),
    "servisler/rapor.ini": ("\n", True, code("""
        [Veritabani]
        ; port=5432 eski değer, yorum satırı
        port=5432
        isim=rapor
    """) + "\n"),
    "servisler/web.ini": ("\n", False, "[genel]\nport=5432\n"),
    "servisler/yedek/api.ini": ("\n", False, "[veritabani]\nport=5432\n"),
}
INI_CHANGED = {"servisler/api.ini", "servisler/odeme/odeme.ini", "servisler/rapor.ini"}


def _ini_bytes(text: str, nl: str, bom: bool) -> bytes:
    return (b"\xef\xbb\xbf" if bom else b"") + text.replace("\n", nl).encode("utf-8")


def _ini_target(name: str) -> bytes:
    nl, bom, text = INI_FILES[name]
    if name in INI_CHANGED:
        out, section = [], ""
        for line in text.split("\n"):
            if m := re.match(r"\s*\[(.+)\]\s*$", line):
                section = m.group(1).lower()
            elif section == "veritabani" and re.match(r"\s*port\s*=\s*5432\s*$", line):
                line = re.sub(r"5432", "6543", line)
            out.append(line)
        text = "\n".join(out)
    return _ini_bytes(text, nl, bom)


def setup_ini(d: Path) -> None:
    for name, (nl, bom, text) in INI_FILES.items():
        p = d / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(_ini_bytes(text, nl, bom))


def grade_ini(d: Path, answer: str, trace) -> Rubric:
    r = Rubric()
    original = {n: _ini_bytes(INI_FILES[n][2], INI_FILES[n][0], INI_FILES[n][1]) for n in INI_CHANGED}
    if not any((d / n).is_file() and (d / n).read_bytes() != original[n] for n in INI_CHANGED):
        r.gate("hiçbir dosya güncellenmemiş", 0.0)
    for name in INI_FILES:
        p = d / name
        want = _ini_target(name)
        if not p.is_file():
            r.add(name, 2 if name in INI_CHANGED else 1, 0, "dosya yok")
            continue
        got = p.read_bytes()
        loose = lambda b: b.removeprefix(b"\xef\xbb\xbf").replace(b"\r\n", b"\n").rstrip(b"\n")  # noqa: E731
        if got == want:
            value, note = 1.0, ""
        elif loose(got) == loose(want):
            value, note = 0.6, "içerik doğru ama satır sonu/BOM korunmamış"
        else:
            value, note = 0.0, "içerik yanlış"
        r.add(name + (" güncellendi" if name in INI_CHANGED else " değişmedi"), 2 if name in INI_CHANGED else 1, value, note)
    return r


def ref_ini(d: Path) -> str:
    for name in INI_CHANGED:
        (d / name).write_bytes(_ini_target(name))
    return "Güncellendi."


task(
    id="term-ini", category="Terminal", title="INI dosyalarında bölüme özel değişiklik", level=3,
    prompt=code("""
        `servisler` klasöründeki (alt klasörler dahil, ancak `servisler/yedek` HARİÇ) tüm `.ini` dosyalarında YALNIZCA
        `[veritabani]` bölümündeki (bölüm adı büyük/küçük harf duyarsız) `port` değerini 5432'den 6543'e değiştir.
        Diğer bölümlerdeki port satırlarına, yorum satırlarına (`;` ile başlayan) ve `servisler/yedek` içindeki
        dosyalara dokunma. Satırların geri kalan biçimi (= etrafındaki boşluklar), dosyaların satır sonu türü
        (LF/CRLF) ve UTF-8 BOM varsa BOM'u aynen korunmalı; başka hiçbir bayt değişmemeli.
    """) + "\n" + TERM_NOTE,
    setup=setup_ini, grade=grade_ini, reference=ref_ini,
    wrong=lambda d: ([(d / n).write_bytes(_ini_target(n).replace(b"\r\n", b"\n").removeprefix(b"\xef\xbb\xbf"))
                      for n in INI_CHANGED], (d / "servisler/web.ini").write_text("[genel]\nport=6543\n"), "")[-1],
)

# ---------------------------------------------------------------- kopya dosyalar

DUP_FILES = {
    "foto/a.jpg": b"AAAA" * 500, "yedek/a_kopya.jpg": b"AAAA" * 500, "yedek/eski/a.jpg": b"AAAA" * 500,
    "belge/rapor.txt": "Yıllık rapor\n".encode(), "belge/rapor_v2.txt": "Yıllık rapor (düzeltilmiş)\n".encode(),
    "arsiv/rapor.txt": "Yıllık rapor\n".encode(),
    "foto/b.png": b"BBBB" * 300, "foto/c.png": b"BBBB" * 299 + b"BBBC",
    "bos1.txt": b"", "belge/bos2.txt": b"",
    "muzik/s1.mp3": b"\x00\x01" * 2048, "muzik/s2.mp3": b"\x00\x01" * 2047 + b"\x00\x02",
    "tek.bin": b"\xff" * 10,
    "yedek/b_kopya.png": b"BBBB" * 300,
}


def _dup_groups() -> list[list[str]]:
    by: dict[bytes, list[str]] = {}
    for n, c in DUP_FILES.items():
        by.setdefault(c, []).append(n)
    return sorted(sorted(g) for g in by.values() if len(g) > 1)


def setup_dups(d: Path) -> None:
    for name, data in DUP_FILES.items():
        p = d / "dosyalar" / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)


def grade_dups(d: Path, answer: str, trace) -> Rubric:
    r = Rubric()
    f, factor, where = locate(d, "kopyalar.txt")
    if not f:
        return r.add("kopyalar.txt var", 1, 0).gate("kopyalar.txt yok", 0.0)
    if where:
        r.gate(where, factor)
    lines = [ln.strip() for ln in read(f).splitlines() if ln.strip()]
    got = [[p.strip().replace("\\", "/").removeprefix("./").removeprefix("dosyalar/") for p in ln.split("|")] for ln in lines]
    got_sets = [frozenset(g) for g in got]
    expected = _dup_groups()
    for g in expected:
        r.add(" | ".join(g), 1.5, frozenset(g) in got_sets)
    extra = [g for g in got_sets if g not in {frozenset(e) for e in expected}]
    r.add("yanlış/fazla grup yok", 1.5, max(0.0, 1 - 0.5 * len(extra)), f"fazla: {[sorted(x) for x in extra][:2]}" if extra else "")
    r.add("biçim: grup içi ve gruplar sıralı", 1, got == expected)
    r.add("dosyalar değişmemiş", 1, all((d / "dosyalar" / n).is_file() and (d / "dosyalar" / n).read_bytes() == c
                                        for n, c in DUP_FILES.items()))
    return r


def ref_dups(d: Path) -> str:
    write(d / "kopyalar.txt", "".join(" | ".join(g) + "\n" for g in _dup_groups()))
    return "kopyalar.txt yazıldı."


task(
    id="term-kopyalar", category="Terminal", title="İçeriği aynı dosyaları bulma", level=3,
    prompt=code("""
        `dosyalar` klasöründe (alt klasörler dahil) İÇERİĞİ birebir aynı olan dosya gruplarını bul (ad ya da boyut
        benzerliği yetmez; içerik aynı olmalı. Boş dosyalar da birbirinin kopyasıdır). Bu klasörde `kopyalar.txt`
        dosyası oluştur: her satır bir grup, gruptaki dosyaların `dosyalar` klasörüne göre göreli yolları (ayırıcı `/`)
        alfabetik sırayla ve ` | ` ile ayrılmış (ör. `a/x.txt | b/y.txt`). Yalnızca en az 2 dosyalı gruplar; satırlar
        da alfabetik sıralı (her satırın ilk yoluna göre). Hiçbir dosyayı değiştirme ya da silme.
    """) + "\n" + TERM_NOTE,
    setup=setup_dups, grade=grade_dups, reference=ref_dups,
    wrong=lambda d: (write(d / "kopyalar.txt", "foto/a.jpg | yedek/a_kopya.jpg\nbelge/rapor.txt | belge/rapor_v2.txt\n"), "")[1],
)
