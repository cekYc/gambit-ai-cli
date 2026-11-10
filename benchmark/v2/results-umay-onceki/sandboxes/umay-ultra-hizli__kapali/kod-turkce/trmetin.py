TURKISH_ALPHABET = '0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz'

char_in_alphabet = set(TURKISH_ALPHABET)

def tr_lower(s):
    result = []
    for c in s:
        if c == 'I':
            result.append('ı')
        elif c == 'İ':
            result.append('i')
        else:
            result.append(c.lower())
    return ''.join(result)


def tr_upper(s):
    result = []
    for c in s:
        if c == 'ı':
            result.append('I')
        elif c == 'i':
            result.append('İ')
        else:
            result.append(c.upper())
    return ''.join(result)

def _char_sort_key(c):
    if c in char_in_alphabet:
        return (1, TURKISH_ALPHABET.index(c))
    else:
        return (0, ord(c))

def _word_sort_key(word):
    lower_word = tr_lower(word)
    return [_char_sort_key(c) for c in lower_word]

def tr_sorted(words):
    return sorted(words, key=_word_sort_key)