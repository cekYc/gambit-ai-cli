def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    CSV metnini parse eder. Standart csv modülü kullanmadan.
    
    Kurallar:
    - Kayıtlar \n ya da \r\n ile ayrılır. Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz.
    - Boş metin [] döndürür. Ortadaki boş bir satır tek boş alanlı kayıttır: [""]
    - Çift tırnakla başlayan bir alan ayırıcı, satır sonu ve "" (tek \" olarak) içerebilir; tırnaklar alana dahil değildir.
    - Tırnaksız alanlar olduğu gibi alınır (boşluklar korunur); tırnaksız alanın ortasındaki \" sıradan karakterdir.
    - Hatalı girdide ValueError fırlat: kapanan tırnaktan hemen sonra ayırıcı/satır sonu dışında bir karakter
      (ör. `\"ab\"c`) ya da hiç kapanmayan tırnak.
    """
    if not text:
        return []
    
    # Satırları ayır - \r\n ve \n ikisini de destekle
    lines = text.splitlines()
    
    records = []
    i = 0
    while i < len(lines):
        line = lines[i]
        fields = []
        field_start = 0
        pos = 0
        
        while pos < len(line):
            if line[pos] == '"':
                # Tırnaklı alan - sadece alan başlangıcında geçerli
                if pos != field_start:
                    # Tırnak alan başında değilse sıradan karakter olarak işle
                    pos += 1
                    continue
                
                pos += 1  # Başlangıç tırnağını atla
                field_chars = []
                
                while pos < len(line):
                    if line[pos] == '"':
                        if pos + 1 < len(line) and line[pos + 1] == '"':
                            # Kaçış tırnağı: "" -> "
                            field_chars.append('"')
                            pos += 2
                        else:
                            # Kapanış tırnağı
                            pos += 1
                            break
                    else:
                        field_chars.append(line[pos])
                        pos += 1
                else:
                    # Satır bitti ama tırnak kapanmadı - çok satırlı alan olabilir
                    # Sonraki satırları da oku
                    field_chars.append('\n')
                    i += 1
                    while i < len(lines):
                        line = lines[i]
                        pos = 0
                        while pos < len(line):
                            if line[pos] == '"':
                                if pos + 1 < len(line) and line[pos + 1] == '"':
                                    field_chars.append('"')
                                    pos += 2
                                else:
                                    # Kapanış tırnağı bulundu
                                    pos += 1
                                    break
                            else:
                                field_chars.append(line[pos])
                                pos += 1
                        else:
                            # Bu satırda da kapanış yok, satır sonu ekle ve devam et
                            field_chars.append('\n')
                            i += 1
                            continue
                        break
                    else:
                        # Tüm satırlar bitti ama tırnak kapanmadı
                        raise ValueError("Unterminated quoted field")
                
                # Kapanış tırnağından sonra ayırıcı veya satır sonu gelmeli
                if pos < len(line):
                    if line[pos] == delimiter:
                        pos += 1
                        field_start = pos
                    elif line[pos] != '"':  # "" durumu yukarıda handle edildi
                        raise ValueError(f"Invalid character after closing quote at position {pos} in line {i}")
                
                fields.append(''.join(field_chars))
            elif line[pos] == delimiter:
                # Tırnaksız alan
                fields.append(line[field_start:pos])
                pos += 1
                field_start = pos
            else:
                pos += 1
        
        # Satır sonundaki son alan
        if field_start <= len(line):
            fields.append(line[field_start:])
        
        records.append(fields)
        i += 1
    
    return records