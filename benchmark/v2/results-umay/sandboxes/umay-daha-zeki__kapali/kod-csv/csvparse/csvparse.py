def parse_csv(text: str, delimiter: str = "") -> list[list[str]]:
    lines = text.splitlines()
    
    if not text.strip():
        return []

    records = []
    current_record = []
    current_field = ""
    in_quotes = False
    
    for i, line in enumerate(lines):
        # Kural: Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz.
        if i == len(lines) - 1 and not line.strip() and len(lines) > 1:
            # Eğer son satır boşsa ve bu, metnin sonunu işaret ediyorsa (tek satır sonu)
            # ancak metnin kendisi tamamen boş değilse, kayıt eklemeyi atla.
            if current_record and current_record[-1] != current_field: # Önceki satırda kayıt varsa ve bu satır yeni bir alan başlatmadıysa
                pass # Hiçbir şey yapma, kaydı sonlandırma adımını atla
            else:
                # Eğer son satır boşsa ve bu, önceki satırın kaydını henüz tamamlamadıysa (yani son satır boşsa)
                # bu kaydı oluşturmayacağız.
                pass 
            # Normalde, son boş satırda kayıt tamamlanmaz.
            # Bu durumda, bu döngü adımını atlayarak son kaydın tamamlanmasını önleriz.
            continue

        i_char = 0
        while i_char < len(line):
            char = line[i_char]
            
            if in_quotes and char == '"':
                # Kaçış tırnağı: ""
                if i_char + 1 < len(line) and line[i_char+1] == '"':
                    current_field += '"'
                    i_char += 2
                    continue
                else:
                    # Tırnak kapandı
                    in_quotes = False
                    current_field += char
                    i_char += 1
                    continue
            elif not in_quotes and char == delimiter:
                # Alan ayırıcı
                current_record.append(current_field)
                current_field = ""
                i_char += 1
                continue
            elif char == '"' and not in_quotes:
                # Tırnak başladı
                in_quotes = True
                current_field += char
                i_char += 1
                continue
            else:
                # Normal karakter
                current_field += char
                i_char += 1

        # Satır sonu geldi: Kaydı tamamla
        current_record.append(current_field)
        records.append(current_record)
        
        # Kural: Hatalı girdi kontrolü (Kapanmamış tırnak)
        if in_quotes:
            raise ValueError("Hatalı girdi: Kapanan tırnak bulunamadı.")

    return records