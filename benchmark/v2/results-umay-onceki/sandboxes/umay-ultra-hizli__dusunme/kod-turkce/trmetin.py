ALPHABET = '0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz'
ALPHABET_SET = set(ALPHABET)


def tr_lower(s):
    """Convert Turkish text to lowercase with Turkish I/ı and İ/i rules."""
    result = []
    for char in s:
        if char == 'I':
            result.append('ı')
        elif char == 'İ':
            result.append('i')
        else:
            result.append(char.lower())
    return ''.join(result)


def tr_upper(s):
    """Convert Turkish text to uppercase with Turkish I/ı and İ/i rules."""
    result = []
    for char in s:
        if char == 'ı':
            result.append('I')
        elif char == 'i':
            result.append('İ')
        else:
            result.append(char.upper())
    return ''.join(result)


def _char_sort_key(char):
    """Get sort key for a single character based on Turkish alphabet order."""
    if char in ALPHABET_SET:
        return (1, ALPHABET.index(char))
    else:
        return (0, ord(char))


def _word_sort_key(word):
    """Get sort key for a word based on Turkish alphabet order."""
    return tuple(_char_sort_key(c) for c in word)


def tr_sorted(words):
    """Sort words based on Turkish alphabet order, case-insensitive with Turkish rules.
    
    Args:
        words: list of strings to sort
        
    Returns:
        New list with words sorted according to Turkish alphabet rules.
        Original list is not modified.
    """
    result = sorted(words, key=lambda w: _word_sort_key(tr_lower(w)))
    return result
