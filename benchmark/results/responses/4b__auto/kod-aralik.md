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

    # Girdiyi başlangıç değerine göre sırala (girdi değişmez, bu yüzden yeni liste oluşturuyoruz)
    sorted_intervals = sorted(intervals, key=lambda x: x[0])

    merged = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        curr_start, curr_end = current

        # Çakışma var mı kontrol et (uç uca değen de çakışır: 3 <= last_end)
        if curr_start <= last_end:
            # Birleştir ve sonu en büyük değeri al
            merged[-1] = [last_start, max(last_end, curr_end)]
        else:
            # Çakışma yoksa yeni aralığı ekle
            merged.append(current)

    return merged
```

## Notlandırılan kod/komut

```
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    if not intervals:
        return []

    # Girdiyi başlangıç değerine göre sırala (girdi değişmez, bu yüzden yeni liste oluşturuyoruz)
    sorted_intervals = sorted(intervals, key=lambda x: x[0])

    merged = [sorted_intervals[0]]

    for current in sorted_intervals[1:]:
        last_start, last_end = merged[-1]
        curr_start, curr_end = current

        # Çakışma var mı kontrol et (uç uca değen de çakışır: 3 <= last_end)
        if curr_start <= last_end:
            # Birleştir ve sonu en büyük değeri al
            merged[-1] = [last_start, max(last_end, curr_end)]
        else:
            # Çakışma yoksa yeni aralığı ekle
            merged.append(current)

    return merged
```
