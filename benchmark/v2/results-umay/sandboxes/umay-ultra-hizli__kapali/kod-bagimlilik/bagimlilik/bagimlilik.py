class DonguHatasi(ValueError):
    """Bağımlılık döngüsü oluştuğunda fırlatılır."""
    def __init__(self, dongu: list[str]):
        super().__init__("Bağımlılık döngüsü tespit edildi.")
        self.dongu = dongu

def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """Bağımlılıklara göre paket kurulum sırasını belirler."""
    
    # Tüm paketleri (bağımlılıklar dahil) topla ve benzersiz yap
    tumu_paketler = set(deps.keys())
    for deps_list in deps.values():
        tumu_paketler.update(deps_list)
    
    # Grafik yapısını oluştur: paket -> bağımlılıklar (önce kurulması gerekenler)
    # Bağımlılık grafiği: A -> B demek B'nin A'ya bağımlı olduğu anlamına gelir (A önce kurulur)
    grafik = {paket: set(deps.get(paket, [])) for paket in tumu_paketler}
    
    # Ters grafik (Kim kime bağımlı?): bağımlılık -> bağımlı paketler
    ters_grafik = {paket: set() for paket in tumu_paketler}
    for paket, bagimlilar in grafik.items():
        for bagimli in bagimlilar:
            if bagimli in tumu_paketler: # Sadece bilinen paketleri ele al
                ters_grafik[bagimli].add(paket)
            
    # Topolojiyi bulmak için Kahn Algoritması (In-degree tabanlı)
    in_degree = {paket: len(grafik[paket]) for paket in tumu_paketler}
    
    # Başlangıçta sıfır in-degree'ye sahip paketleri bul (kurulabilir olanlar)
    kurulabilirler = sorted([paket for paket in tumu_paketler if in_degree[paket] == 0])
    kurulum_sirasi_listesi = []
    
    while kurulabilirler:
        # Alfabetik olarak en küçüğü seç (Tek ve belirli sonuç için kural)
        aktif_paket = kurulabilirler.pop(0) 
        kurulum_sirasi_listesi.append(aktif_paket)
        
        # Bu pakete bağımlı olanları (ters_grafikteki) güncelle
        siradaki_paketler = sorted(list(ters_grafik[aktif_paket]))
        
        for sonraki_paket in siradaki_paketler:
            in_degree[sonraki_paket] -= 1
            # Eğer in-degree sıfıra düştüyse, kurulabilirler listesine ekle
            if in_degree[sonraki_paket] == 0:
                # Yeni eklenenler de alfabetik sırada kalmalı
                # Basitlik için, listeye ekleyip sonra tekrar sıralayalım veya uygun yere yerleştirelim.
                # En basit ve doğru yol: listenin sonuna ekleyip sıralamak.
                kurulabilirler.append(sonraki_paket)
        
        # Yeni eklenenleri sıraya koyarak (alfabetik olarak) listenin bütünlüğünü koru
        kurulabilirler.sort()

    # Döngü kontrolü
    if len(kurulum_sirasi_listesi) != len(tumu_paketler):
        # Döngü varsa, döngüdeki paketleri bulmalıyız.
        # Kalan in_degree > 0 olanlar döngüde.
        dongu_paketleri = [paket for paket in tumu_paketler if in_degree[paket] > 0]
        
        # Döngüdeki paketler arasında gerçek döngüyü tespit et (Tarama ile)
        # Döngüdeki paketler üzerinde DFS veya basit takip yapabiliriz.
        
        # Döngüdeki paketleri alfabetik sıraya koyarak başlat
        dongu_paketleri.sort()
        
        # Basit döngü tespiti (Paket -> Bağımlılık) üzerinden
        # Bu paketler arasında bir döngü var demektir.
        # En küçük alfabetik paketle başlayan döngüyü bulmak için:
        
        # Basit bir döngü takip mekanizması (DFS benzeri, sadece döngü üyelerini bulur)
        def find_cycle(start_node: str) -> list[str] | None:
            path = [start_node]
            visited_in_path = {start_node}
            current = start_node
            
            while True:
                # Mevcut paketin bağımlılıkları arasında döngüdeki bir sonraki paketi bul
                bağımlılıklar = grafik.get(current, set())
                
                # Sadece döngüdeki paketler arasında döngüyü izle
                potansiyel_sonraki = [b for b in bağımlılıklar if b in dongu_paketleri and b != start_node]
                
                if not potansiyel_sonraki:
                    break # Bu yolda döngü yok veya başlangıca dönmüyor
                
                # Döngüyü en küçük alfabetik elemanla başlatma kuralı nedeniyle,
                # döngüyü oluşturan *tüm* paketleri bulup, en küçüğünden başlatmalıyız.
                # DFS yaparken, kendisinden sonraki elemanı (alfabetik olarak) seçmeliyiz.
                
                # Döngüdeki paketler arasındaki alfabetik sırayı takip etmeliyiz.
                # Örn: a->b, b->c, c->a ise, a'dan başlamalıyız.
                
                # Basitleştirme: Döngüdeki tüm paketleri sıralayalım ve birbirine bağımlı olup olmadıklarını kontrol edelim.
                # Bu, karmaşık DFS yerine, döngüdeki elemanlar kümesi üzerinde en küçük elemandan başlayarak takip demektir.
                
                return None # Karmaşık döngü çözümü bu kapsamda basitçe uygulanmıyor, orijinal kurala odaklanalım.
        
        # Kural: Liste döngüdeki alfabetik olarak en küçük paketle başlar.
        # Döngüdeki tüm paketleri sırala ve ilk elemandan başlayarak takip et.
        dongu_paketleri.sort()
        start_node = dongu_paketleri[0]
        
        try:
            current_cycle_path = [start_node]
            current_node = start_node
            
            while True:
                # Bu düğümün bağımlılıkları içinden, döngüdeki ve henüz path'te olmayan (veya başlangıç düğümü olan) bir sonraki düğümü bul.
                # Kural gereği, bağımlılıklar arasında alfabetik sıralamaya göre ilerlemeliyiz.
                potansiyel_sonrakiler = sorted(list(grafik[current_node].intersection(set(dongu_paketleri)) - set(current_cycle_path)))
                
                if not potansiyel_sonrakiler:
                    # Eğer sadece başlangıç düğümüne bağımlıysa döngü tamamlanmıştır.
                    if start_node in grafik.get(current_node, set()):
                        return current_cycle_path
                    break # Döngü değil, sadece izole döngüde kalmış
                
                next_node = potansiyel_sonrakiler[0]
                
                if next_node == start_node: 
                    # Döngü tamamlandı
                    return current_cycle_path
                
                current_cycle_path.append(next_node)
                current_node = next_node
        
        except Exception: 
            # Karmaşık durumlar için fallback
            pass 

        # Basit bir döngü tespit mekanizması: Bir paket kendi bağımlılıkları içinde kendini içeriyor mu?
        # (Bu, kuralın en zor kısmıdır, basit bir DFS/Topological Sort ile çözülür.)
        # Tüm döngü üyeleri bulunduğuna göre, en küçükten başlayarak döngüyu takip et.
        
        # Basit döngü takip (Tarama): Döngüdeki her paketi al ve kendisini içeren bir döngü var mı diye bak.
        final_dongu = None
        for p in dongu_paketleri:
            path = [p]

            # DFS ile döngü tespiti
            stack = [(p, [p])] # (mevcut_paket, yol)
            while stack:
                node, current_path = stack.pop()
                
                for dep in grafik[node]:
                    if dep in dongu_paketleri and dep not in current_path:
                        new_path = current_path + [dep]
                        stack.append((dep, new_path))
                    
                    elif dep == p and len(current_path) > 1: # Döngü tamamlandı ve başlangıç noktası p'ye ulaştı
                        # Döngü bulundu. Başlangıç noktası en küçük alfabetik olmalı.
                        # Şu an p'den başladık. Eğer p, döngüdeki en küçükse kabul et.
                        if p == min(current_path):
                            final_dongu = current_path
                            break
            if final_dongu:
                break

        if final_dongu: 
            raise DonguHatasi(final_dongu)
        else:
             # Döngü olmamasına rağmen sıralama tamamlanamadıysa (grafik izole bileşenler içeriyorsa)
             # Bu, mantıksal bir hata ya da karmaşık bir durumdur, ancak kural gereği döngü varsayılmalı.
             # Basitçe, döngüdeki elemanların kendisini oluşturan bir döngü var varsayılır.
             dongu_paketleri.sort()
             raise DonguHatasi(dongu_paketleri)

    return kurulum_sirasi_listesi
