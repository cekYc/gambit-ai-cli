"""
Minimal düzenleme dizisi (diff) hesaplayıcı — Myers O(ND) algoritması.
"""
from __future__ import annotations


def _myers_shortest_edit_script(a: list[str], b: list[str]) -> list[tuple[int, int, int]]:
    """
    Myers O(ND) algoritması ile en kısa düzenleme betiğini bulur.
    Dönüş: (i, j, op) listesi
      op =  0  -> eşleşme (a[i] == b[j]), her iki tarafta da ilerle
      op = -1  -> silme (a'dan), sadece i ilerler
      op = +1  -> ekleme (b'ye), sadece j ilerler
    """
    n, m = len(a), len(b)
    max_d = n + m
    # V[k] = en ileri ulaşılan i indeksi (k = i - j)
    # k aralığı: [-max_d, max_d], offset = max_d
    offset = max_d + 1
    v = [-1] * (2 * offset + 1)
    v[offset + 1] = 0  # k=1 için başlangıç (sanal)
    trace = []  # her D için V kopyası

    for d in range(max_d + 1):
        # V dizisini bu D için kaydet (geriye doğru izlemek için)
        trace.append(v.copy())
        for k in range(-d, d + 1, 2):
            # k = i - j
            # Aşağıdan mı (silme), yoksa soldan mı (ekleme) geliyor?
            if k == -d or (k != d and v[offset + k - 1] < v[offset + k + 1]):
                i = v[offset + k + 1]  # ekleme: j artar, i aynı
            else:
                i = v[offset + k - 1] + 1  # silme: i artar
            j = i - k
            # Eşleşen öneki atla (snake)
            while i < n and j < m and a[i] == b[j]:
                i += 1
                j += 1
            v[offset + k] = i
            if i >= n and j >= m:
                # Bitti, geriye doğru izle (backtrack)
                return _backtrack(trace, a, b, n, m, d, k, offset)
    return []  # asla buraya gelmez


def _backtrack(
    trace: list[list[int]],
    a: list[str],
    b: list[str],
    n: int,
    m: int,
    d: int,
    k: int,
    offset: int
) -> list[tuple[int, int, int]]:
    """Trace dizisinden geriye doğru yolunu kurar."""
    path = []
    i, j = n, m
    for d_cur in range(d, -1, -1):
        v = trace[d_cur]
        k_prev = k
        # Hangi k'dan geldik?
        if k == -d_cur or (k != d_cur and v[offset + k - 1] < v[offset + k + 1]):
            k_prev = k + 1  # ekleme yapmıştık
        else:
            k_prev = k - 1  # silme yapmıştık
        i_prev = v[offset + k_prev]
        j_prev = i_prev - k_prev
        # Snake (eşleşen kısım) varsa tersine ekle
        while i > i_prev and j > j_prev:
            path.append((i - 1, j - 1, 0))  # eşleşme
            i -= 1
            j -= 1
        # Değişiklik varsa ekle
        if d_cur > 0:
            if k_prev == k + 1:
                # ekleme (+)
                path.append((i, j - 1, 1))
                j -= 1
            else:
                # silme (-)
                path.append((i - 1, j, -1))
                i -= 1
        k = k_prev
    path.reverse()
    return path


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    a satır listesini b'ye çeviren minimal düzenleme dizisini döndürür.
    Her eleman: (" ", satır) ortak, ("-", satır) silinen, ("+", satır) eklenen.
    - " " ve "-" sırayla a'yı, " " ve "+" sırayla b'yi verir.
    - Ortak satır sayısı maksimum (LCS).
    - Ardışık değişikliklerde silmeler eklemelerden önce gelir.
    """
    if not a and not b:
        return []
    if not a:
        return [("+", line) for line in b]
    if not b:
        return [("-", line) for line in a]

    # Myers ile en kısa betiği bul
    ops = _myers_shortest_edit_script(a, b)

    # Çıktı formatına dönüştür + "silmeler önce" kuralı uygula
    # ops: (i, j, op)  op: 0=eşleşme, -1=silme, +1=ekleme
    # Ardışık değişiklik bloklarını topla, içinde silmeleri öne al
    result: list[tuple[str, str]] = []
    i = 0
    while i < len(ops):
        op_type = ops[i][2]
        if op_type == 0:
            # Eşleşme
            _, j, _ = ops[i]
            result.append((" ", b[j]))
            i += 1
        else:
            # Değişiklik bloğu topla
            block_start = i
            while i < len(ops) and ops[i][2] != 0:
                i += 1
            block = ops[block_start:i]
            # Bloğu işle: önce silmeler (-), sonra eklemeler (+)
            # Not: block içindeki sıralama zaten a/b indekslerine göre doğrudur.
            # Sadece çıkış sırasını değiştiriyoruz.
            deletions = [(idx_a, idx_b) for idx_a, idx_b, op in block if op == -1]
            additions = [(idx_a, idx_b) for idx_a, idx_b, op in block if op == 1]
            for idx_a, _ in deletions:
                result.append(("-", a[idx_a]))
            for _, idx_b in additions:
                result.append(("+", b[idx_b]))
    return result


# --- Basit kendi testleri (çalıştırmak için: python fark.py) ---
if __name__ == "__main__":
    # Test 1: Basit ekleme/silme
    a = ["satir1", "satir2", "satir3"]
    b = ["satir1", "yeni", "satir2", "satir3"]
    print("Test 1:", satir_farki(a, b))
    # Beklenen: [(' ', 'satir1'), ('+', 'yeni'), (' ', 'satir2'), (' ', 'satir3')]

    # Test 2: Silme sonra ekleme (ardışık değişiklik -> silmeler önce)
    a = ["a", "b", "c"]
    b = ["a", "x", "c"]
    print("Test 2:", satir_farki(a, b))
    # Beklenen: [(' ', 'a'), ('-', 'b'), ('+', 'x'), (' ', 'c')]

    # Test 3: Çoklu silme/ekleme
    a = ["1", "2", "3", "4"]
    b = ["1", "5", "6", "4"]
    print("Test 3:", satir_farki(a, b))
    # Beklenen: [(' ', '1'), ('-', '2'), ('-', '3'), ('+', '5'), ('+', '6'), (' ', '4')]

    # Test 4: Boş liste
    print("Test 4:", satir_farki([], ["a", "b"]))
    print("Test 5:", satir_farki(["a", "b"], []))

    # Test 5: Performans - 5000 satır, 10 değişiklik
    import random
    random.seed(42)
    base = [f"line_{i}" for i in range(5000)]
    a = base.copy()
    b = base.copy()
    for _ in range(10):
        idx = random.randint(0, 4999)
        b[idx] = f"changed_{idx}"
    import time
    t0 = time.time()
    diff = satir_farki(a, b)
    t1 = time.time()
    print(f"Performans: {len(a)} satır, {t1-t0:.4f} saniye, diff uzunluğu: {len(diff)}")
    # Değişiklik sayısı kontrolü
    changes = sum(1 for op, _ in diff if op != " ")
    print(f"Değişiklik sayısı: {changes} (beklenen ~20: 10 silme + 10 ekleme)")