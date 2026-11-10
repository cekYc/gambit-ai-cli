class DonguHatasi(ValueError):
    """Bağımlılık döngüsü oluştuğunda fırlatılır."""
    def __init__(self, dongu: list[str]):
        super().__init__("Bağımlılık döngüsü tespit edildi: " + " -> ".join(dongu) + " -> " + dongu[0])
        self.dongu = dongu

def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """Paket bağımlılıklarına göre kuruluma uygun sıralamayı hesaplar."""
    # Tüm paketleri (bağımlılıklar dahil) topla
    tum_paketler = set(deps.keys())
    for deps_list in deps.values():
        tum_paketler.update(deps_list)
    
    # Bağımlılık grafiğini (adj list) oluştur
    # Girdi: deps[A] = [B, C] -> A, B ve C'ye bağımlı. Yani B->A ve C->A (Kurulma sırası: önce B, C sonra A)
    # Grafikte: Bağımlıdan bağımlılığına ok çekmeliyiz: B -> A, C -> A
    graph = {pkg: [] for pkg in tum_paketler}
    in_degree = {pkg: 0 for pkg in tum_paketler}
    
    # Bağımlılık ilişkilerini grafiğe dönüştür ve in_degree'u hesapla
    for paket, bagimlilar in deps.items():
        for bagimli_paket in bagimlilar:
            if bagimli_paket not in tum_paketler: # Tanımlı olmayan bağımlılıklar varsa hata verebiliriz ama kurala göre tüm paketler toplanmalı.
                continue
            # İlişki: bagimli_paket -> paket (Önce bağımlılık kurulur)
            # Bu, Topolojik Sıralama için doğru yönlü kenardır.
            if paket not in graph[bagimli_paket]: # Tekrarlayan kenarları önle
                graph[bagimli_paket].append(paket)
                in_degree[paket] += 1

    # Kahn's Algoritması ile Topolojik Sıralama
    # Başlangıçta in_degree'u 0 olan tüm paketleri bul
    queue = []
    for pkg, degree in in_degree.items():
        if degree == 0:
            queue.append(pkg)
    
    # İlk kurulumda alfabetik sıralama kuralı için queue'yu sırala
    queue.sort()
    
    sonuc = []
    
    while queue:
        # En küçük alfabetik paketi seç
        mevcut_paket = queue.pop(0)
        sonuc.append(mevcut_paket)
        
        # Komşularını (bağımlılığı olanları) işle
        sonraki_komsu_lar = sorted(graph[mevcut_paket]) # Alfabetik sırayla işlemek sonraki seçimi etkilemez ama tutarlılık sağlar.
        
        yeni_queue_eklemeler = []
        for komsu in sonraki_komsu_lar:
            in_degree[komsu] -= 1
            if in_degree[komsu] == 0:
                yeni_queue_eklemeler.append(komsu)
        
        # Yeni sıfırlanan düğümleri mevcut queue'nun sonuna, alfabetik sırayla ekle
        yeni_queue_eklemeler.sort()
        queue.extend(yeni_queue_eklemeler)

    # Döngü kontrolü
    if len(sonuc) != len(tum_paketler):
        # Döngü tespiti için en karmaşık kısım: Hangi paketler döngüde?
        # Sıralanmamış (in_degree > 0) tüm paketler döngünün bir parçasıdır.
        dongu_paketleri = [pkg for pkg, degree in in_degree.items() if degree > 0]
        
        # Döngüdeki paketleri al, alfabetik olarak sırala
        dongu_paketleri.sort()
        
        # Döngü yolunu bulmak için DFS kullanabiliriz (Basitlik ve standart kütüphane kısıtlaması nedeniyle).
        # En küçük alfabetik paketle başlayan döngüyü bulmalıyız.
        if not dongu_paketleri: # Güvenlik kontrolü
             raise ValueError("Beklenmedik hata: Döngü paketleri bulunamadı.")
             
        baslangic_paketi = dongu_paketleri[0]
        
        # DFS ile döngüyü takip et (Yalnızca döngüde olanlar arasında)
        path = []
        visited_in_cycle = set()
        
        def find_cycle(u, start_node):
            path.append(u)
            visited_in_cycle.add(u)
            
            # Sadece döngüdeki diğer düğümlere bak
            for v in graph[u]:
                if v in dongu_paketleri:
                    if v == start_node and len(path) >= 1: # Döngü tamamlandı
                        return True
                    if v not in visited_in_cycle:
                        if find_cycle(v, start_node):
                            return True
            
            path.pop()
            return False

        # Başlangıç paketinden döngüyü bulmaya çalış
        if find_cycle(baslangic_paketi, baslangic_paketi):
            # Path döngüyü içerir: [a, b, c]. Sonraki a'dır.
            # Kural: Liste döngüdeki alfabetik olarak en küçük paketle başlar.
            # find_cycle, başlangıç paketi (en küçük) ile başlar ve döngüyü tamamladığında 'path' son haliyle döngüyü tutar.
            return DonguHatasi(path)
        
        # Eğer yukarıdaki DFS ile döngü bulunamadıysa (teorik olarak olmamalı, çünkü in_degree > 0 olanlar döngüde olmalı),
        # en azından döngüdeki tüm paketleri alfabetik olarak döndür.
        return DonguHatasi(dongu_paketleri)

    return sonuc
