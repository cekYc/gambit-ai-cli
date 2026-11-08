import json
import re
from datetime import datetime
from collections import defaultdict

# Türkçe ay isimleri
turkce_aylar = {
    'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4, 'mayıs': 5, 'haziran': 6,
    'temmuz': 7, 'ağustos': 8, 'eylül': 9, 'ekim': 10, 'kasım': 11, 'aralık': 12
}

def parse_tutar(val):
    """Tutar değerini float'a çevirir. Geçersizse None döner."""
    if isinstance(val, (int, float)):
        return float(val)
    if not isinstance(val, str):
        return None
    s = val.strip().replace('₺', '').replace('TL', '').replace(' ', '')
    if not s:
        return None
    # Hem . hem , varsa -> . binlik, , ondalık
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        # Sadece virgül varsa ondalık ayırıcı
        s = s.replace(',', '.')
    elif '.' in s:
        # Sadece nokta varsa
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3:
            # Noktadan sonra tam 3 rakam -> binlik ayırıcı
            s = s.replace('.', '')
        else:
            # Değilse ondalık ayırıcı (zaten . olarak kalır)
            pass
    try:
        return float(s)
    except ValueError:
        return None

def parse_tarih(val):
    """Tarih değerini datetime'a çevirir. Geçersizse None döner."""
    if not isinstance(val, str):
        return None
    s = val.strip()
    if not s:
        return None
    # YYYY-MM-DD
    for fmt in ('%Y-%m-%d', '%Y/%m/%d', '%d.%m.%Y'):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    # Türkçe ay adı: G Ay YYYY
    match = re.match(r'^(\d{1,2})\s+(\w+)\s+(\d{4})$', s, re.IGNORECASE)
    if match:
        gun = int(match.group(1))
        ay_str = match.group(2).lower()
        yil = int(match.group(3))
        if ay_str in turkce_aylar:
            ay = turkce_aylar[ay_str]
            try:
                return datetime(yil, ay, gun)
            except ValueError:
                return None
    return None

with open('siparisler.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

gecerli_kayitlar = {}
hatali_satir = 0

for i, line in enumerate(lines, 1):
    line = line.rstrip('\n')
    # Boş ya da sadece boşluk içeren satırları yok say
    if not line.strip():
        continue
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        hatali_satir += 1
        continue
    # Gerekli alanlar var mı?
    required = ['id', 'musteri', 'tutar', 'tarih', 'durum']
    if not all(k in obj for k in required):
        hatali_satir += 1
        continue
    # Tutar parse et
    tutar = parse_tutar(obj['tutar'])
    if tutar is None:
        hatali_satir += 1
        continue
    # Tarih parse et
    tarih = parse_tarih(obj['tarih'])
    if tarih is None:
        hatali_satir += 1
        continue
    # Durum normalize et
    durum = str(obj['durum']).strip().lower()
    # Müşteri adı temizle
    musteri = str(obj['musteri']).strip()
    # Geçerli kayıt (aynı id varsa sonuncusu geçerli)
    gecerli_kayitlar[obj['id']] = {
        'id': obj['id'],
        'musteri': musteri,
        'tutar': tutar,
        'tarih': tarih,
        'durum': durum
    }

# Sonuçları hesapla
gecerli_sayisi = len(gecerli_kayitlar)
iptal_sayisi = sum(1 for r in gecerci_kayitlar.values() if r['durum'] == 'iptal')

# İptal olmayanlar
iptal_olmayanlar = [r for r in gecerci_kayitlar.values() if r['durum'] != 'iptal']

toplam_tutar = round(sum(r['tutar'] for r in iptal_olmayanlar), 2)

# Aylık toplamlar
aylik = defaultdict(float)
for r in iptal_olmayanlar:
    key = r['tarih'].strftime('%Y-%m')
    aylik[key] += r['tutar']
aylik = {k: round(v, 2) for k, v in sorted(aylik.items())}

# En çok harcanan müşteri
musteri_toplam = defaultdict(float)
for r in iptal_olmayanlar:
    musteri_toplam[r['musteri']] += r['tutar']
if musteri_toplam:
    en_cok_harcayan = max(musteri_toplam.items(), key=lambda x: x[1])[0]
else:
    en_cok_harcayan = ''

sonuc = {
    'gecerli_kayit': gecerli_sayisi,
    'hatali_satir': hatali_satir,
    'iptal_sayisi': iptal_sayisi,
    'toplam_tutar': toplam_tutar,
    'aylik': aylik,
    'en_cok_harcayan': en_cok_harcayan
}

print(json.dumps(sonuc, ensure_ascii=False, indent=2))

with open('ozet.json', 'w', encoding='utf-8') as f:
    json.dump(sonuc, f, ensure_ascii=False, indent=2)

print('\n--- Detaylı kayıtlar ---')
for r in sorted(gecerci_kayitlar.values(), key=lambda x: x['id']):
    print(f"ID: {r['id']}, Müşteri: {r['musteri']}, Tutar: {r['tutar']}, Tarih: {r['tarih'].strftime('%Y-%m-%d')}, Durum: {r['durum']}")