def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    if not text:
        return []

    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    i = 0
    text_len = len(text)

    while i < text_len:
        char = text[i]

        if in_quotes:
            if char == '"':
                # Escaped quote ("" -> ")
                if i + 1 < text_len and text[i + 1] == '"':
                    current_field += '"'
                    i += 2
                    continue
                else:
                    # Kapatıcı tırnak
                    in_quotes = False
            else:
                current_field += char
        else:  # Tırnak içinde değil
            if char == delimiter:
                current_record.append(current_field)
                current_field = ""
            elif char == '\n' or (char == '\r' and i + 1 < text_len and text[i + 1] == '\n'):
                # Satır sonu tespiti
                is_rn = char == '\r' and i + 1 < text_len and text[i + 1] == '\n'
                line_end_len = 2 if is_rn else 1
                
                # Kural: Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz.
                if i < text_len - 1: # Eğer metin bu satır sonundan sonra devam ediyorsa, kayıt biter.
                    current_record.append(current_field)
                    records.append(current_record)
                    # Yeni kayıt için sıfırlama
                    current_record = []
                    current_field = ""
                    i += line_end_len - 1 # Döngü sonunda +1 yapıldığı için son karakteri atlayalım
                    continue
                # Eğer son satır sonu ise, kayıt eklenmez (kurala uygun).
            else:
                # Normal karakter
                current_field += char
        
        i += 1

    # Döngü bittikten sonra kalan alanı kaydet (son alan)
    if text_len > 0:
        # Kural: Son satır sonu yeni kayıt oluşturmaz. Eğer metin satır sonuyla bitmiyorsa, son alanı ekle.
        if not (text.endswith('\n') or text.endswith('\r\n')):
            current_record.append(current_field)
            records.append(current_record)
        # Eğer tek satır ve satır sonuyla bitiyorsa ve records boşsa, tek kayıt olarak ekle (ortadaki boş satır kuralı için).
        elif not records and current_field:
             records.append([current_field])

    # Hata Kontrolü 1: Kapanmayan tırnak
    if in_quotes:
        raise ValueError("Hatalı girdi: Kapanmayan tırnak")

    return records

# --- Test Senaryoları ---
tests = {
    "Basic": ("a,b\nc,d", [['a', 'b'], ['c', 'd']]),
    "Empty Input": ("", []),
    "Trailing Newline": ("a,b\n", [['a', 'b']]),
    "Internal Empty Line": ("a,b\n\nc,d", [['a', 'b'], [''], ['c', 'd']]), # Ortadaki boş satır: [""]
    "Quoted Field": ("1,""a,b\n"",2", [['1', 'a,b', '2']]),
    "Escaped Quotes": ("""a\"b""",c", [['a\"b'], ['c']]),
    "Unquoted Spaces": ("  a  ,b", [['  a  ', 'b']]),
    "CRLF Complex Field": ("A,""comma, line\r\nand \"quote\"\r\n"",B", [['A', 'comma, line\r\nand "quote"\r\n'], ['B']])
}

# Hata Testleri (Kural ihlali testleri)
tests_error = [
    ("""unclosed quote,a", "Hatalı girdi: Kapanmayan tırnak"),
    (""""ab"c", "Hatalı girdi: Kapanmayan tırnak") # Kurala göre bu hata vermeli
]

print("=== Test Çalıştırma Başladı ===")
success_count = 0

# Başarı Testleri
for name, (text, expected) in tests.items():
    try:
        result = parse_csv(text)
        assert result == expected, f"[{name}] HATA: Beklenen {expected}, Alınan {result}"
        print(f"[✅ {name}] Başarılı.")
        success_count += 1
    except Exception as e:
        print(f"[❌ {name}] Beklenmeyen HATA: {e}")

# Hata Testleri
for text, expected_msg in tests_error:
    try:
        parse_csv(text)
        print(f"[❌ Hata Test] Beklenmeyen şekilde başarılı oldu: {text}")
    except ValueError as e:
        if str(e) == expected_msg:
            print(f"[✅ Hata Test] Beklenen ValueError yakalandı: {text}")
            success_count += 1
        else:
            print(f"[❌ Hata Test] Yanlış hata mesajı: Beklenen '{expected_msg}', Alınan '{e}'")
    except Exception as e:
        print(f"[❌ Hata Test] Beklenmeyen Hata Tipi: {e}")

print("==================================")
print(f"Toplam Test Sayısı: {len(tests) + len(tests_error)}")
print(f"Başarılı Test Sayısı: {success_count}")
print("==================================")