TURKCE_ALFABE = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"
_TURKCE_SIRALAMA = {ch: i for i, ch in enumerate(TURKCE_ALFABE)}
_ALFABE_DISI_BASLANGIC = len(TURKCE_ALFABE)


def _turkce_kucult_karakter(ch):
    if ch == "I":
        return "ı"
    if ch == "İ":
        return "i"
    return ch.lower()


def _turkce_buyult_karakter(ch):
    if ch == "i":
        return "İ"
    if ch == "ı":
        return "I"
    return ch.upper()


def tr_lower(s):
    return "".join(_turkce_kucult_karakter(ch) for ch in s)


def tr_upper(s):
    return "".join(_turkce_buyult_karakter(ch) for ch in s)


def _sirala_anahtari(kelime):
    anahtar = []
    for ch in kelime:
        if ch in _TURKCE_SIRALAMA:
            anahtar.append((1, _TURKCE_SIRALAMA[ch]))
        else:
            anahtar.append((0, 0, ord(ch)))
    return anahtar


def tr_sorted(words):
    return sorted(words, key=lambda kelime: _sirala_anahtari(tr_lower(kelime)))
