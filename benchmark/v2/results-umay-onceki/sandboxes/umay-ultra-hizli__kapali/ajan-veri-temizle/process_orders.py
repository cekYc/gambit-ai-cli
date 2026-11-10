import json
import re
from datetime import datetime

# Read the file
with open('siparisler.jsonl', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
for i, line in enumerate(lines, 1):
    print(f'Line {i}: {line.rstrip()!r}')

# Process lines
valid_records = []  # list of dict
invalid_count = 0
blank_count = 0

for line in lines:
    line_stripped = line.strip()
    
    # Skip blank lines
    if not line_stripped or line_stripped.isspace():
        blank_count += 1
        continue
    
    # Try to parse as JSON
    try:
        obj = json.loads(line_stripped)
    except json.JSONDecodeError:
        invalid_count += 1
        continue
    
    # Check required fields: id, musteri, tutar, tarih, durum
    required_fields = ['id', 'musteri', 'tutar', 'tarih', 'durum']
    if not all(field in obj for field in required_fields):
        invalid_count += 1
        continue
    
    # Parse tutar
    tutar_raw = obj['tutar']
    tutar = None
    
    if isinstance(tutar_raw, (int, float)):
        tutar = float(tutar_raw)
    elif isinstance(tutar_raw, str):
        # Remove currency symbols and spaces
        tutar_clean = tutar_raw.replace('₺', '').replace('TL', '').replace(' ', '')
        
        has_dot = '.' in tutar_clean
        has_comma = ',' in tutar_clean
        
        if has_dot and has_comma:
            # . is thousands, , is decimal
            tutar_clean = tutar_clean.replace('.', '').replace(',', '.')
        elif has_dot:
            # Only dot - check if thousands separator (3 digits after dot)
            match = re.match(r'^(\d+)\.(\d+)$', tutar_clean)
            if match:
                integer_part = match.group(1)
                decimal_part = match.group(2)
                if len(decimal_part) == 3:
                    # It's a thousands separator, remove the dot
                    tutar_clean = integer_part
                # else: dot is decimal separator, keep as is
        elif has_comma:
            # Only comma - it's decimal separator
            tutar_clean = tutar_clean.replace(',', '.')
        
        try:
            tutar = float(tutar_clean)
        except ValueError:
            invalid_count += 1
            continue
    else:
        invalid_count += 1
        continue
    
    # Parse tarih
    tarih_str = obj['tarih']
    tarih_valid = False
    normalized_tarih = None
    
    # Try YYYY-MM-DD
    try:
        dt = datetime.strptime(tarih_str, '%Y-%m-%d')
        tarih_valid = True
        normalized_tarih = dt.strftime('%Y-%m-%d')
    except ValueError:
        pass
    
    # Try YYYY/MM/DD
    if not tarih_valid:
        try:
            dt = datetime.strptime(tarih_str, '%Y/%m/%d')
            tarih_valid = True
            normalized_tarih = dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Try GG.AA.YYYY
    if not tarih_valid:
        try:
            dt = datetime.strptime(tarih_str, '%d.%m.%Y')
            tarih_valid = True
            normalized_tarih = dt.strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Try Turkish month name: G Ay YYYY
    if not tarih_valid:
        tr_months = {
            'Ocak': 1, 'Şubat': 2, 'Mart': 3, 'Nisan': 4, 'Mayıs': 5, 'Haziran': 6,
            'Temmuz': 7, 'Ağustos': 8, 'Eylül': 9, 'Ekim': 10, 'Kasım': 11, 'Aralık': 12
        }
        match = re.match(r'^(\d+)\s+(\w+)\s+(\d{4})$', tarih_str)
        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            year = int(match.group(3))
            if month_name in tr_months:
                month = tr_months[month_name]
                try:
                    dt = datetime(year, month, day)
                    tarih_valid = True
                    normalized_tarih = dt.strftime('%Y-%m-%d')
                except ValueError:
                    pass
    
    if not tarih_valid:
        invalid_count += 1
        continue
    
    # Parse durum (normalize to lowercase)
    durum = obj['durum'].lower().strip()
    
    # Trim musteri
    musteri = obj['musteri'].strip()
    
    # Record
    valid_records.append({
        'id': obj['id'],
        'musteri': musteri,
        'tutar': tutar,
        'tarih': normalized_tarih,
        'durum': durum
    })

print(f'Valid records before dedup: {len(valid_records)}')
print(f'Invalid count: {invalid_count}')
print(f'Blank count: {blank_count}')

# Deduplication: same id - keep last occurrence
last_occurrence = {}
for rec in valid_records:
    last_occurrence[rec['id']] = rec

unique_records = list(last_occurrence.values())
print(f'Unique records after dedup: {len(unique_records)}')

# Calculate metrics
# 1. gecerli_kayit
gecerli_kayit = len(unique_records)

# 2. hatali_satir
hatali_satir = invalid_count

# 3. iptal_sayisi
iptal_sayisi = sum(1 for r in unique_records if r['durum'] == 'iptal')
print(f'iptal_sayisi: {iptal_sayisi}')

# 4. toplam_tutar (iptal OLMAYAN tekil kayıtların tutar toplamı)
toplam_tutar = round(sum(r['tutar'] for r in unique_records if r['durum'] != 'iptal'), 2)
print(f'toplam_tutar: {toplam_tutar}')

# 5. aylik
aylik = {}
for r in unique_records:
    if r['durum'] != 'iptal':
        # Extract year-month from tarih (format: YYYY-MM)
        yyyy = r['tarih'][:4]
        aa = r['tarih'][5:7]  # month part
        ay_key = f'{yyyy}-{aa}'
        if ay_key not in aylik:
            aylik[ay_key] = 0.0
        aylik[ay_key] += r['tutar']

# Round to 2 decimal places
aylik_rounded = {k: round(v, 2) for k, v in aylik.items()}
print(f'aylik: {aylik_rounded}')

# 6. en_cok_harcayan
musteri_totals = {}
for r in unique_records:
    if r['durum'] != 'iptal':
        musteri = r['musteri']
        if musteri not in musteri_totals:
            musteri_totals[musteri] = 0.0
        musteri_totals[musteri] += r['tutar']

musteri_totals_rounded = {k: round(v, 2) for k, v in musteri_totals.items()}
if musteri_totals_rounded:
    en_cok_harcayan = max(musteri_totals_rounded, key=musteri_totals_rounded.get)
else:
    en_cok_harcayan = None
print(f'en_cok_harcayan: {en_cok_harcayan} with total {musteri_totals_rounded.get(en_cok_harcayan, 0) if en_cok_harcayan else 0}')

# Generate ozet.json
ozet = {
    "gecerli_kayit": gecerli_kayit,
    "hatali_satir": hatali_satir,
    "iptal_sayisi": iptal_sayisi,
    "toplam_tutar": toplam_tutar,
    "aylik": aylik_rounded,
    "en_cok_harcayan": en_cok_harcayan
}

with open('ozet.json', 'w', encoding='utf-8') as f:
    json.dump(ozet, f, ensure_ascii=False, indent=2)

print('\n ozet.json yazıldı!')
print(json.dumps(ozet, ensure_ascii=False, indent=2))