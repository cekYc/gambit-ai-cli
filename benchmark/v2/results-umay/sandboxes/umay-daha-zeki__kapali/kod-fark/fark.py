def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    a satır listesini b'ye çeviren minimal düzenleme dizisi döndürür.
    En uzun ortak alt diziyi (LCS) baz alarak minimum edit mesafesi ile
    operasyonları (' ', '-', '+') bulur. Silmeler, eklemelerden önce gelir.
    """
    m, n = len(a), len(b)
    
    # Edit Distance (Levenshtein benzeri) DP tablosu
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i  # Silme maliyeti
    for j in range(n + 1):
        dp[0][j] = j  # Ekleme maliyeti

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            # Minimum maliyet: Silme, Ekleme, Eşleşme/Değiştirme
            dp[i][j] = min(
                dp[i-1][j] + 1,      # Silme (a'dan çıkar)
                dp[i][j-1] + 1,      # Ekleme (b'ye ekle)
                dp[i-1][j-1] + cost  # Eşleşme (cost=0) veya Değiştirme (cost=1)
            )

    # Geri izleme (Backtracking) ile en kısa yolu bulma
    path_raw = []
    i, j = m, n
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            # Ortak satır
            path_raw.append((' ', a[i-1]))
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i][j] == dp[i-1][j] + 1):
            # Silme (En düşük maliyet veya j=0)
            path_raw.append(('-', a[i-1]))
            i -= 1
        elif j > 0 and (i == 0 or dp[i][j] == dp[i][j-1] + 1):
            # Ekleme (En düşük maliyet veya i=0)
            path_raw.append(('+', b[j-1]))
            j -= 1
        # Not: Değiştirme (cost=1) durumu, istenen operasyonlar (' ', '-', '+') ile uyumlu olmadığı için
        # otomatik olarak silme+ekleme (toplam maliyet 2) veya doğrudan silme/ekleme yolunu takip eder.
        else:
            break
    
    path_raw.reverse()
    
    # Kural Uygulama: Ardışık değişikliklerde silmeler eklemelerden önce gelsin.
    final_path = []
    i = 0
    while i < len(path_raw):
        op, satir = path_raw[i]
        
        if op == ' ': # Ortak satırları olduğu gibi al
            final_path.append((op, satir))
            i += 1
        else:
            # Ardışık +/- bloğunu bul
            block = []
            k = i
            while k < len(path_raw) and path_raw[k][0] in ('+', '-'):
                block.append(path_raw[k])
                k += 1
            
            # Kurala göre sıralama: Silmeler ( - ) önce, sonra Eklemeler ( + )
            silmeler = [item for item in block if item[0] == '-']
            eklemeler = [item for item in block if item[0] == '+']
            
            final_path.extend(silmeler)
            final_path.extend(eklemeler)
            
            i = k
            
    return final_path
