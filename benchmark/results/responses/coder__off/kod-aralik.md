# kod-aralik · puan 0.88

**Not:** 7/8 test; başarısız: not_mutated()

## Prompt

Python'da `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` fonksiyonunu yaz. Çakışan ya da
uç uca değen aralıkları birleştirsin ([1, 3] ve [3, 5] → [1, 5]). Girdi sıralı olmayabilir; sonuç başlangıç
değerine göre sıralı olsun. Girdi listesi (ve içindeki listeler) değiştirilmesin.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

Python'da `merge_intervals` fonksiyonu için aşağıdaki kodu yazabilirsiniz:

```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    merged = []
    intervals.sort()  # Girdi listesini başlangıç değeri göre sıralayın

    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)  # Eşleşmeyen aralıkları birleştirin
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])  # Çakışan aralıkları birleştirin

    return merged
```

Buun kod, girdi listesini `[start, end]` şeklinde sıralar ve birleştirirken `start` değerine göre sıralı sonuç elde eder. Her iki aralık da başlangıç değerine göre karşılaştırılır, eğer birleşik değilse yeni bir aralık eklenir; eğer çakışan aralıkları varsa son bir aralanın `end` değeri güncellenir. Buun gibi bir yaklaşım kullanarak çakışan veya uç uca aralıklar birleştirilebilir.

## Notlandırılan kod/komut

```
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    merged = []
    intervals.sort()  # Girdi listesini başlangıç değeri göre sıralayın

    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)  # Eşleşmeyen aralıkları birleştirin
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])  # Çakışan aralıkları birleştirin

    return merged
```
