"""Türkçe metin için standart-kütüphaneye dayalı yardımcı fonksiyonlar.

Bu modül şu fonksiyonları sağlar:
- tr_lower(s): Türkçe kurallarla küçük harfe çevirme (I-ı, Ii)
- tr_upper(s): Türkçe kurallarla büyük harfe çevirme (i-I, I-I)
- tr_sorted(words): Türk alfabesine göre büyük/küçük harf farkı gözetmeden sıralama
"""

# Karakter sırası: 0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz
# Listede olmayan karakterler (boşluk, noktalama vb.) listedeki tüm karakterlerden
# önce gelir ve kendi aralarında Unicode kod noktasına göre sıralanır.
_TURKCE_SIRALAMA = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"

# Harf indeksi haritası (küçük harf -> sıralama pozisyonu)
_TURKCE_INDEX = {ch: idx for idx, ch in enumerate(_TURKCE_SIRALAMA)}


# --- Türkçe büyük/küçük harf eşleştirmeleri -------------------------------

# ASCII + Türkçe specials için büyük harfe çevirme tablosu (codepoint -> codepoint)
# chr() kullanılır ki dosya encoding sorunları yaşanmasın.
_UPPER_TABLE = {
    97: 65,   # a -> A
    98: 66,   # b -> B
    99: 67,   # c -> C
    231: 199, # ç -> Ç
    100: 68,  # d -> D
    101: 69,  # e -> E
    102: 70,  # f -> F
    103: 71,  # g -> G
    287: 286, # ğ -> Ğ
    104: 72,  # h -> H
    305: 73,  # ı -> I
    105: 304, # i -> İ
    106: 74,  # j -> J
    107: 75,  # k -> K
    108: 76,  # l -> L
    109: 77,  # m -> M
    110: 78,  # n -> N
    111: 79,  # o -> O
    246: 214, # ö -> Ö
    112: 80,  # p -> P
    113: 81,  # q -> Q
    114: 82,  # r -> R
    115: 83,  # s -> S
    351: 350, # ş -> Ş
    116: 84,  # t -> T
    117: 85,  # u -> U
    252: 220, # ü -> Ü
    118: 86,  # v -> V
    119: 87,  # w -> W
    120: 88,  # x -> X
    121: 89,  # y -> Y
    122: 90,  # z -> Z
}

# ASCII + Türkçe specials için küçük harfe çevirme tablosu (codepoint -> codepoint)
_LOWER_TABLE = {
    65: 97,   # A -> a
    66: 98,   # B -> b
    67: 99,   # C -> c
    199: 231, # Ç -> ç
    68: 100,  # D -> d
    69: 101,  # E -> e
    70: 102,  # F -> f
    71: 103,  # G -> g
    286: 287, # Ğ -> ğ
    72: 104,  # H -> h
    73: 305,  # I -> ı
    304: 105, # İ -> i
    74: 106,  # J -> j
    75: 107,  # K -> k
    76: 108,  # L -> l
    77: 109,  # M -> m
    78: 110,  # N -> n
    79: 111,  # O -> o
    214: 246, # Ö -> ö
    80: 112,  # P -> p
    81: 113,  # Q -> q
    82: 114,  # R -> r
    83: 115,  # S -> s
    350: 351, # Ş -> ş
    84: 116,  # T -> t
    85: 117,  # U -> u
    220: 252, # Ü -> ü
    86: 118,  # V -> v
    87: 119,  # W -> w
    88: 120,  # X -> x
    89: 121,  # Y -> y
    90: 122,  # Z -> z
}


def tr_lower(s: str) -> str:
    """Türkçe kurallarla string'i küçük harfe çevirir.

    Özel durumlar:
      I -> ı
      İ -> i
    Diğer harfler standart Unicode kurallarıyla (ASCII A-Z -> a-z) çevrilir.
    """
    return s.translate(_LOWER_TABLE)


def tr_upper(s: str) -> str:
    """Türkçe kurallarla string'i büyük harfe çevirir.

    Özel durumlar:
      i -> İ
      ı -> I
    Diğer harfler standart Unicode kurallarıyla (ASCII a-z -> A-Z) çevrilir.
    """
    return s.translate(_UPPER_TABLE)


def _siralama_anahtari(kelime: str):
    """Bir kelime için sıralama anahtarı döndürür.

    Kurallar:
      - Listede olmayan karakterler önce gelir (grup 0), kendi aralarında
        Unicode kod noktasına göre sıralanır.
      - Listedeki karakterler sonra gelir (grup 1), alfabetik indeksine göre.
      - Büyük/küçük harf farkı gözetilmez (küçük harfe çevrilerek karşılaştırılır).
      - Önek durumu: Python tuple karşılaştırması zaten kısa olanı önce getirir.
      - Eşit anahtarlar stable sort sayesinde girdideki sıraları korur.
    """
    kucuk = tr_lower(kelime)
    anahtar = []
    for ch in kucuk:
        idx = _TURKCE_INDEX.get(ch)
        if idx is None:
            # Listede olmayan karakter: önce gelir, kendi içinde kod noktasına göre
            anahtar.append((0, ord(ch)))
        else:
            # Listedeki karakter: alfabetik sıraya göre
            anahtar.append((1, idx))
    return tuple(anahtar)


def tr_sorted(words) -> list[str]:
    """Kelimeleri Türk alfabesine göre, büyük/küçük harf farkı gözetmeden sıralar.

    Orijinal listenin kopyasını döndürür; girdi listesi değiştirilmez.
    """
    return sorted(words, key=_siralama_anahtari)
