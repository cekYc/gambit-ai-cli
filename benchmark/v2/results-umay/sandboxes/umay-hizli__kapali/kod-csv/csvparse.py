"""CSV ayrıştırıcı.

Standart kütüphane `csv` modülünü kullanmadan, satır sonu (\n veya \r\n)
ve birim ayırıcı (delimiter, varsayılan virgül) bazlı CSV metnini ayrıştırır.
"""

from typing import List


def parse_csv(text: str, delimiter: str = ",") -> List[List[str]]:
    """CSV metnini satır ve alanlara ayırır.

    Args:
        text: Ayrıştırılacak CSV metni.
        delimiter: Alan ayırıcı karakteri (varsayılan ",").

    Returns:
        Her kayıt bir liste olan kayıt listesidir.

    Raises:
        ValueError: Çift tırnakla başlayan alan hatalıysa (kapalı olmayan
            tırnak veya kapanıştan hemen sonra ayırıcı/satır sonu dışında bir
            karakter varsa).
    """

    if text == "":
        return []

    records: List[List[str]] = []
    record: List[str] = []
    n = len(text)
    i = 0

    def read_unquoted_field() -> str:
        nonlocal i
        start = i
        while i < n and text[i] not in (delimiter, "\r", "\n"):
            i += 1
        return text[start:i]

    def read_quoted_field() -> str:
        nonlocal i
        # text[i] == '"'
        i += 1  # açılış tırnaktan geç
        chars: List[str] = []
        while i < n:
            ch = text[i]
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    chars.append('"')
                    i += 2
                else:
                    i += 1  # kapanış tırnak
                    if i < n and text[i] in (delimiter, "\r", "\n"):
                        return "".join(chars)
                    raise ValueError(
                        "Çift tırnakla başlayan alanda kapanıştan sonra "
                        "geçersiz karakter."
                    )
            else:
                chars.append(ch)
                i += 1
        raise ValueError("Çift tırnakla başlayan alan kapanmadı.")

    def finish_record() -> None:
        nonlocal record
        if record:
            records.append(record)
            record = []

    while i < n:
        ch = text[i]

        if ch == '"':
            record.append(read_quoted_field())
            if i >= n:
                break
            if text[i] == delimiter:
                i += 1
                continue
            if text[i] in ("\r", "\n"):
                finish_record()
                continue
            raise ValueError(
                "Çift tırnakla başlayan alanda kapanıştan sonra "
                "geçersiz karakter."
            )

        if ch == delimiter:
            record.append("")
            i += 1
            continue

        if ch == "\r":
            if i + 1 < n and text[i + 1] == "\n":
                i += 2
            else:
                i += 1
            finish_record()
            continue

        if ch == "\n":
            i += 1
            finish_record()
            continue

        # Tırnaksız alan.
        record.append(read_unquoted_field())
        if i >= n:
            break
        if text[i] == delimiter:
            i += 1
            continue
        if text[i] in ("\r", "\n"):
            # Satır sonu bir sonraki döngüde işlenir.
            continue

    # Metin sonu geldiğinde açık olan son alanı kaydet ve kayıtı bitir.
    record.append("")
    finish_record()

    return records
