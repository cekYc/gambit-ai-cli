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
    
    # Sıralama için kopya al (girdi değiştirilmesin)
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = [list(sorted_intervals[0])]
    
    for i in range(1, len(sorted_intervals)):
        current_start, current_end = sorted_intervals[i]
        last_merged_start, last_merged_end = merged[-1]
        
        # Çakışan veya uç uca değen aralık mı?
        if current_start <= last_merged_end:
            # Birleştir: sonu genişlet
            merged[-1][1] = max(last_merged_end, current_end)
        else:
            # Yeni aralık ekle (kopyala)
            merged.append([current_start, current_end])
    
    return merged
```

## Notlandırılan kod/komut

```
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []
    
    # Sıralama için kopya al (girdi değiştirilmesin)
    sorted_intervals = sorted(intervals, key=lambda x: x[0])
    
    merged = [list(sorted_intervals[0])]
    
    for i in range(1, len(sorted_intervals)):
        current_start, current_end = sorted_intervals[i]
        last_merged_start, last_merged_end = merged[-1]
        
        # Çakışan veya uç uca değen aralık mı?
        if current_start <= last_merged_end:
            # Birleştir: sonu genişlet
            merged[-1][1] = max(last_merged_end, current_end)
        else:
            # Yeni aralık ekle (kopyala)
            merged.append([current_start, current_end])
    
    return merged
```
