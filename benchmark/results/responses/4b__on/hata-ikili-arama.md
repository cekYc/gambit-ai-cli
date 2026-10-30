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

Kullanıcı binary_search fonksiyonunda bir hata olduğunu belirtiyor. [1, 3, 5] listesindeki hedef değer 5'in indeksini döndürmesi gerekiyor (2), ancak -1 döndürüyor.

İşte sorunun analizi:

```python
def binary_search(arr, target):
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

Sorun şu: `while` koşulu `lo < hi`, ancak binary search algoritmasında tipik olarak `while lo <= hi` olmalı. Ayrıca, last line'de `hi = mid` olması gerekir çünkü last iteration'ı kontrol edeceğimizde mid'i son değer olarak alabiliriz.

Aslında ana sorun şu: binary_search algoritmada while koşulu genellikle `lo < hi` değil de `lo <= hi` olmalı. Ancak bu durumda, son iterasyon sırasında lo ve hi aynı değere sahip olduğunda kontrol edilmeli.

Test etelim:
- arr = [1, 3, 5], target = 5
- lo = 0, hi = 2
- while 0 < 2: True
- mid = (0 + 2) // 2 = 1
- arr[1] = 3 < 5, so lo = 2

Şimdi: lo = 2, hi = 2
while 2 < 2: False - döngü biter!

Döngü bitince mid kontrol edilmez ve target bulunamaz. Bu yüzden `lo <= hi` olmalı veya son iterasyon sırasında `hi` değeri güncellenmeli.

Standard binary search'ta normalde:
```python
while lo < hi:
    mid = (lo + hi) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        lo = mid + 1
    else:
        hi = mid - 1


```

Ama bu durumda, son iterasyonda lo ve hi aynı değerdeyse, bu değer kontrol edilmeli. Bu yüzden `lo <= hi` olmalı veya döngü içindeki logic'i düzeltmeliyiz.

Daha iyisi:
```python
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

Bu şekilde çalışır. Bu kodda `while lo <= hi` olmalı çünkü last element'in kontrolü için bu şart gerekli.

Daha iyi bir düzeltme yapalım. 

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

Bu düzeltme ile [1, 3, 5], 5 için:
- lo=0, hi=2, mid=1, arr[1]=3 < 5 → lo=2
- lo=2, hi=2, mid=2, arr[2]=5 == 5 → return 2 ✅

Düzeltilmiş kodu tek bir ```python bloğu içinde vereceğim.


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
