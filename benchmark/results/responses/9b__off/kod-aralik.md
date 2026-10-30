# kod-aralik · puan 1.00

**Not:** 8/8 test

## Prompt

Python'da `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` fonksiyonunu yaz. Çakışan ya da
uç uca değen aralıkları birleştirsin ([1, 3] ve [3, 5] → [1, 5]). Girdi sıralı olmayabilir; sonuç başlangıç
değerine göre sıralı olsun. Girdi listesi (ve içindeki listeler) değiştirilmesin.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
from typing import List

def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    # Eğer liste boşse veya tek elemanlıysa, zaten birleştirilmiş demektir
    if not intervals or len(intervals) == 1:
        return intervals
    
    # Girdi değiştirilmesin diye derinlikli kopyasını alıyoruz (nested list olduğu için)
    sorted_intervals = [interval[:] for interval in sorted(intervals)]
    
    merged = []
    current_start, current_end = sorted_intervals[0]
    
    for next_interval in sorted_intervals[1:]:
        # Eğer bir sonraki aralık, mevcut aktif aralığın sonundan önce başlıyorsa (çakışma)
        if next_interval[0] <= current_end:
            # Aktif aralığı genişlet: yeni bitiş noktası max(current_end, next_interval[1]) olur
            current_end = max(current_end, next_interval[1])
        else:
            # Çakışma yoksa, mevcut aktif aralığı sonuca ekle ve yenisini başlat
            merged.append([current_start, current_end])
            current_start, current_end = next_interval
    
    # Son kalan aktif aralığı ekle
    merged.append([current_start, current_end])
    
    return merged
```

## Notlandırılan kod/komut

```
from typing import List

def merge_intervals(intervals: List[List[int]]) -> List[List[int]]:
    # Eğer liste boşse veya tek elemanlıysa, zaten birleştirilmiş demektir
    if not intervals or len(intervals) == 1:
        return intervals
    
    # Girdi değiştirilmesin diye derinlikli kopyasını alıyoruz (nested list olduğu için)
    sorted_intervals = [interval[:] for interval in sorted(intervals)]
    
    merged = []
    current_start, current_end = sorted_intervals[0]
    
    for next_interval in sorted_intervals[1:]:
        # Eğer bir sonraki aralık, mevcut aktif aralığın sonundan önce başlıyorsa (çakışma)
        if next_interval[0] <= current_end:
            # Aktif aralığı genişlet: yeni bitiş noktası max(current_end, next_interval[1]) olur
            current_end = max(current_end, next_interval[1])
        else:
            # Çakışma yoksa, mevcut aktif aralığı sonuca ekle ve yenisini başlat
            merged.append([current_start, current_end])
            current_start, current_end = next_interval
    
    # Son kalan aktif aralığı ekle
    merged.append([current_start, current_end])
    
    return merged
```
