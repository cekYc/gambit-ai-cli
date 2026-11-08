from __future__ import annotations


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    a listesini b'ye çeviren minimal düzenleme dizisini döndürür.
    Her eleman: (" ", satır) ortak, ("-", satır) silinen, ("+", satır) eklenen.
    - " " ve "-" sırayla a'yı, " " ve "+" sırayla b'yi verir.
    - Ortak satır sayısı en fazla (LCS).
    - Silmeler eklemelerden önce gelir ("+" hemen ardından "-" gelmez).
    """
    n, m = len(a), len(b)
    max_d = n + m

    # v[k] = x koordinatı (a'daki indeks) en uzak ulaşılan nokta
    # k = x - y  (diagonal indeksi)
    v = {1: 0}
    trace = []  # her d için v kopyası

    for d in range(max_d + 1):
        trace.append(v.copy())
        for k in range(-d, d + 1, 2):
            # aşağı (silme) mi sağa (ekleme) mi?
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v[k + 1]  # sağdan gel (ekleme)
            else:
                x = v[k - 1] + 1  # aşağıdan gel (silme)
            y = x - k

            # kopyalanan (eşleşen) kısmı atla
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            v[k] = x

            if x >= n and y >= m:
                # Bitti, yolu yeniden kur
                return _yolu_kuvur(trace, a, b, n, m)

    return []  # asla buraya gelmez


def _yolu_kuvur(trace: list[dict[int, int]], a: list[str], b: list[str],
                 n: int, m: int) -> list[tuple[str, str]]:
    """Trace'tan geriye doğru yol kurar, sonra düzeltip sonucu üretir."""
    x, y = n, m
    path = []  # (op, idx_a, idx_b) geriye doğru

    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y

        # Hangi koldan geldik?
        if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
            prev_k = k + 1  # sağdan (ekleme)
        else:
            prev_k = k - 1  # aşağıdan (silme)

        prev_x = v[prev_k]
        prev_y = prev_x - prev_k

        # Eşleşen kısmı geri al
        while x > prev_x and y > prev_y:
            x -= 1
            y -= 1
            path.append((' ', x, y))  # a[x] == b[y]

        # Silme veya ekleme
        if d > 0:
            if prev_k == k + 1:  # ekleme (+): (prev_x, prev_y) -> (x, y) = (prev_x, prev_y+1)
                # eklenen eleman b[prev_y]
                path.append(('+', prev_x, prev_y))
                y -= 1
            else:  # silme (-): (prev_x, prev_y) -> (x, y) = (prev_x+1, prev_y)
                # silinen eleman a[prev_x]
                path.append(('-', prev_x, prev_y))
                x -= 1
        else:
            # d=0 başlangıç
            while x > 0 or y > 0:
                if x > 0 and y > 0:
                    x -= 1
                    y -= 1
                    path.append((' ', x, y))
                elif x > 0:
                    x -= 1
                    path.append(('-', x, y))
                else:
                    y -= 1
                    path.append(('+', x, y))
        x, y = prev_x, prev_y

    # path ters sırada, düzelt
    path.reverse()

    # Sonuç listesi oluştur
    result = []
    for op, ia, ib in path:
        if op == ' ':
            result.append((" ", a[ia]))
        elif op == '-':
            result.append(("-", a[ia]))
        else:  # '+'
            result.append(("+", b[ib]))

    # Kural: "+" hemen ardından "-" gelmesin (silmeler önce)
    # Ardışık +- çiftlerini -+ yap
    i = 0
    while i < len(result) - 1:
        if result[i][0] == '+' and result[i + 1][0] == '-':
            result[i], result[i + 1] = result[i + 1], result[i]
            i += 1  # atla
        i += 1

    return result


if __name__ == "__main__":
    # Basit testler
    a = ["satır1", "satır2", "satır3", "satır4"]
    b = ["satır1", "yeni2", "satır3", "yeni4", "satır5"]
    
    print("A:", a)
    print("B:", b)
    print("Diff:")
    for op, line in satir_farki(a, b):
        print(f"  {op} {line}")
    
    # Doğrulama
    recon_a = [l for op, l in satir_farki(a, b) if op in (" ", "-")]
    recon_b = [l for op, l in satir_farki(a, b) if op in (" ", "+")]
    print("\nReconstructed A:", recon_a)
    print("Reconstructed B:", recon_b)
    print("A match:", recon_a == a)
    print("B match:", recon_b == b)