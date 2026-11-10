"""Minimal CSV parser without using the csv module."""


def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    if text == "":
        return []

    records: list[list[str]] = []
    fields: list[str] = []
    cur: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        c = text[i]

        # Quoted field
        if c == '"':
            j = i + 1
            while j < n:
                if text[j] == '"':
                    if j + 1 < n and text[j + 1] == '"':
                        cur.append('"')
                        j += 2
                    else:
                        # End of quoted field
                        k = j + 1
                        # Bir kapanış tırnaktan sonra sadece ayırıcı veya satır sonu gelebilir.
                        # Başka bir karakter (ör. "ab"c) hatadır.
                        if k < n and text[k] not in delimiter + "\r\n":
                            raise ValueError(
                                f"Invalid trailing character after closing quote: {text[k]!r}"
                            )
                        # Delimiter veya satır sonu ise kaydı/alanı bitir ve işleme devam et.
                        if k < n and text[k] in delimiter:
                            fields.append("".join(cur))
                            cur = []
                            i = k + 1
                        elif k < n and text[k] in "\r\n":
                            fields.append("".join(cur))
                            cur = []
                            i = k
                            # Satır sonu işlemi aşağıdaki elif dallarıyla ele alınacak.
                        else:
                            i = j + 1
                        break
                else:
                    cur.append(text[j])
                    j += 1
            else:
                raise ValueError("Unclosed quoted field")

        elif c in delimiter:
            fields.append("".join(cur))
            cur = []
            i += 1

        elif c == "\r":
            fields.append("".join(cur))
            cur = []
            i += 1
            if i < n and text[i] == "\n":
                i += 1
            records.append(fields)
            fields = []

        elif c == "\n":
            fields.append("".join(cur))
            cur = []
            i += 1
            records.append(fields)
            fields = []

        else:
            cur.append(c)
            i += 1

    # End of text: flush last field / record if anything pending
    if cur or fields:
        fields.append("".join(cur))
        records.append(fields)

    # Drop trailing empty record caused by final line ending only
    if records and records[-1] == [""]:
        records.pop()

    return records


if __name__ == "__main__":
    import sys

    sample = 'a,b,c\n"d,e",f,g\nh,i,j'
    print(parse_csv(sample))
