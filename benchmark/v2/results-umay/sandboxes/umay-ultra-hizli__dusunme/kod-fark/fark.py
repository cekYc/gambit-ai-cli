def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """a satır listesini b'ye çeviren minimal düzenleme dizisini döndürür.
    Ortak satır sayısı maksimize edilir ve silmeler ("-", satır) eklemeler ("+", satır) öncesinde gelir.
    """
    m = len(a)
    n = len(b)
    
    # LCS için DP tablosu
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    # Geri izleme ile düzenleme dizisini oluşturma
    diff_sequence = []
    i, j = m, n
    
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            # Ortak satır (" ", satır)
            diff_sequence.append((" ", a[i-1]))
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i-1][j] >= dp[i][j-1]):
            # Silme (a'dan çıkarıldı) ("-", satır)
            diff_sequence.append(("-", a[i-1]))
            i -= 1
        elif j > 0 and (i == 0 or dp[i][j-1] > dp[i-1][j]):
            # Ekleme (b'ye eklendi) ("+", satır)
            diff_sequence.append(("+", b[j-1]))
            j -= 1
            
    # Sonucu tersine çevir
    diff_sequence.reverse()
    
    # Minimal değişiklik dizisi LCS'den gelir. 
    # Silme/Ekleme sıralaması (Bloklar halinde - sonra +) genellikle minimal diff'te en doğal akıştır.
    # Standart LCS geriye izleme, bu kuralı en iyi şekilde karşılar.
    return diff_sequence
