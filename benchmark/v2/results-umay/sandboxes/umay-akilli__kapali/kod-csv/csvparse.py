def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    CSV metnini parse eder. `csv` modülü kullanılmaz.
    
    Kurallar:
    - Kayıtlar \n ya da \r\n ile ayrılır. Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz.
    - Boş metin [] döndürür.
    - Ortadaki boş bir satır tek boş alanlı kayıttır: [""]
    - Çift tırnakla başlayan bir alan ayırıcı, satır sonu ve "" (tek \" olarak) içerebilir; tırnaklar alana dahil değildir.
    - Tırnaksız alanlar olduğu gibi alınır (boşluklar korunur); tırnaksız alanın ortasındaki \" sıradan karakterdir.
    - Hatalı girdide ValueError fırlat: kapanan tırnaktan hemen sonra ayırıcı/satır sonu dışında bir karakter
      (ör. \"ab\"c) ya da hiç kapanmayan tırnak.
    """
    if not text:
        return []
    
    records = []
    fields = []
    field_chars = []
    
    i = 0
    n = len(text)
    in_quoted = False
    
    while i < n:
        ch = text[i]
        
        if in_quoted:
            if ch == '"':
                # Kapanış tırnağı mı escaped tırnak mı?
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped tırnak: "" -> "
                    field_chars.append('"')
                    i += 2
                else:
                    # Kapanış tırnağı
                    in_quoted = False
                    i += 1
                    # Kapanış tırnağından hemen sonra: ayırıcı, satır sonu, veya metin sonu beklenir
                    if i < n:
                        next_ch = text[i]
                        if next_ch != delimiter and next_ch != '\n' and next_ch != '\r':
                            raise ValueError(f"Kapanan tırnaktan sonra ayırıcı veya satır sonu bekleniyordu, '{next_ch}' bulundu")
            else:
                field_chars.append(ch)
                i += 1
        else:
            # Tırnak dışında
            if ch == '"':
                # Tırnaklı alan başlangıcı - alan başında olmalı
                if field_chars:
                    # Tırnak alan ortasında -> tırnaksız alanda tırnak sıradan karakter
                    field_chars.append(ch)
                    i += 1
                else:
                    in_quoted = True
                    i += 1
            elif ch == delimiter:
                # Alan ayırıcı
                fields.append(''.join(field_chars))
                field_chars = []
                i += 1
            elif ch == '\n':
                # Satır sonu (LF)
                fields.append(''.join(field_chars))
                field_chars = []
                records.append(fields)
                fields = []
                i += 1
            elif ch == '\r':
                # CR - CRLF olabilir
                if i + 1 < n and text[i + 1] == '\n':
                    # CRLF
                    fields.append(''.join(field_chars))
                    field_chars = []
                    records.append(fields)
                    fields = []
                    i += 2
                else:
                    # Yalnız CR - satır sonu say
                    fields.append(''.join(field_chars))
                    field_chars = []
                    records.append(fields)
                    fields = []
                    i += 1
            else:
                field_chars.append(ch)
                i += 1
    
    # Metin bitti
    # Eğer in_quoted hala True ise -> kapanmayan tırnak hatası
    if in_quoted:
        raise ValueError("Kapanmayan tırnak")
    
    # Son alanı ekle
    fields.append(''.join(field_chars))
    
    # Trailing newline kontrolü: eğer text \n veya \r\n ile bitiyorsa VE fields sadece [''] ise
    # ve records boş değilse -> bu trailing newline'dan kaynaklı boş kayıttır, ekleme
    ends_with_newline = text.endswith('\n') or text.endswith('\r\n')
    is_empty_record = (len(fields) == 1 and fields[0] == '')
    
    if not (ends_with_newline and is_empty_record and records):
        records.append(fields)
    elif not records and is_empty_record:
        # Sadece trailing newline varsa ve hiç kayıt yoksa -> boş metin gibi davran
        pass
    
    return records
