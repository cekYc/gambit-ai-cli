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

*   Function: `binary_search(arr, target)`
    *   Goal: Find the index of `target` in a sorted list `arr`. Return `-1` if not found.
    *   Current implementation logic:
        *   `lo = 0`, `hi = len(arr) - 1`
        *   `while lo < hi:` (This is the potential issue)
        *   `mid = (lo + hi) // 2`
        *   If `arr[mid] == target`, return `mid`.
        *   If `arr[mid] < target`, `lo = mid + 1`.
        *   Else, `hi = mid - 1`.
    *   Example case: `binary_search([1, 3, 5], 5)`
        *   `lo = 0`, `hi = 2`
        *   Loop 1: `lo < hi` (0 < 2) is True.
            *   `mid = (0 + 2) // 2 = 1`.
            *   `arr[1]` is 3. `3 == 5` is False.
            *   `3 < 5` is True, so `lo = mid + 1 = 2`.
        *   Loop 2: `lo < hi` (2 < 2) is False.
        *   Return -1.

    *   The condition `while lo < hi:` terminates when `lo == hi`. In the example above, when `lo` becomes 2 and `hi` is 2, the loop exits before checking the element at index 2 (which is the target).
    *   Standard binary search uses `while lo <= hi:`.

    *   Change `while lo < hi:` to `while lo <= hi:`.

    *   `binary_search([1, 3, 5], 5)`
        *   `lo = 0`, `hi = 2`
        *   Loop 1: `0 <= 2` is True.
            *   `mid = (0 + 2) // 2 = 1`.
            *   `arr[1]` is 3. `3 < 5` -> `lo = 2`.
        *   Loop 2: `2 <= 2` is True.
            *   `mid = (2 + 2) // 2 = 2`.
            *   `arr[2]` is 5. `5 == 5` -> return 2. Correct.

    *   Provide only the corrected Python code in a single ```python block.

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
