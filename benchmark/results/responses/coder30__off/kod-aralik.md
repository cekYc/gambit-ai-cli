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
    
    # Girdiyi başlangıç değerine göre sırala
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        
        # Eğer aralıklar çakışıyor ya da uç uca değiyorlarsa birleştir
        if last[1] >= current[0]:
            merged[-1] = [last[0], max(last[1], current[1])]
        else:
            merged.append(current)
    
    return merged
```

## Notlandırılan kod/komut

```
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    
    # Girdiyi başlangıç değerine göre sırala
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = [sorted_intervals[0]]
    
    for current in sorted_intervals[1:]:
        last = merged[-1]
        
        # Eğer aralıklar çakışıyor ya da uç uca değiyorlarsa birleştir
        if last[1] >= current[0]:
            merged[-1] = [last[0], max(last[1], current[1])]
        else:
            merged.append(current)
    
    return merged
```
