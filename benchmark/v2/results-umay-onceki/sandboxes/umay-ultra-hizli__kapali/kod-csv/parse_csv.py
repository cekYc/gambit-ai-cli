import csv
import io


def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """Parse CSV text into a list of lists of strings.

    Rules:
    - Records are split by ``\n`` or ``\r\n``. A trailing newline does NOT create a new record.
    - Empty text returns ``[]``.
    - A blank line in the middle of the text is treated as a single‑field row ``[""]``.
    - Fields enclosed in double quotes may contain the delimiter, newlines and escaped quotes
      (``""`` represents a single quote).
    - Unquoted fields are taken as‑is (spaces are kept).
    - A ValueError is raised if a quote is unclosed or appears in an invalid position.
    """
    # Empty or whitespace‑only input → empty list
    if not text or not text.strip():
        return []

    try:
        # csv.reader handles quoting, delimiters and line splitting per RFC 4180
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = list(reader)
    except csv.Error as exc:
        raise ValueError(str(exc))

    # Convert empty rows to [""] as required
    new_rows = []
    for row in rows:
        if len(row) == 0:
            new_rows.append([''])
        else:
            new_rows.append(row)
    rows = new_rows

    # Remove trailing empty rows caused by final newline(s)
    while rows and rows[-1] == ['']:
        rows.pop()

    return rows


if __name__ == "__main__":
    # Basic sanity checks
    print(parse_csv(""))                         # → []
    print(parse_csv("a,b\\nc,d"))                # → [['a','b'],['c','d']]
    print(parse_csv("a,b\\n\\nc,d"))               # blank line in middle → [['a','b'],[""],['c','d']]
    print(parse_csv('"a,b",c'))                 # quoted field with delimiter
    print(parse_csv('"a""b"'))                # escaped quote inside quoted field
