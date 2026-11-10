from __future__ import annotations


def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    CSV metnini parse eder (csv modülü kullanılmadan).

    Kurallar:
    - Kayıtlar \n ya da \r\n ile ayrılır.
    - Metnin sonundaki tek satır sonu yeni bir kayıt oluşturmaz;
      boş metin [] döndürür.
    - Ortadaki boş bir satır tek boş alanlı kayıttır: [""]
    - Çift tırnakla başlayan bir alan ayırıcı, satır sonu ve "" (tek ")
      olarak) içerebilir; tırnaklar alana dahil değildir.
    - Tırnaksız alanlar olduğu gibi alınır (boşluklar korunur);
      tırnaksız alanın ortasındaki " sıradan karakterdir.
    - Hatalı girdide ValueError fırlat: kapanan tırnaktan hemen sonra
      ayırıcı/satır sonu dışında bir karakter (ör. "ab"c)
      ya da hiç kapanmayan tırnak.
    """
    if not text:
        return []

    # Satır sonlarını normalize et: \r\n -> \n
    lines = text.splitlines()
    # splitlines() son satır sonunu korumaz, bu istediğimiz davranış.
    # Ancak boş satırları da korur.

    records: list[list[str]] = []
    current_record: list[str] = []
    current_field: list[str] = []
    in_quotes = False
    i = 0
    n = len(text)

    # Satır bazlı değil, karakter bazlı parse etmek daha güvenli
    # çünkü tırnak içi satır sonları olabilir.
    # Bu yüzden text üzerinde tek geçiş yapalım.

    field_start = 0
    field_chars: list[str] = []
    pending_field = False  # Track if we have a field waiting to be added

    while i < n:
        ch = text[i]

        if in_quotes:
            if ch == '"':
                # Peek next char
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped quote
                    field_chars.append('"')
                    i += 2
                    continue
                else:
                    # Closing quote
                    in_quotes = False
                    i += 1
                    # After closing quote, must be delimiter, newline, or end of input
                    if i < n:
                        next_ch = text[i]
                        if next_ch != delimiter and next_ch != '\n' and next_ch != '\r':
                            raise ValueError(
                                f"Expected delimiter or newline after closing quote at position {i}"
                            )
                    # Keep pending_field = True to indicate we have a field (even if empty)
                    pending_field = True
                    continue
            else:
                # Any other character inside quotes (including delimiter, newline)
                field_chars.append(ch)
                i += 1
                continue
        else:
            # Not in quotes
            if ch == '"':
                # If field_chars is empty, this starts a quoted field
                # If field_chars is not empty, this is a quote in the middle of unquoted field (allowed)
                if not field_chars:
                    in_quotes = True
                else:
                    field_chars.append(ch)
                i += 1
                continue
            elif ch == delimiter:
                # End of field
                current_record.append(''.join(field_chars))
                field_chars = []
                pending_field = True
                i += 1
                continue
            elif ch == '\n':
                # End of record
                current_record.append(''.join(field_chars))
                records.append(current_record)
                current_record = []
                field_chars = []
                pending_field = False
                i += 1
                continue
            elif ch == '\r':
                # Handle \r\n
                if i + 1 < n and text[i + 1] == '\n':
                    # \r\n sequence
                    current_record.append(''.join(field_chars))
                    records.append(current_record)
                    current_record = []
                    field_chars = []
                    pending_field = False
                    i += 2
                    continue
                else:
                    # Lone \r - treat as regular char? Spec says records separated by \n or \r\n
                    # We'll treat lone \r as regular character for safety
                    field_chars.append(ch)
                    i += 1
                    continue
            else:
                field_chars.append(ch)
                i += 1
                continue

    # End of input
    if in_quotes:
        raise ValueError("Unclosed quoted field")

    # Add the last field/record if there's content or if we have a pending field
    if field_chars or current_record or pending_field:
        current_record.append(''.join(field_chars))
        records.append(current_record)
    # If text ends with newline, the last record was already added in the loop
    # No extra handling needed

    return records
