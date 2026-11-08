import re


def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """CSV metnini çözümle ve satır/alan listesini döndür.

    Kural kısamı:
    - Kayıtlar '\n' veya '\r\n' ile ayrılır. Sonda tek satır sonu yeni kayıt oluşturmaz.
    - Boş metin [] döndürür. Ortadaki boş satır tek boş alanlı kayıttır: [''].
    - Çift tırnaklı alan: ayırıcı, satır sonu ve '' (tek " olarak) içerebilir;
      tırnaklar alana dahil değildir.
    - Tırnaksız alan olduğu gibi alınır (boşluklar korunur); ortadaki " sıradan karakterdir.
    - Hatalı girdide ValueError fırlatır: kapanan tırnaktan hemen sonra ayırıcı/satır sonu
      dışında bir karakter (ör. "ab"c) ya da hiç kapanmayan tırnak.
    """
    if text == "":
        return []

    # Satır sonlarını normalize et: \r\n -> \n, tek başına \r -> \n
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Sondaki tek bir satır sonu yeni kayıt oluşturmaz.
    if text.endswith("\n"):
        text = text[:-1]

    # Tamamen boşsa (sadece satır sonundan ibaretse) boş döndür.
    if text == "":
        return []

    lines = text.split("\n")
    records: list[list[str]] = []
    line_index = 0

    while line_index < len(lines):
        line = lines[line_index]
        record, line_index = _parse_line_multi(line, delimiter, lines, line_index)
        records.append(record)

    return records


def _parse_line_multi(line: str, delimiter: str, lines: list[str], line_index: int) -> tuple[list[str], int]:
    """Tek bir CSV satırını alanlara ayır; tırnak içi alan birden fazla satıra yayabilir."""
    fields: list[str] = []
    i = 0
    n = len(line)

    while i <= n:
        if i == n:
            # Satır sonuna ulaşıldı (tırnak içi alanın içinde olabilir).
            break
        if line[i] == '"':
            field, i, line_index = _parse_quoted_field_multi(line, i, n, delimiter, lines, line_index)
        else:
            field, i = _parse_unquoted_field(line, i, n, delimiter)

        fields.append(field)

        if i < n:
            if line[i] == delimiter:
                i += 1  # ayırıcıyı atla ve bir sonraki alana geç
                continue
            else:
                # Satır sonuna gelinmediyse ama beklenmeyen karakter varsa hata.
                raise ValueError("Geçersiz CSV satırı: beklenmeyen karakter")

    # Tamamen boş satır: tek boş alanlı kayıttır.
    if not fields:
        fields.append("")

    return fields, line_index + 1


def _parse_quoted_field_multi(line: str, i: int, n: int, delimiter: str, lines: list[str], line_index: int) -> tuple[str, int, int]:
    # i, başlangıç tırnağının işaretinde.
    i += 1  # açılış tırnağını atla
    chars: list[str] = []
    current_line_index = line_index

    while True:
        current_line = lines[current_line_index]
        while i < len(current_line):
            c = current_line[i]
            if c == '"':
                # İkinci tırnak: kaçış ('') veya kapanış.
                if i + 1 < len(current_line) and current_line[i + 1] == '"':
                    chars.append('"')
                    i += 2
                else:
                    # Kapanış tırnağı bulundu.
                    i += 1
                    # Kapanan tırnaktan hemen sonra sadece ayırıcı veya satır sonu olabilir.
                    if i < len(current_line) and current_line[i] != delimiter:
                        raise ValueError(f"Kapanan tırnaktan sonra geçersiz karakter: {current_line[i]!r}")
                    return "".join(chars), i, current_line_index
            else:
                chars.append(c)
                i += 1

        # Satır sonuna ulaşıldı ve tırnak henüz kapanmadı.
        # Bu satır sonu alanın parçasıdır (eğer sonraki satır varsa).
        if current_line_index + 1 < len(lines):
            chars.append("\n")
            current_line_index += 1
            i = 0
        else:
            raise ValueError("Kapanmayan tırnak")


def _parse_unquoted_field(line: str, i: int, n: int, delimiter: str) -> tuple[str, int]:
    chars: list[str] = []
    while i < n:
        c = line[i]
        if c == delimiter:
            break
        if c == '"':
            # Tırnaksız alanın ortasındaki " sıradan karakterdir.
            chars.append(c)
            i += 1
        else:
            chars.append(c)
            i += 1
    return "".join(chars), i
