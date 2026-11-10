from collections import defaultdict

import ayristir


def ozet(satirlar):
    """satirlar: (tarih_metni, urun, tutar_metni). Aylık toplamlar ve genel toplam."""
    aylik = defaultdict(float)
    for t, _, tt in satirlar:
        d = ayristir.tarih(t)
        aylik[f"{d.year}-{d.month:02d}"] += ayristir.tutar(tt.replace('.', '').replace(',', '.'))
    return dict(sorted(aylik.items())), round(sum(aylik.values()), 2)


def yaz(satirlar, yol):
    aylik, genel = ozet(satirlar)
    with open(yol, "w", encoding="utf-8") as f:
        for ay, t in aylik.items():
            f.write(f"{ay}: {t:.2f}\n")
        f.write(f"GENEL: {genel:.2f}\n")
