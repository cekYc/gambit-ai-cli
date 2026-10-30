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

## Düşünme

The user is asking me to fix a bug in the binary_search function. Let me analyze the code:

The issue is in the while loop condition and the logic. The current code has several problems:

1. `while lo < hi:` should be `while lo <= hi:` - This is because when lo == hi, we still need to check that element
2. When `arr[mid] > target`, setting `hi = mid - 1` skips checking the middle element itself if it could be equal (though this case is handled in the first if)

Actually, looking more carefully:
- The main issue is `while lo < hi:` should be `while lo <= hi:` 
- When lo == hi, we still need to check that single remaining element

Let me trace through an example with `[1, 3, 5]` and target `5`:
- Initial: lo=0, hi=2
- Iteration 1: mid = (0+2)//2 = 1, arr[1]=3 < 5, so lo = 2
- Now lo=2, hi=2, but the loop condition is `lo < hi` which is False (2 < 2 is False)
- So it exits and returns -1

But we should check arr[2] which is 5! That's why we need `while lo <= hi:`

Let me fix this:

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

This should fix the issue. The only change needed is `while lo < hi:` to `while lo <= hi:`.


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
