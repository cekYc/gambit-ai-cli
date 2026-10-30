# kod-aralik · puan 1.00

**Not:** 8/8 test

## Prompt

Python'da `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` fonksiyonunu yaz. Çakışan ya da
uç uca değen aralıkları birleştirsin ([1, 3] ve [3, 5] → [1, 5]). Girdi sıralı olmayabilir; sonuç başlangıç
değerine göre sıralı olsun. Girdi listesi (ve içindeki listeler) değiştirilmesin.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []

    # Girdiyi değiştirmemek için sıralanmış bir kopya oluşturuyoruz
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = []
    for interval in sorted_intervals:
        # Eğer merged listesi boşsa veya mevcut aralık son öncekiyle çakışmıyorsa (uç uca değme dahil)
        if not merged or merged[-1][1] < interval[0]:
            merged.append(list(interval))
        else:
            # Çakışma varsa, birleşmiş olanın bitiş noktasını güncelle
            merged[-1][1] = max(merged[-1][1], interval[1])
            
    return merged
```

## Notlandırılan kod/komut

```
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []

    # Girdiyi değiştirmemek için sıralanmış bir kopya oluşturuyoruz
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = []
    for interval in sorted_intervals:
        # Eğer merged listesi boşsa veya mevcut aralık son öncekiyle çakışmıyorsa (uç uca değme dahil)
        if not merged or merged[-1][1] < interval[0]:
            merged.append(list(interval))
        else:
            # Çakışma varsa, birleşmiş olanın bitiş noktasını güncelle
            merged[-1][1] = max(merged[-1][1], interval[1])
            
    return merged
```
