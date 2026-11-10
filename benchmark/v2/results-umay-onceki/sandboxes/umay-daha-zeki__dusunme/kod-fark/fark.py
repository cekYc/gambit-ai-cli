def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    İki satır listesi arasındaki minimal düzenleme dizisini (diff) döndürür.
    Ortak satırları maksimize eder (LCS).
    Minimal düzenleme kısıtını sağlamak için geri izleme sırasında silmeler (-) eklemeler (+)den önce tercih edilir.
    """
    m = len(a)
    n = len(b)

    # DP tablosu: dp[i][j] = a[:i] ve b[:j] arasındaki LCS uzunluğu
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                # En uzun ortak alt diziyi korumak için max(silme, ekleme) alınır
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])

    # Geri izleme (Traceback)
    diff = []
    i, j = m, n

    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i-1] == b[j-1]:
            # Eşleşme: Ortak satır (' ')
            diff.append((' ', a[i-1]))
            i -= 1
            j -= 1
        elif i > 0 and j > 0:
            # Eşleşme yok. LCS'yi koruyarak, kısıta uygun (silme önce) karar verilir.
            if dp[i-1][j] > dp[i][j-1]:
                # Silme (a'dan) tercih edilir (Daha uzun LCS yolu)
                diff.append(('-', a[i-1]))
                i -= 1
            elif dp[i][j-1] > dp[i-1][j]:
                # Ekleme (b'ye) tercih edilir (Daha uzun LCS yolu)
                diff.append(('+', b[j-1]))
                j -= 1
            else: # dp[i-1][j] == dp[i][j-1] (Eşit LCS)
                # Kısıt: Silmeler eklemelerden önce gelsin. Eşitlik durumunda '-' tercih edilir.
                diff.append(('-', a[i-1]))
                i -= 1
        elif i > 0: # Sadece a kaldı (Silme)
            diff.append(('-', a[i-1]))
            i -= 1
        elif j > 0: # Sadece b kaldı (Ekleme)
            diff.append(('+', b[j-1]))
            j -= 1

    # Diff dizisi tersten oluşturulduğu için tersine çevir
    return diff[::-1]
