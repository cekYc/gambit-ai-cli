def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    CSV metnini standart kütüphaneler kullanmadan ayrıştırır.
    """
    if not text.strip():
        return []

    records = []
    # splitlines() \n ve \r\n'yi ele alır ve metin sonundaki boş satırı kayıt oluşturmadan atar.
    lines = text.splitlines()

    for line in lines:
        if not line:
            # Ortadaki boş satır kuralı: tek boş alanlı kayıt [""] olmalı.
            records.append([''])
            continue

        fields = []
        current_field = ""
        in_quotes = False
        i = 0
        line_length = len(line)
        
        while i < line_length:
            char = line[i]

            if in_quotes:
                if char == '"' and i + 1 < line_length and line[i+1] == '"':
                    # Kaçış tırnağı: "" -> "
                    current_field += '"'
                    i += 2
                    continue
                elif char == '"':
                    # Tırnak kapatıldı
                    in_quotes = False
                    
                    # Kapatan tırnak sonrası kontrol: Sadece ayırıcı veya satır sonu (EOL) olmalı.
                    if i + 1 < line_length and line[i+1] != delimiter:
                        raise ValueError("Hatalı girdi: Kapanan tırnak sonrası geçersiz karakter")
                        
                    i += 1
                    continue
                else:
                    # Tırnak içindeki normal karakter
                    current_field += char
                    i += 1
                    continue
            else:
                # Tırnaklar dışında
                if char == '"':
                    # Tırnak başladı
                    in_quotes = True
                    i += 1
                    continue
                elif char == delimiter:
                    # Alan ayırıcı bulundu, alanı kaydet
                    fields.append(current_field)
                    current_field = ""
                    i += 1
                    continue
                else:
                    # Normal karakter (boşluklar dahil)
                    current_field += char
                    i += 1
        
        # Satır sonuna gelindiğinde kontrol
        if in_quotes:
            # Hata: Kapanmayan tırnak
            raise ValueError("Hatalı girdi: Kapanmayan tırnak")
        else:
            # Son alanı kaydet
            fields.append(current_field)
            records.append(fields)

    return records
