# hata-ikili-arama · puan 1.00

**Not:** 9/9 test

## Prompt

Aşağıdaki Python kodunda hata var. Örneğin binary_search([1, 3, 5], 5) 2 döndürmesi gerekirken -1 döndürüyor.
Hatayı düzelt ve kodun düzeltilmiş tam halini ver. Sadece Python kodunu tek bir ```python bloğu içinde ver.

```python
def binary_search(arr, target):
    """Sıralı listede target'ın indeksini, yoksa -1 döndürür."""
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Cevap

```python
def binary_search(arr, target):
    """Sıralı listede target'ın indeksini, yoksa -1 döndürür."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```

## Notlandırılan kod/komut

```
def binary_search(arr, target):
    """Sıralı listede target'ın indeksini, yoksa -1 döndürür."""
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
```
