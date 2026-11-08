"""Paket kurulum sırası (topolojik sıralama) modülü.

Standart kitaplık ile yazılmıştır; binlerce paketli bağımlılık grafinde de
hızlı ve deterministik sonuç üretir.
"""


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde döngü bulunduğunda fırlatılır.

    Attributes:
        dongu: Döngüyü oluşturan paketlerin listesi. Her paket listede
            kendisinden sonraki pakete bağımlıdır ve sonuncusu ilkine
            bağımlıdır. Liste döngüdeki alfabetik olarak en küçük paketle
            başlar (kendine bağımlı paket için ["x"] şeklindedir).
    """

    def __init__(self, dongu: list[str]):
        super().__init__(f"DonguHatasi: {dongu}")
        self.dongu = dongu


def _donguyu_bul(baslangic: str, dugumler: set[str], kenar: dict[str, list[str]]) -> list[str] | None:
    """Verilen başlangıçtan çıkan bir döngüyü bulur.

    Bulunan döngü, listedeki her elemanın sıradaki elemana bağlı olduğu,
    sonuncunun ise ilkine bağlı olduğu biçimdedir ve alfabetik olarak en
    küçük paketle başlar.
    """
    path: list[str] = [baslangic]
    in_path: dict[str, int] = {baslangic: 0}

    def dfs(node: str) -> list[str] | None:
        for nxt in sorted(kenar.get(node, [])):
            if nxt not in dugumler:
                continue
            if nxt in in_path:
                # Döngü bulundu: in_path[nxt] ... son (nxt tekrar eklenmez)
                return path[in_path[nxt]:]
            path.append(nxt)
            in_path[nxt] = len(path) - 1
            sonuc = dfs(nxt)
            if sonuc is not None:
                return sonuc
            path.pop()
            del in_path[nxt]
        return None

    return dfs(baslangic)


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """Bağımlılıklara göre paket kurulum sırasını döndürür.

    Args:
        deps: Anahtar her paketin adı, değer o paketten önce kurulması
            gereken paketlerin listesi. Yalnızca bağımlılık olarak geçen
            paketler de sonuçta yer alır.

    Returns:
        Her paket kendi bağımlı olduğu paketlerden sonra gelen, alfabetik
        kuralı ile sıralanmış paket isimleri listesi.

    Raises:
        DonguHatasi: Bağımlılık grafiğinde döngü varsa.
    """
    # Tüm paketleri topla (anahtarlar ve sadece-bağımlılık olarak geçenler)
    dugumler: set[str] = set(deps.keys())
    for liste in deps.values():
        dugumler.update(liste)

    # Kenar: bagimli -> bagimlilik (bagimlilik önce kurulur)
    kenar: dict[str, list[str]] = {d: [] for d in dugumler}
    giris_derecesi: dict[str, int] = {d: 0 for d in dugumler}

    for bagimli, bagimliliklar in deps.items():
        for bagimlilik in bagimliliklar:
            if bagimlilik not in dugumler:
                continue
            # Aynı bağımlık iki kez yazılmış olabilir: tekilleştir
            if bagimlilik not in kenar[bagimli]:
                kenar[bagimli].append(bagimlilik)
                giris_derecesi[bagimlilik] += 1

    # Küçükten büyüğe sıralanmış kenar listeleri (deterministik çıkış)
    for d in dugumler:
        kenar[d].sort()

    # Kahn algoritması: o an kurabilecekler (giriş derecesi 0) alfabetik
    sıfır_giris: list[str] = sorted([d for d in dugumler if giris_derecesi[d] == 0])
    sonuc: list[str] = []

    while sıfır_giris:
        # Alfabetik olarak en küçük paketi seç
        mevcut = sıfır_giris.pop(0)
        sonuc.append(mevcut)

        for komşu in kenar[mevcut]:
            giris_derecesi[komşu] -= 1
            if giris_derecesi[komşu] == 0:
                sıfır_giris.append(komşu)
                sıfır_giris.sort()

    if len(sonuc) != len(dugumler):
        # Döngü var: döngüyü oluşturan paketleri bul
        kalan = set(dugumler) - set(sonuc)
        for baslangic in sorted(kalan):
            dongu = _donguyu_bul(baslangic, dugumler, kenar)
            if dongu is not None:
                raise DonguHatasi(dongu)
        # Güvenlik amaçlı (asla buraya düşmemesi gerekir)
        raise DonguHatasi(sorted(kalan))

    return sonuc

if __name__ == "__main__":
    # Hızlı manuel test
    print(kurulum_sirasi({"a": ["b", "c"], "b": ["c"], "c": []}))  # ['c', 'b', 'a']
    try:
        kurulum_sirasi({"a": ["b"], "b": ["a"]})
    except DonguHatasi as e:
        print("dongu:", e.dongu)  # ['a', 'b']
    try:
        kurulum_sirasi({"x": ["x"]})
    except DonguHatasi as e:
        print("kendine:", e.dongu)  # ['x']
