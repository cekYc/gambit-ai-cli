def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    CSV metnini parse eder. csv modülü kullanılmaz.
    
    Kurallar:
    - Kayıtlar \n ya da \r\n ile ayrılır
    - Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz
    - Boş metin [] döndürür
    - Ortadaki boş bir satır tek boş alanlı kayıttır: [""]
    - Çift tırnakla başlayan alan ayırıcı, satır sonu ve "" (tek " olarak) içerebilir
    - Tırnaklar alana dahil değildir
    - Tırnaksız alanlar olduğu gibi alınır (boşluklar korunur)
    - Tırnaksız alanın ortasındaki " sıradan karakterdir
    - Hatalı girdide ValueError: kapanan tırnaktan hemen sonra ayırıcı/satır sonu dışında karakter
      ya da hiç kapanmayan tırnak
    """
    if not text:
        return []
    
    # Satır sonlarını normalize et: \r\n -> \n
    normalized = text.replace('\r\n', '\n')
    
    records = []
    i = 0
    n = len(normalized)
    
    while i < n:
        # Bir kayıt (satır) parse et
        fields = []
        
        while i < n:
            # Alan parse et
            if i < n and normalized[i] == '"':
                # Tırnaklı alan
                field_value, i = _parse_quoted_field(normalized, i, delimiter)
                fields.append(field_value)
            else:
                # Tırnaksız alan
                field_start = i
                while i < n:
                    ch = normalized[i]
                    if ch == delimiter:
                        break
                    elif ch == '\n':
                        break
                    else:
                        i += 1
                field_value = normalized[field_start:i]
                fields.append(field_value)
            
            # Alan bitti, ayırıcı veya satır sonu kontrol et
            if i < n and normalized[i] == delimiter:
                i += 1  # delimiter atla, sonraki alan
                continue
            elif i < n and normalized[i] == '\n':
                i += 1  # newline atla, kayıt bitti
                break
            elif i >= n:
                # Dosya sonu
                break
            else:
                # Buraya gelmemeli
                pass
        
        records.append(fields)
        
        # Eğer dosya sonundaysak ve son karakter \n ise, döngü kırılır
        # Ama eğer \n\n varsa, ikinci \n yeni bir boş kayıt başlatır
    
    # Trailing newline temizliği:
    # Eğer normalized \n ile bitiyorsa VE son kayıt tek boş alanlıysa VE
    # bu boş alan trailing newline'dan kaynaklıysa (yani sondan önceki char \n DEĞILSE)
    # VEYA normalized sadece \n ise -> son kayıt sil
    if normalized.endswith('\n'):
        if len(normalized) == 1:
            # Sadece \n
            records = []
        elif records and len(records[-1]) == 1 and records[-1][0] == '':
            # Son kayıt [""] - trailing newline mi yoksa gerçek boş satır mı?
            # Eğer sondan ikinci karakter \n ise -> gerçek boş satır ("\n\n" durumu)
            # Değilse -> trailing newline
            if normalized[-2] != '\n':
                records.pop()
    
    return records


def _parse_quoted_field(text: str, start: int, delimiter: str) -> tuple[str, int]:
    """
    Tırnaklı alanı parse eder.
    Başlangıçtaki " atlanır.
    İçinde "" -> tek " olur.
    Kapanan " sonrası delimiter, \n veya string sonu gelmeli.
    """
    if start >= len(text) or text[start] != '"':
        raise ValueError("Tırnaklı alan \" ile başlamalı")
    
    i = start + 1  # İlk " atla
    result = []
    
    while i < len(text):
        ch = text[i]
        
        if ch == '"':
            # Çift tırnak kontrolü
            if i + 1 < len(text) and text[i + 1] == '"':
                # "" -> kaçış, tek " ekle
                result.append('"')
                i += 2
            else:
                # Kapanan tırnak
                i += 1  # Kapanan " atla
                
                # Kapanan tırnak sonrası: delimiter, \n, veya string sonu olmalı
                if i < len(text):
                    next_ch = text[i]
                    if next_ch != delimiter and next_ch != '\n':
                        raise ValueError(f'Kapanan tırnak sonrası beklenmeyen karakter: {repr(next_ch)}')
                
                return ''.join(result), i
        
        elif ch == '\n':
            # Tırnak içinde satır sonu - izin ver
            result.append(ch)
            i += 1
        
        else:
            result.append(ch)
            i += 1
    
    # Döngü bitti, kapanan tırnak bulunamadı
    raise ValueError("Kapanmayan tırnak")