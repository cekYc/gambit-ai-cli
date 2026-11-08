"""Türkçe metin yardımcı fonksiyonları.

Bu modül, Python'ın standart kütüphanesini kullanarak Türkçe dil kurallarına
uygun büyük/küçük harf dönüşümü ve sıralama işlemleri sağlar.
"""

# Türk alfabesine göre karakter sırası (küçük harf).
# Listede olmayan karakterler (boşluk, noktalama vb.) bu listedeki tüm
# karakterlerden önce gelir ve kendi aralarında Unicode kod noktasına göre
# sıralanır.
_TURKCE_ALFABE = "0123456789abcçdefgğhıijklmnoöpqrsştuüvwxyz"

# Karakter -> sıralama indeksi haritası (O(1) erişim için).
_TURKCE_SIRALAMA = {karakter: indis for indis, karakter in enumerate(_TURKCE_ALFABE)}


def tr_lower(s: str) -> str:
    """Verilen metni Türkçe kurallara göre küçük harfe çevirir.

    Özellikle 'I' -> 'ı' ve 'İ' -> 'i' dönüşümleri doğru şekilde yapılır.
    Diğer harfler Unicode küçük harf kurallarıyla dönüştürülür.
    """
    sonuc = []
    for karakter in s:
        if karakter == "I":
            sonuc.append("ı")
        elif karakter == "İ":
            sonuc.append("i")
        else:
            sonuc.append(karakter.lower())
    return "".join(sonuc)


def tr_upper(s: str) -> str:
    """Verilen metni Türkçe kurallara göre büyük harfe çevirir.

    Özellikle 'i' -> 'İ' ve 'ı' -> 'I' dönüşümleri doğru şekilde yapılır.
    Diğer harfler Unicode büyük harf kurallarıyla dönüştürülür.
    """
    sonuc = []
    for karakter in s:
        if karakter == "i":
            sonuc.append("İ")
        elif karakter == "ı":
            sonuc.append("I")
        else:
            sonuc.append(karakter.upper())
    return "".join(sonuc)


def _sirala_anahtari(kelime: str):
    """Sıralama için anahtar üretir.

    - Kelime Türkçe kurallarla küçültülür (büyük/küçük harf farkı göz ardı edilir).
    - Alfabe dışındaki karakterler listedeki tüm karakterlerden önce gelir.
    - Alfabe dışındaki karakterler kendi aralarında Unicode kod noktasına göre
      sıralanır.
    - Alfabe içindeki karakterler Türk alfabesi sırasına göre sıralanır.
    - Kısa önek kelimesi uzuninden önce gelir (tuple uzunluğu nedeniyle).
    """
    kucuk = tr_lower(kelime)
    anahtar = []
    for karakter in kucuk:
        indis = _TURKCE_SIRALAMA.get(karakter)
        if indis is None:
            # Alfabe dışındaki karakterler: (0, 1, kod noktası)
            # Alfabe içindeki karakterler: (1, 0, alfabe indeksi)
            anahtar.append((0, 1, ord(karakter)))
        else:
            anahtar.append((1, 0, indis))
    # Tuple karşılaştırmasında önce uzunluk (önceki kelime kısaysa önce gelir),
    # sonra karakter karakter karşılaştırma yapılır.
    return (len(anahtar), anahtar)


def tr_sorted(words: list[str]) -> list[str]:
    """Kelimeleri Türk alfabesine göre büyük/küçük harf farkı gözetmeden sıralar.

    Girdi listesi değiştirilmez; sıralanmış yeni bir liste döndürür.
    Eşit sayılan kelimeler girdideki sıralarını korur (stabil sıralama).
    """
    return sorted(words, key=_sirala_anahtari)
