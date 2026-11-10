from typing import List, Tuple


def satir_farki(a: List[str], b: List[str]) -> List[Tuple[str, str]]:
    """
    a satır listesini b'ye çeviren minimal düzenleme dizisini döndürür.
    
    Her eleman:
    - (" ", satır): İki tarafta ortak
    - ("-", satır): a'dan silinen
    - ("+", satır): b'ye eklenen
    
    Özellikler:
    - " " ve "-" olanlar sırayla a'yı, " " ve "+" olanlar sırayla b'yi verir.
    - Ortak (" ") satır sayısı maksimumdur (LCS).
    - Ardışık değişikliklerde silmeler eklemelerden önce gelir.
    - Büyük listelerde hızlı çalışır.
    """
    n, m = len(a), len(b)
    
    # LCS uzunluklarını hesapla (DP tablosu)
    # Sadece 2 satır tutarak bellek optimize et
    prev = [0] * (m + 1)
    curr = [0] * (m + 1)
    
    # Tam DP tablosu için path reconstruction - küçük listelerde OK
    # Büyük listelerde bellek sorunu olabilir, o yüzden Hirschberg benzeri yaklaşım
    if n * m <= 10_000_000:  # 10M hücre ~ 80MB, güvenli
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            ai = a[i - 1]
            dpi = dp[i]
            dpim1 = dp[i - 1]
            for j in range(1, m + 1):
                if ai == b[j - 1]:
                    dpi[j] = dpim1[j - 1] + 1
                else:
                    dpi[j] = dpi[j - 1] if dpi[j - 1] > dpim1[j] else dpim1[j]
        
        # Geri izleme
        result = []
        i, j = n, m
        while i > 0 or j > 0:
            if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
                # Eşleşme
                i -= 1
                j -= 1
                result.append((" ", a[i]))
            elif j > 0 and (i == 0 or dp[i][j - 1] >= dp[i - 1][j]):
                # Ekleme
                j -= 1
                result.append(("+", b[j]))
            else:
                # Silme
                i -= 1
                result.append(("-", a[i]))
        
        result.reverse()
        return _reorder_changes(result)
    
    # Büyük listeler için Hirschberg (divide & conquer)
    return _hirschberg(a, b, 0, n, 0, m)


def _hirschberg(a: List[str], b: List[str], a_lo: int, a_hi: int, b_lo: int, b_hi: int) -> List[Tuple[str, str]]:
    """Hirschberg algoritması: O(nm) zaman, O(min(n,m)) bellek."""
    n = a_hi - a_lo
    m = b_hi - b_lo
    
    if n == 0:
        return [("+", b[b_lo + j]) for j in range(m)]
    if m == 0:
        return [("-", a[a_lo + i]) for i in range(n)]
    if n == 1:
        # a'da 1 eleman var, b'de ara
        item = a[a_lo]
        for j in range(m):
            if item == b[b_lo + j]:
                # Bulundu, öncesi ekleme, eleman ortak, sonrası ekleme
                res = []
                for k in range(j):
                    res.append(("+", b[b_lo + k]))
                res.append((" ", item))
                for k in range(j + 1, m):
                    res.append(("+", b[b_lo + k]))
                return _reorder_changes(res)
        # Bulunamadı, sil ve hepsini ekle
        return _reorder_changes([("-", item)] + [("+", b[b_lo + j]) for j in range(m)])
    if m == 1:
        # b'de 1 eleman var, a'da ara
        item = b[b_lo]
        for i in range(n):
            if a[a_lo + i] == item:
                res = []
                for k in range(i):
                    res.append(("-", a[a_lo + k]))
                res.append((" ", item))
                for k in range(i + 1, n):
                    res.append(("-", a[a_lo + k]))
                return _reorder_changes(res)
        return _reorder_changes([("+", item)] + [("-", a[a_lo + i]) for i in range(n)])
    
    # a'yı ikiye böl
    a_mid = a_lo + n // 2
    
    # Forward LCS scores
    def lcs_scores(a_start, a_end, b_start, b_end, reverse=False):
        n1 = a_end - a_start
        m1 = b_end - b_start
        prev = [0] * (m1 + 1)
        curr = [0] * (m1 + 1)
        
        a_indices = range(a_start, a_end) if not reverse else range(a_end - 1, a_start - 1, -1)
        b_indices = range(b_start, b_end) if not reverse else range(b_end - 1, b_start - 1, -1)
        
        for ai in a_indices:
            curr[0] = 0
            for idx_b, bj in enumerate(b_indices, 1):
                if a[ai] == b[bj]:
                    curr[idx_b] = prev[idx_b - 1] + 1
                else:
                    curr[idx_b] = curr[idx_b - 1] if curr[idx_b - 1] > prev[idx_b] else prev[idx_b]
            prev, curr = curr, prev
        return prev
    
    # Forward
    fwd = lcs_scores(a_lo, a_mid, b_lo, b_hi)
    # Reverse
    rev = lcs_scores(a_mid, a_hi, b_lo, b_hi, reverse=True)
    
    # En iyi bölme noktasını bul
    max_val = -1
    best_j = 0
    for j in range(m + 1):
        val = fwd[j] + rev[m - j]
        if val > max_val:
            max_val = val
            best_j = j
    
    b_mid = b_lo + best_j
    
    # Özyinelemeli çağrılar
    left = _hirschberg(a, b, a_lo, a_mid, b_lo, b_mid)
    right = _hirschberg(a, b, a_mid, a_hi, b_mid, b_hi)
    
    return _reorder_changes(left + right)


