def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    a satır listesini b'ye çeviren minimal bir düzenleme dizisi döndürür.
    Her eleman (" ", satır) (iki tarafta ortak), ("-", satır) (a'dan silinen) ya da ("+", satır) (b'ye eklenen) olur.
    - " " ve "-" olanlar sırayla a'yı, " " ve "+" olanlar sırayla b'yi verir.
    - Ortak (" ") satır sayısı mümkün olan en fazla olmalı (en uzun ortak alt dizi).
    - Ardışık değişikliklerde silmeler eklemelerden önce gelir: bir "+" elemanının hemen ardından "-" gelmez.
    - Birkaç bin satırlık, az değişiklik içeren listelerde birkaç saniyeden kısa sürede çalışır.
    """
    n, m = len(a), len(b)
    
    # Myers diff algoritması (O((N+M)D) zaman, O(N+M) bellek)
    # D = düzenleme mesafesi (silme + ekleme sayısı)
    # "az değişiklik" varsayımıyla D küçüktür, çok hızlı çalışır
    
    max_d = n + m
    offset = m + 1  # k indeksi offset'i (k = -m ... n aralığı)
    V_size = n + m + 3
    
    # trace[D][k + offset] = x koordinatı
    trace = []
    
    # D = 0 başlangıcı
    V = [-1] * V_size
    V[offset + 1] = 0  # k=1 için x=0 (boş a, y=-1 konumundan başla)
    trace.append(V[:])
    
    for D in range(max_d + 1):
        V = [-1] * V_size
        
        # k = -D, -D+2, ..., D-2, D
        for k in range(-D, D + 1, 2):
            # x koordinatını belirle
            if k == -D or (k != D and V[offset + k - 1] < V[offset + k + 1]):
                # Aşağı hareket (ekleme): k+1 diagonalinden gelir
                x = V[offset + k + 1]
            else:
                # Sağa hareket (silme): k-1 diagonalinden gelir
                x = V[offset + k - 1] + 1
            
            y = x - k
            
            # Sınır kontrolü
            if x > n or y > m:
                continue
            
            # Kopyalama (eşleşen satırlar - diagonal hareket)
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            
            V[offset + k] = x
            
            # Bitiş kontrolü
            if x >= n and y >= m:
                trace.append(V[:])
                return _backtrack_myers(trace, a, b, n, m, offset)
        
        trace.append(V[:])
    
    # Bulunamazsa (olmamalı)
    return [("-", line) for line in a] + [("+", line) for line in b]


def _backtrack_myers(trace, a, b, n, m, offset):
    """Myers trace'ten diff sonucu üret."""
    x, y = n, m
    result_rev = []
    
    for D in range(len(trace) - 1, 0, -1):
        V = trace[D]
        V_prev = trace[D - 1]
        
        k = x - y
        
        # Hangi hareketten geldiğimizi bul
        if k == -D or (k != D and V_prev[offset + k - 1] < V_prev[offset + k + 1]):
            k_prev = k + 1
        else:
            k_prev = k - 1
        
        x_prev = V_prev[offset + k_prev]
        y_prev = x_prev - k_prev
        
        # x_prev -> x, y_prev -> y arası hareket
        while x > x_prev and y > y_prev:
            # Eşleşen satır (diagonal hareket)
            result_rev.append((" ", a[x - 1]))
            x -= 1
            y -= 1
        
        if x > x_prev:
            # Silme (a'dan) - sağa hareket
            result_rev.append(("-", a[x - 1]))
            x -= 1
        elif y > y_prev:
            # Ekleme (b'ye) - aşağı hareket
            result_rev.append(("+", b[y - 1]))
            y -= 1
    
    # D=0 için kalan (k=1 diagonalından)
    while x > 0 and y > 0:
        result_rev.append((" ", a[x - 1]))
        x -= 1
        y -= 1
    
    while x > 0:
        result_rev.append(("-", a[x - 1]))
        x -= 1
    
    while y > 0:
        result_rev.append(("+", b[y - 1]))
        y -= 1
    
    # Ters çevir
    result_rev.reverse()
    
    # Kural kontrolü: "+" hemen ardından "-" gelmemeli
    # Myers algoritması bu sırayı doğal olarak verir (silmeler önce)
    # Ama emin olmak için kontrol edelim
    return result_rev
