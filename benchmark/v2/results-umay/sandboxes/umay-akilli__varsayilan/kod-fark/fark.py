from __future__ import annotations


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """
    a satır listesini b'ye çeviren minimal düzenleme dizisini döndürür.
    
    Her eleman:
    - (" ", satır) : iki tarafta ortak
    - ("-", satır) : a'dan silinen
    - ("+", satır) : b'ye eklenen
    
    Kurallar:
    - " " ve "-" olanlar sırayla a'yı, " " ve "+" olanlar sırayla b'yi verir
    - Ortak (" ") satır sayısı maksimum (LCS)
    - Ardışık değişikliklerde silmeler eklemelerden önce gelir
    - Myers O(ND) algoritması ile birkaç bin satırda hızlı çalışır
    """
    n, m = len(a), len(b)
    max_d = n + m
    
    # V[k] = x koordinatı (a'daki indeks) en uzak ulaşıldığında
    # k = x - y (diagonal)
    v = {1: 0}
    trace = []
    
    for d in range(max_d + 1):
        trace.append(v.copy())
        for k in range(-d, d + 1, 2):
            # Aşağı mı geliyor (silme), sağa mı gidiyor (ekleme)?
            if k == -d or (k != d and v.get(k - 1, -1) < v.get(k + 1, -1)):
                x = v[k + 1]  # sağdan gel (ekleme)
            else:
                x = v[k - 1] + 1  # aşağıdan gel (silme)
            
            y = x - k
            
            # Eşleşenleri atla (diagonal hareket)
            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1
            
            v[k] = x
            
            if x >= n and y >= m:
                # Bulundu, yolu yeniden inşa et
                return _yolu_olustur(a, b, trace, n, m)
    
    # Buraya asla gelmemeli ama güvenlik için
    return _yolu_olustur(a, b, trace, n, m)


def _yolu_olustur(a: list[str], b: list[str], trace: list[dict[int, int]], n: int, m: int) -> list[tuple[str, str]]:
    """Trace'ten düzenleme dizisini geriye doğrü inşa eder."""
    x, y = n, m
    sonuc = []
    
    for d in range(len(trace) - 1, -1, -1):
        v = trace[d]
        k = x - y
        
        if d == 0:
            prev_x, prev_y = 0, 0
        else:
            prev_v = trace[d - 1]
            
            # Hangi k'dan geldik? Myers algoritmasının tersini uygula
            # k = x - y, önceki adımda ya k-1 (silme) ya da k+1 (ekleme) idi
            # Hangisi geçerli ve hangisi daha büyük x veriyorsa oradan gelmişizdir
            # Önce her iki olasılığı da kontrol et
            k_minus = k - 1  # silme (dikey) hareketi
            k_plus = k + 1   # ekleme (yatay) hareketi
            
            x_minus = prev_v.get(k_minus, -1)
            x_plus = prev_v.get(k_plus, -1)
            
            # Geçerli olanı seç: k_minus için x_minus + 1 == x olmalı (silme)
            # k_plus için x_plus == x olmalı (ekleme)
            # Myers forward'da: k == -d -> k+1, k == d -> k-1, diğer -> max(v[k-1]+1, v[k+1])
            # Backward'da: hangi prev_k x değerini üretir?
            
            # Silme (dikey) hareketi: prev_x = x - 1, prev_k = k - 1
            # Ekleme (yatay) hareketi: prev_x = x, prev_k = k + 1
            
            if x_minus + 1 == x and x_plus == x:
                # Her ikisi de mümkün, Myers forward'da max(v[k-1]+1, v[k+1]) seçer
                # Yani daha büyük x vereni seçer
                if x_minus + 1 >= x_plus:
                    prev_k = k_minus
                    prev_x = x_minus
                else:
                    prev_k = k_plus
                    prev_x = x_plus
            elif x_minus + 1 == x:
                prev_k = k_minus
                prev_x = x_minus
            elif x_plus == x:
                prev_k = k_plus
                prev_x = x_plus
            else:
                # Fallback: Myers forward mantığına göre
                if k == -d or (k != d and x_minus < x_plus):
                    prev_k = k_plus
                    prev_x = x_plus
                else:
                    prev_k = k_minus
                    prev_x = x_minus
            
            prev_y = prev_x - prev_k
        
        # Diagonal hareket (eşleşenler) - geriye doğrü
        while x > prev_x and y > prev_y:
            sonuc.append((" ", a[x - 1]))
            x -= 1
            y -= 1
        
        # Dikey hareket (silme) - geriye doğrü
        if x > prev_x:
            sonuc.append(("-", a[x - 1]))
            x -= 1
        # Yatay hareket (ekleme) - geriye doğrü
        elif y > prev_y:
            sonuc.append(("+", b[y - 1]))
            y -= 1
    
    sonuc.reverse()
    
    # Silmeleri eklemelerden önce getir (ardışık değişikliklerde)
    return _silmeleri_oncele(sonuc)


def _silmeleri_oncele(ops: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Ardışık değişiklik bloklarında silmeleri eklemelerden önce sıralar."""
    if not ops:
        return ops
    
    sonuc = []
    i = 0
    
    while i < len(ops):
        op, line = ops[i]
        
        if op == " ":
            sonuc.append((op, line))
            i += 1
        else:
            # Değişiklik bloğunu topla
            blok = []
            while i < len(ops) and ops[i][0] != " ":
                blok.append(ops[i])
                i += 1
            
            # Bloğu sırala: önce silmeler (-), sonra eklemeler (+)
            silinen = [(op, line) for op, line in blok if op == "-"]
            eklenen = [(op, line) for op, line in blok if op == "+"]
            sonuc.extend(silinen)
            sonuc.extend(eklenen)
    
    return sonuc


if __name__ == "__main__":
    # Hızlı testler
    a = ["satir1", "satir2", "satir3", "satir4"]
    b = ["satir1", "yeni2", "satir3", "yeni4", "satir5"]
    
    sonuc = satir_farki(a, b)
    for op, line in sonuc:
        print(f"{op} {line}")
    
    print("---")
    
    # Doğrulama
    a_reconstructed = [line for op, line in sonuc if op in (" ", "-")]
    b_reconstructed = [line for op, line in sonuc if op in (" ", "+")]
    print(f"a eşleşiyor: {a_reconstructed == a}")
    print(f"b eşleşiyor: {b_reconstructed == b}")