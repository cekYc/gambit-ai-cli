def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    if not text:
        return []
    text = text.replace("\r\n", "\n")
    records = []
    current_record = []
    current_field = []
    in_quotes = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_quotes:
            if ch == "\"":
                if i + 1 < n and text[i + 1] == "\"":
                    current_field.append("\"")
                    i += 2
                    continue
                else:
                    in_quotes = False
                    i += 1
                    if i < n:
                        next_ch = text[i]
                        if next_ch != delimiter and next_ch != "\n":
                            raise ValueError(f"Invalid character after closing quote at position {i}: {next_ch}")
                    continue
            else:
                current_field.append(ch)
                i += 1
                continue
        else:
            if ch == "\"":
                if current_field:
                    raise ValueError(f"Quote not at start of field at position {i}")
                in_quotes = True
                i += 1
                continue
            elif ch == delimiter:
                current_record.append("".join(current_field))
                current_field = []
                i += 1
                continue
            elif ch == "\n":
                current_record.append("".join(current_field))
                records.append(current_record)
                current_record = []
                current_field = []
                i += 1
                continue
            else:
                current_field.append(ch)
                i += 1
                continue
    if current_field or current_record or (records and text.endswith("\n")):
        if not text.endswith("\n"):
            current_record.append("".join(current_field))
            records.append(current_record)
    if in_quotes:
        raise ValueError("Unclosed quote at end of input")
    return records

if __name__ == "__main__":
    test_cases = [
        ("", []),
        ("a,b,c", [["a", "b", "c"]]),
        ("a,b\nc,d", [["a", "b"], ["c", "d"]]),
        ("\"hello\",world", [["hello", "world"]]),
        ("\"hello\"\"world\",foo", [["hello\"world", "foo"]]),
        ("a,\"b\nc\",d", [["a", "b\nc", "d"]]),
        ("a,b\n", [["a", "b"]]),
        ("a,b\n\nc,d", [["a", "b"], [""], ["c", "d"]]),
        ("\n", [[""]]),
        ("a,\"b\"c", None),
        ("\"unclosed", None),
    ]
    for i, (inp, expected) in enumerate(test_cases):
        try:
            result = parse_csv(inp)
            if expected is None:
                print(f"Test {i}: FAIL - expected ValueError but got {result}")
            elif result == expected:
                print(f"Test {i}: PASS")
            else:
                print(f"Test {i}: FAIL - got {result}, expected {expected}")
        except ValueError as e:
            if expected is None:
                print(f"Test {i}: PASS - ValueError raised: {e}")
            else:
                print(f"Test {i}: FAIL - unexpected ValueError: {e}")
