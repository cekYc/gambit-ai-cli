def parse_csv(text: str, delimiter: str = ",") -> list[list[str]]:
    """
    Parse CSV text without using the csv module.
    
    Args:
        text: CSV formatted text
        delimiter: Field delimiter (default ",")
    
    Returns:
        List of records, each record is a list of fields
    
    Raises:
        ValueError: For malformed CSV input
    """
    if not text:
        return []
    
    # Normalize line endings to \n only
    text = text.replace('\r\n', '\n')
    
    records = []
    fields = []
    field_chars = []
    in_quotes = False
    i = 0
    n = len(text)
    
    while i < n:
        ch = text[i]
        
        if in_quotes:
            if ch == '"':
                if i + 1 < n and text[i + 1] == '"':
                    # Escaped quote
                    field_chars.append('"')
                    i += 2
                else:
                    # Closing quote
                    in_quotes = False
                    i += 1
                    # After closing quote, next char must be delimiter, newline, or end
                    if i < n:
                        next_ch = text[i]
                        if next_ch != delimiter and next_ch != '\n':
                            raise ValueError(f"Invalid character after closing quote at position {i}")
            elif ch == '\n':
                # Newline inside quoted field
                field_chars.append('\n')
                i += 1
            else:
                field_chars.append(ch)
                i += 1
        else:
            # Not in quotes
            if ch == '"':
                # Start of quoted field - only valid at field start
                if field_chars:
                    # Quote in middle of unquoted field - treat as literal
                    field_chars.append(ch)
                    i += 1
                else:
                    in_quotes = True
                    i += 1
            elif ch == delimiter:
                # Field separator
                fields.append(''.join(field_chars))
                field_chars = []
                i += 1
            elif ch == '\n':
                # End of record
                fields.append(''.join(field_chars))
                field_chars = []
                records.append(fields)
                fields = []
                i += 1
            else:
                field_chars.append(ch)
                i += 1
    
    # End of text
    if in_quotes:
        raise ValueError("Unclosed quoted field")
    
    # Add the last field and record if there's content
    # But don't add empty record if text ended with newline
    if field_chars or fields or (n > 0 and text[-1] != '\n'):
        fields.append(''.join(field_chars))
        if fields:
            records.append(fields)
    
    return records
