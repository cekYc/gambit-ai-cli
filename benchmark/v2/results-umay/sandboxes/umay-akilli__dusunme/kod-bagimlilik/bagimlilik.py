import heapq
from collections import defaultdict


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde döngü tespit edildiğinde fırlatılır."""
    def __init__(self, dongu: list[str]):
        self.dongu = dongu
        super().__init__(f"Bağımlılık döngüsü tespit edildi: {' -> '.join(dongu)}")


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """
    Topolojik sıralama (Kahn algoritması) ile paket kurulum sırasını belirler.
    
    Args:
        deps: Her paketin bağımlılıklarını içeren sözlük. Anahtar paket adı,
              değer o paketin kurulması için önce kurulması gereken paketler listesi.
    
    Returns:
        Tüm paketlerin (bağımlılık olarak geçenler dahil) kurulum sırasını içeren liste.
        Her paket kendi bağımlılıklarından sonra gelir. Aynı anda kurulabilecek birden
        fazla paket varsa alfabetik olarak en küçüğü önce gelir.
    
    Raises:
        DonguHatasi: Bağımlılık grafiğinde döngü varsa, döngüyü oluşturan paketlerin
                     listesiyle (alfabetik en küçüğüyle başlayacak şekilde).
    """
    # Tüm paketleri topla (anahtarlar + bağımlılık olarak geçenler)
    tum_paketler = set(deps.keys())
    for bagimlilar in deps.values():
        tum_paketler.update(bagimlilar)
    
    # Giriş dereceleri ve komşuluk listesi oluştur
    giris_derecesi = {p: 0 for p in tum_paketler}
    komsuluk = defaultdict(list)
    
    for paket, bagimlilar in deps.items():
        # Tekrar eden bağımlılıkları temizle
        benzersiz_bagimlilar = set(bagimlilar)
        for bagimli in benzersiz_bagimlilar:
            komsuluk[bagimli].append(paket)
            giris_derecesi[paket] += 1
    
    # Giriş derecesi 0 olan paketleri min-heap'e ekle (alfabetik sıra için)
    heap = [p for p, d in giris_derecesi.items() if d == 0]
    heapq.heapify(heap)
    
    sonuc = []
    
    while heap:
        paket = heapq.heappop(heap)
        sonuc.append(paket)
        
        for komsu in komsuluk[paket]:
            giris_derecesi[komsu] -= 1
            if giris_derecesi[komsu] == 0:
                heapq.heappush(heap, komsu)
    
    # Döngü kontrolü: işlenemeyen paketler varsa döngü vardır
    if len(sonuc) != len(tum_paketler):
        # Döngüyü bul: kalan paketler üzerinden DFS ile döngüyü tespit et
        kalan = {p for p in tum_paketler if p not in sonuc}
        
        # Kalan paketler üzerinde döngü bul
        dongu = _dongu_bul(kalan, komsuluk, deps)
        raise DonguHatasi(dongu)
    
    return sonuc


def _dongu_bul(kalan_paketler: set[str], komsuluk: dict[str, list[str]], 
                deps: dict[str, list[str]]) -> list[str]:
    """Kalan paketler içinde bir döngü bulur ve alfabetik en küçüğüyle başlayan liste döndürür.
    
    Dönüş formatı: her paket kendisinden sonrakine bağımlıdır (paket -> next), sonuncusu ilki.
    """
    # Bağımlılık yönünde komşuluk: paket -> onun bağımlılıkları (sadece kalan paketler)
    bagimlilik_grafi = defaultdict(list)
    for paket in kalan_paketler:
        for bagimli in set(deps.get(paket, [])):
            if bagimli in kalan_paketler:
                bagimlilik_grafi[paket].append(bagimli)
    
    # DFS ile döngü bul (bağımlılık yönünde: paket -> bağımlılığı)
    ziyaret_edildi = set()
    yigin = set()
    ebeveyn = {}
    
    def dfs(dugum: str) -> list[str] | None:
        ziyaret_edildi.add(dugum)
        yigin.add(dugum)
        
        for bagimli in sorted(bagimlilik_grafi[dugum]):  # Alfabetik sıra için sıralı gezin
            if bagimli not in ziyaret_edildi:
                ebeveyn[bagimli] = dugum
                sonuc = dfs(bagimli)
                if sonuc:
                    return sonuc
            elif bagimli in yigin:
                # Döngü bulundu - geriye doğru izle (bağımlılık yönünde)
                dongu = [bagimli]
                g = dugum
                while g != bagimli:
                    dongu.append(g)
                    g = ebeveyn[g]
                dongu.append(bagimli)
                dongu.reverse()  # artık bağımlılık yönünde: a->b->c->a
                return dongu
        
        yigin.remove(dugum)
        return None
    
    # Alfabetik sırayla başla ki en küçük paketle başlayan döngü bulunsun
    for paket in sorted(kalan_paketler):
        if paket not in ziyaret_edildi:
            dongu = dfs(paket)
            if dongu:
                # dongu şu an: [a, b, c, a] formatında (bağımlılık yönünde)
                # Son eleman tekrar, çıkar
                dongu = dongu[:-1]
                # Alfabetik en küçük elemanla başlat
                min_indeks = min(range(len(dongu)), key=lambda i: dongu[i])
                dongu = dongu[min_indeks:] + dongu[:min_indeks]
                return dongu
    
    # Fallback (olmamalı)
    return sorted(kalan_paketler)[:1]
