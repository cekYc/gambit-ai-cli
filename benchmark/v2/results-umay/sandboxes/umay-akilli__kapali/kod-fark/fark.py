from __future__ import annotations

def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    a satır listesini b'ye çeviren minimal bir düzenleme dizisi döndürür (Myers O(ND) algoritması).
    
    Her eleman:
    - (" ", satır) : iki tarafta ortak
    - ("-", satır) : a'dan silinen
    - ("+", satır) : b'ye eklenen
    
    Kurallar:
    - " " ve "-" olanlar sırayla a'yı verir
    - " " ve "+" olanlar sırayla b'yi verir  
    - Ortak (" ") satır sayısı maksimum (LCS)
    - Ardışık değişikliklerde silmeler eklemelerden önce gelir
    """
    n, m = len(a), len(b)
    max_d = n + m
    
    offset = max_d + 1
    v = [0] * (2 * offset + 1)
    
    # trace[d] = v dizisinin kopyası o D seviyesinde
    trace = []
    
    def snake(x: int, y: int) -> tuple[int, int]:
        while x < n and y < m and a[x] == b[y]:
            x += 1
            y += 1
        return x, y
    
    # D = 0
    x, y = snake(0, 0)
    v[offset] = x
    trace.append(v[:])
    
    if x == n and y == m:
        return [(" ", line) for line in a]
    
    for d in range(1, max_d + 1):
        for k in range(-d, d + 1, 2):
            k_idx = offset + k
            
            if k == -d or (k != d and v[k_idx - 1] < v[k_idx + 1]):
                # Insertion: sağdan gel
                x = v[k_idx + 1]
                y = x - k - 1
            else:
                # Deletion: yukarıdan gel
                x = v[k_idx - 1] + 1
                y = x - k + 1
            
            x, y = snake(x, y)
            v[k_idx] = x
            
            if x == n and y == m:
                trace.append(v[:])
                return _build_result(a, b, trace, n, m, offset)
        trace.append(v[:])
    
    return _build_result(a, b, trace, n, m, offset)


def _build_result(a: list[str], b: list[str], trace: list, n: int, m: int, offset: int) -> list[tuple[str, str]]:
    ops_rev = []
    x, y = n, m
    
    for d in range(len(trace) - 1, 0, -1):
        v_d = trace[d]
        v_prev = trace[d - 1]
        k = x - y
        k_idx = offset + k
        
        x_end = v_d[k_idx]
        
        # Hangi k'dan geldik?
        # Deletion: k-1 diagonalinden, x = v_prev[k-1] + 1
        # Insertion: k+1 diagonalinden, x = v_prev[k+1]
        # Snake: k diagonalinden, x = v_prev[k]
        
        if k_idx - 1 >= 0 and v_d[k_idx] == v_prev[k_idx - 1] + 1:
            # Deletion: a'dan silme
            # Snake kısmı
            snake_len = x_end - (v_prev[k_idx - 1] + 1)
            for _ in range(snake_len):
                x -= 1
                y -= 1
                ops_rev.append((" ", a[x]))
            # Deletion
            x -= 1
            ops_rev.append(("-", a[x]))
        elif k_idx + 1 < len(v_d) and v_d[k_idx] == v_prev[k_idx + 1]:
            # Insertion: b'ye ekleme
            snake_len = x_end - v_prev[k_idx + 1]
            for _ in range(snake_len):
                x -= 1
                y -= 1
                ops_rev.append((" ", a[x]))
            y -= 1
            ops_rev.append(("+", b[y]))
        else:
            # Snake only
            snake_len = x_end - v_prev[k_idx]
            for _ in range(snake_len):
                x -= 1
                y -= 1
                ops_rev.append((" ", a[x]))
    
    # D = 0 snake
    v_0 = trace[0]
    snake_len = v_0[offset]
    for _ in range(snake_len):
        x -= 1
        y -= 1
        ops_rev.append((" ", a[x]))
    
    ops = ops_rev[::-1]
    
    # Kural: ardışık değişikliklerde silmeler eklemelerden önce gelsin
    result = []
    i = 0
    while i < len(ops):
        if ops[i][0] == "+":
            plus_block = []
            while i < len(ops) and ops[i][0] == "+":
                plus_block.append(ops[i])
                i += 1
            minus_block = []
            while i < len(ops) and ops[i][0] == "-":
                minus_block.append(ops[i])
                i += 1
            result.extend(minus_block)
            result.extend(plus_block)
        else:
            result.append(ops[i])
            i += 1
    
    return result


if __name__ == "__main__":
    a = ["satır1", "satır2", "satır3", "satır4"]
    b = ["satır1", "yeni2", "satır3", "yeni4", "satır5"]
    
    result = satir_farki(a, b)
    for op, line in result:
        print(f"{op} {line}")