def _reorder_changes(ops: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Ardışık değişiklik bloklarında silmeleri eklemelerden önce yerleştirir."""
    if not ops:
        return ops
    
    result = []
    i = 0
    
    while i < len(ops):
        op, line = ops[i]
        
        if op == " ":
            result.append((op, line))
            i += 1
        else:
            # Değişiklik bloğunu topla
            block = []
            while i < len(ops) and ops[i][0] != " ":
                block.append(ops[i])
                i += 1
            
            # Bloğu yeniden sırala: önce silmeler (-), sonra eklemeler (+)
            deletions = [(op, line) for op, line in block if op == "-"]
            additions = [(op, line) for op, line in block if op == "+"]
            
            result.extend(deletions)
            result.extend(additions)
    
    return result


if __name__ == "__main__":
    # Basit testler
    test_cases = [
        # Temel test
        (
            ["a", "b", "c"],
            ["a", "b", "c"],
            [(" ", "a"), (" ", "b"), (" ", "c")]
        ),
        # Sona ekleme
        (
            ["a", "b"],
            ["a", "b", "c"],
            [(" ", "a"), (" ", "b"), ("+", "c")]
        ),
        # Baştan ekleme
        (
            ["b", "c"],
            ["a", "b", "c"],
            [("+", "a"), (" ", "b"), (" ", "c")]
        ),
        # Silme
        (
            ["a", "b", "c"],
            ["a", "c"],
            [(" ", "a"), ("-", "b"), (" ", "c")]
        ),
        # Değiştirme (silme + ekleme)
        (
            ["a", "b", "c"],
            ["a", "x", "c"],
            [(" ", "a"), ("-", "b"), ("+", "x"), (" ", "c")]
        ),
        # Silme ekleme sırası testi
        (
            ["a", "b"],
            ["x", "y"],
            [("-", "a"), ("-", "b"), ("+", "x"), ("+", "y")]
        ),
        # Karmaşık durum
        (
            ["satır1", "satır2", "satır3", "satır4"],
            ["satır1", "yeni2", "satır3", "yeni4", "yeni5"],
            [(" ", "satır1"), ("-", "satır2"), ("+", "yeni2"), (" ", "satır3"), ("-", "satır4"), ("+", "yeni4"), ("+", "yeni5")]
        ),
        # Boş liste
        (
            [],
            ["a", "b"],
            [("+", "a"), ("+", "b")]
        ),
        (
            ["a", "b"],
            [],
            [("-", "a"), ("-", "b")]
        ),
    ]
    
    for i, (a, b, expected) in enumerate(test_cases):
        result = satir_farki(a, b)
        status = "✓" if result == expected else "✗"
        print(f"Test {i+1}: {status}")
        if result != expected:
            print(f"  a: {a}")
            print(f"  b: {b}")
            print(f"  Beklenen: {expected}")
            print(f"  Elde:     {result}")
    
    print("\nTüm testler tamamlandı.")
