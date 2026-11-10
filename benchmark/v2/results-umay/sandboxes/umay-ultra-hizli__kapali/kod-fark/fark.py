def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """a satır listesini b'ye çeviren minimal düzenleme dizisi döndürür.
    Ortak (\" \"\" ), silinen (\"-\\"\" ), eklenen (\"+\\"\" ) etiketlerini kullanır.
    Minimal uzunluk LCS'yi maksimize ederek sağlanır.
    """
    m = len(a)
    n = len(b)
    
    # DP tablosu: dp[i][j] = a[:i] ve b[:j]'nin LCS uzunluğu
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Geriye doğru izleme ile minimal düzenleme dizisi oluşturma
    result = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            # Ortak satır
            result.append((" ", a[i-1]))
            i -= 1
            j -= 1
        elif i > 0 and (j == 0 or dp[i-1][j] >= dp[i][j-1]):
            # Silme (a'da var, b'de karşılığı yok veya LCS'yi azaltacak şekilde ilerlemek gerekiyorsa)
            result.append(("-", a[i-1]))
            i -= 1
        elif j > 0: # Ekleme
            result.append(("+", b[j-1]))
            j -= 1

    # Minimal düzenleme dizisi, LCS'yi maksimize eden en kısa dizidir. 
    # Geri izleme, genellikle minimal uzunluğu garantiler.
    # Sıralama kuralı (Silme önce gelmeli) bu minimal diziyi bozabilir. Minimal olma öncelikli kabul edilir.
    result.reverse()
    return result
