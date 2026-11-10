import heapq


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde bir döngü bulunduğunda fırlatılır."""

    def __init__(self, dongu):
        self.dongu = dongu
        super().__init__(f"Bagimlilik dongusu tespit edildi: {' -> '.join(dongu)}")


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """Topolojik sıralama döndürür; eşit seçeneklerde alfabetik olarak küçükten büyüğe.

    Parametreler
    ----------
    deps : dict[str, list[str]]
        Her anahtar bir pakettir; değerler o paketten önce kurulması gereken paketlerdir.
        Aynı bağımlılık birden fazla kez gelebilir.

    Döndürür
    --------
    list[str]
        Her paketin kendi bağımlılıklarından sonra gelen paketlerin sıralanmış listesi.

    Fırlatır
    --------
    DonguHatasi
        Grafikte bir döngü varsa. ``dongu`` özniteliği döngüyü oluşturan paketlerin listesi,
        alfabetik en küçük paketten başlar ve her paket listenin sonraki elemanına bağımlıdır;
        sonuncu ilke ba˙ğlıdır (kendine bağımlı paket için tek elemanlı liste).
    """
    # Tüm paketleri topla (anahtarlar ve bağımlılık olarak geçenler).
    paketler = set(deps.keys())
    for bagimliliklar in deps.values():
        paketler.update(bagimliliklar)

    # Adjacency listesi ve gelen kenar sayıları.
    # edge: dependency -> package (dependency önce kurulmalı)
    giden: dict[str, set[str]] = {p: set() for p in paketler}
    gelen: dict[str, int] = {p: 0 for p in paketler}

    for paket, bagimliliklar in deps.items():
        for bagimlilik in bagimliliklar:
            if bagimlilik not in giden:
                giden[bagimlilik] = set()
                gelen[bagimlilik] = 0
            if paket not in giden[bagimlilik]:
                giden[bagimlilik].add(paket)
                gelen[paket] += 1

    # Min-heap ile alfabetik olarak en küçük sıfır-gelen-kenarlı paketten başla.
    kuyruk = [p for p in paketler if gelen[p] == 0]
    heapq.heapify(kuyruk)

    sirali: list[str] = []
    while kuyruk:
        p = heapq.heappop(kuyruk)
        sirali.append(p)
        for komsu in giden[p]:
            gelen[komsu] -= 1
            if gelen[komsu] == 0:
                heapq.heappush(kuyruk, komsu)

    if len(sirali) != len(paketler):
        dongu_paketleri = set(paketler) - set(sirali)
        dongu = _bul_dongu(deps, dongu_paketleri)
        raise DonguHatasi(dongu)

    return sirali


def _bul_dongu(deps: dict[str, list[str]], dongu_paketleri: set[str]) -> list[str]:
    """Verilen paketler içinde bir döngü bulur ve formatlanmış liste döndürür."""
    # Kısıtlanmış adjacency: yalnızca döngü paketleri arasında.
    local: dict[str, list[str]] = {}
    for p in dongu_paketleri:
        local[p] = [b for b in deps.get(p, []) if b in dongu_paketleri]

    baslangic = min(dongu_paketleri)

    # DFS ile bir döngü bul; path içinde paketler, indeks ile hızlı back-edge tespiti.
    renk: dict[str, int] = {}  # 0 ziyaret edilmedi, 1 işlemde, 2 bitti
    yigin: list[str] = []
    pozisyon: dict[str, int] = {}

    def dfs(u: str) -> list[str] | None:
        renk[u] = 1
        pozisyon[u] = len(yigin)
        yigin.append(u)
        for v in local[u]:
            if renk.get(v, 0) == 1:
                # Geri kenar bulundu; yigin[pozisyon[v]:] bir döngü.
                dongu = yigin[pozisyon[v]:].copy()
                return dongu
            if renk.get(v, 0) == 0:
                sonuc = dfs(v)
                if sonuc is not None:
                    return sonuc
        yigin.pop()
        pozisyon.pop(u, None)
        renk[u] = 2
        return None

    dongu = dfs(baslangic)
    if dongu is None:
        # Fallback: komşuluk listesini dolaşarak döngü bul.
        for p in sorted(dongu_paketleri):
            if renk.get(p, 0) == 0:
                dongu = dfs(p)
                if dongu is not None:
                    break
    if dongu is None:
        dongu = [baslangic]

    return dongu


if __name__ == "__main__":
    # Hızlı manuel testler.
    print(kurulum_sirasi({"a": ["b"], "b": ["c"], "c": []}))  # ['c', 'b', 'a']
    print(kurulum_sirasi({"a": ["b", "b"], "b": ["a"]}))  # DonguHatasi ['a', 'b']
    print(kurulum_sirasi({"x": ["x"]}))  # DonguHatasi ['x']
    print(kurulum_sirasi({}))  # []
    print(kurulum_sirasi({"a": ["b"], "c": ["b"]}))  # ['b', 'a', 'c']
