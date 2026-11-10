class DonguHatasi(ValueError):
    """Bağımlılık döngüsünü belirtir."""
    def __init__(self, dongu: list[str]):
        super().__init__(f"Bağımlılık döngüsü tespit edildi: {dongu}")
        self.dongu = dongu

def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """Bağımlılık grafiği üzerinde Topolojik Sıralama yapar."""
    
    # 1. Tüm düğümleri (paketleri) topla
    tum_paketler = set(deps.keys())
    for paketler in deps.values():
        tum_paketler.update(paketler)
    
    # Paketleri alfabetik sıraya koy ve listeye çevir (sadece benzersiz olanlar)
    siralanmis_paketler = sorted(list(tum_paketler))
    
    # 2. Bağımlılık grafiğini ve girilen derece (in-degree) hesapla
    graph = {paket: [] for paket in tum_paketler}
    in_degree = {paket: 0 for paket in tum_paketler}
    
    for paket, bagimlilar in deps.items():
        for bagim_paket in bagimlilar:
            # Bağımlılık yönü: bagim_paket -> paket
            # Yani paket, bagim_paket'ten sonra kurulur.
            
            if bagim_paket not in tum_paketler: # Bu durum teorik olarak olmamalı ama güvenli olalım
                 continue

            # Grafikteki ok yönü: Bağımlı -> Bağımlılık (Topolojik sıralama için gelen kenar sayısını bulmalıyız)
            # deps[A] = [B] demek, B'nin A'dan önce kurulması gerektiği demektir (B -> A)
            # Bizim grafiğimizde: B'nin A'ya bağımlılığı var.
            
            # A'yı kurmak için B'nin kurulması gerekir. Ok yönü: B -> A
            graph[bagim_paket].append(paket) # B'den A'ya ok
            in_degree[paket] += 1
    
    # 3. Kahn Algoritması ile sıralama yap (Öncelik: Alfabetik küçük olan)
    # Kuyruk yerine, her seferinde en küçük alfabetik değere sahip olanı seçmek için bir küme veya min-heap kullanacağız.
    # Standart kütüphane kısıtlaması var, bu yüzden bir liste ve sürekli sıralama/min eleman seçimi yapacağız (küçük paket sayısı için yeterli).
    
    # Başlangıçta in_degree'u 0 olan paketleri topla ve sırala
    uygun_paketler = sorted([paket for paket in tum_paketler if in_degree[paket] == 0])
    kurulum_sirasi_listesi = []
    
    while uygun_paketler:
        # Alfabetik olarak en küçük olanı seç (Zaten sıralı tutuyoruz)
        mevcut_paket = uygun_paketler.pop(0)
        kurulum_sirasi_listesi.append(mevcut_paket)
        
        # Komşularını işle
        komsu_paketler = sorted(graph[mevcut_paket]) # Komşuları alfabetik sırayla işle
        
        yeni_uygun_paketler = []
        for komsu in komsu_paketler:
            in_degree[komsu] -= 1
            if in_degree[komsu] == 0:
                yeni_uygun_paketler.append(komsu)
        
        # Yeni uygun olanları mevcut listenin içine ekle ve tekrar sırala
        uygun_paketler.extend(yeni_uygun_paketler)
        uygun_paketler.sort()

    # 4. Döngü kontrolü
    if len(kurulum_sirasi_listesi) != len(tum_paketler):
        # Döngü var, döngüdeki paketleri bulmalıyız.
        # Bir geriye izleme (DFS) ile döngüyü bulalım.
        visited = set()
        recursion_stack = set()
        dongu_paketleri = set()

        def dfs_find_cycle(u, path): # path, o anki yürüyüş yolu (sıralı liste)
            nonlocal dongu_paketleri
            visited.add(u)
            recursion_stack.add(u)
            path.append(u)
            
            for v in graph[u]: # u -> v okları
                if v in recursion_stack:
                    # Döngü bulundu: v'den başlar ve u'ya kadar uzanır (v...u->v)
                    # Döngüyü oluşturan elemanlar, path içinde v'nin ilk geçtiği yerden sonraki elemanlardır.
                    cycle_start_index = path.index(v)
                    cycle = path[cycle_start_index:]
                    
                    # Kural: Liste döngüdeki alfabetik olarak en küçük paketle başlamalı.
                    min_paket = min(cycle)
                    min_index = cycle.index(min_paket)
                    
                    # Döngüyü min_paket'ten başlatarak döndür
                    final_cycle = cycle[min_index:] + cycle[:min_index]
                    
                    raise DonguHatasi(final_cycle)
                
                if v not in visited:
                    dfs_find_cycle(v, path)
            
            path.pop()
            recursion_stack.remove(u)
        
        # Tüm paketler üzerinde DFS yap
        for paket in siralanmis_paketler:
            if paket not in visited:
                try:
                    dfs_find_cycle(paket, [])
                except DonguHatasi as e:
                    # Hata yakalanır ve fonksiyon dışına fırlatılır
                    raise e

    return kurulum_sirasi_listesi
