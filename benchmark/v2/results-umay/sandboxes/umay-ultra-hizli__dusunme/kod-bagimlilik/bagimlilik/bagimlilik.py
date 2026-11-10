import heapq
from typing import Dict, List

class DonguHatasi(ValueError):
    """Bağımlılık döngüsü tespit edildiğinde fırlatılır."""
    def __init__(self, dongu: List[str]):
        self.dongu = dongu
        super().__init__(f"Bağımlılık döngüsü tespit edildi: {dongu}")

def kurulum_sirasi(deps: Dict[str, List[str]]) -> List[str]:
    """Bağımlılık grafiğini topolojik olarak sıralar. Kurulabilir paketler arasında alfabetik sırayı esas alır.

    Args:
        deps: Her paketin kurulmadan önce ihtiyaç duyduğu bağımlılıkları (paket_adı: [bağımlılık1, bağımlılık2]) içeren sözlük.

    Returns:
        Topolojik olarak sıralanmış paket listesi.

    Raises:
        DonguHatasi: Bir bağımlılık döngüsü varsa.
    """
    # 1. Tüm düğümleri ve in-degree'leri belirle
    tum_paketler = set(deps.keys())
    for bağımlılık_listesi in deps.values():
        tum_paketler.update(bağımlılık_listesi)

    # Tüm paketlerin in-degree'sini ve bağlı olduğu paketleri (adj list) tut
    in_degree: Dict[str, int] = {paket: 0 for paket in tum_paketler}
    adj: Dict[str, List[str]] = {paket: [] for paket in tum_paketler}

    # Bağımlılık ilişkilerini kur ve in_degree'yi hesapla
    # Yön: Bağımlılık -> Bağımlı
    for paket, bağımlilikler in deps.items():
        for bağımlılık in bağımlilikler:
            adj[bağımlılık].append(paket)
            in_degree[paket] += 1

    # 2. Başlangıç sırasındaki (in_degree = 0) paketleri min-heap'e ekle
    pq = []
    for paket in tum_paketler:
        if in_degree[paket] == 0:
            heapq.heappush(pq, paket)

    sirali_paketler: List[str] = []

    # 3. Kahn Algoritması
    while pq:
        # Alfabetik olarak en küçük paketi al
        u = heapq.heappop(pq)
        sirali_paketler.append(u)

        # u'ya bağımlı tüm paketleri işle
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(pq, v)

    # 4. Döngü Kontrolü
    if len(sirali_paketler) != len(tum_paketler):
        # Döngü var. Döngüdeki paketleri bulmak için in_degree > 0 olanları kullan.
        dongu_paketler = [paket for paket in tum_paketler if in_degree[paket] > 0]
        
        # Döngüdeki paketleri alfabetik olarak sırala (istek uyarınca)
        dongu_paketler.sort()
        
        # Döngü hatası fırlatılır
        raise DonguHatasi(dongu=dongu_paketler)

    return sirali_paketler