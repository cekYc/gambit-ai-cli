def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    iki satır listedeki minimum düzeltme dizisini LCS (uzun ortak alt dizi)
    algoritmas%C4 %B0n %C3%gen olarak hesaplar.
    
    Döndürülen listedeki her eleman:
    - (" ", satır): hem a hem de b'de ortak olan satır
    - ("-", satır): a'da olan, b'da olmayan/silinen satır
    - ("+", satır): b'de olan, a'da olmayan/eklenen satır
    
    Kurallar:
    - " " ve "-" together a'yı, " " ve "+" together b'yi verir.
    - Ortak satırlar en fazla olmalı (LCS).
    - Ardışık değişikliklerde silmeler eklemelerden önce gelir;
      bir "+" elemanının hemen ardından "-" gelmesin.
    """
    n, m = len(a), len(b)

    # LCS (Uzun Ortak Alt Dizi) için DP tablosu oluştur
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # LCS'yi backtrack ile bul
    lcs_vals = []
    i, j = n, m
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            lcs_vals.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    lcs_vals.reverse()

    # LCS elemanları arasına göre fark dizisini oluştur
    # Her LCS elemanı için: önce a'dan silinenler (-), sonra b'ye eklenenler (+), ardından ortak (" ")
    result = []
    idx_a, idx_b = 0, 0

    for lcs_elem in lcs_vals:
        # a'dan LCS elemanının önündeki (veya içindeki) ekstra elemanlar -> silinir
        while idx_a < len(a) and a[idx_a] != lcs_elem:
            result.append(("-", a[idx_a]))
            idx_a += 1
        idx_a += 1  # LCS elemanı a'dan atlandı

        # b'ye LCS elemanının önündeki ekstra elemanlar -> eklendi
        while idx_b < len(b) and b[idx_b] != lcs_elem:
            result.append(("+", b[idx_b]))
            idx_b += 1
        idx_b += 1  # LCS elemanı b'den atlandı

        # Ortak elemanı ekle
        result.append((" ", lcs_elem))

    # Kalan a elemanları (son LCS sonrası) -> silinir
    while idx_a < len(a):
        result.append(("-", a[idx_a]))
        idx_a += 1

    # Kalan b elemanları (son LCS sonrası) -> eklendi
    while idx_b < len(b):
        result.append(("+", b[idx_b]))
        idx_b += 1

    return result


# Testler
if __name__ == "__main__":
    # Test 1: Basit fark
    a1 = ["1", "2", "3", "4", "5"]
    b1 = ["1", "3", "4", "6", "5"]
    r1 = satir_farki(a1, b1)
    print("Test 1:", r1)
    a_filtered = [s for op, s in r1 if op in (" ", "-")]
    b_filtered = [s for op, s in r1 if op in (" ", "+")]
    print("  a filter:", a_filtered, "==", a1, ":", a_filtered == a1)
    print("  b filter:", b_filtered, "==", b1, ":", b_filtered == b1)

    # Test 2: Boş liste
    r2 = satir_farki([], ["1", "2"])
    print("Test 2 (empty a):", r2)

    # Test 3: İntikal liste
    r3 = satir_farki(["1", "2"], ["1", "2"])
    print("Test 3 (identical):", r3)

    # Test 4: Tamamen farklı
    r4 = satir_farki(["1", "2"], ["3", "4"])
    print("Test 4 (different):", r4)
    a_f = [s for op, s in r4 if op in (" ", "-")]
    b_f = [s for op, s in r4 if op in (" ", "+")]
    print("  a filter:", a_f, "==", ["1", "2"], ":", a_f == ["1", "2"])
    print("  b filter:", b_f, "==", ["3", "4"], ":", b_f == ["3", "4"])

    # Test 5: + sonra - yasaklaması
    r5 = satir_farki(["A", "P", "B"], ["A", "Q", "B"])
    print("Test 5 (interleaved):", r5)
    has_forbidden = any(r5[i][0] == "+" and r5[i+1][0] == "-" for i in range(len(r5)-1))
    print("  Yasakli pattern (+ sonra -):", has_forbidden)

    # Test 6: Büyük veri performansı
    import time, random
    n = 1000
    a6 = [str(i) for i in range(n)]
    b6 = [str(i) for i in range(0, n, 2)] + [str(i) for i in range(n-1, -1, -2)]
    start = time.time()
    r6 = satir_farki(a6, b6)
    elapsed = time.time() - start
    print(f"Test 6 (size {n}): {elapsed:.3f}s, result len={len(r6)}")
    a_f6 = [s for op, s in r6 if op in (" ", "-")]
    b_f6 = [s for op, s in r6 if op in (" ", "+")]
    print("  a filter match:", a_f6 == a6)
    print("  b filter match:", b_f6 == b6)
