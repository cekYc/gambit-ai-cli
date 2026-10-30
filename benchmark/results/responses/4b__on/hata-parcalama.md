# hata-parcalama · puan 1.00

**Not:** 6/6 test

## Prompt

Aşağıdaki Python kodunda hata var. Örneğin chunks([1, 2, 3, 4, 5], 2) [[1, 2], [3, 4], [5]] döndürmeli.
Hatayı düzelt ve kodun düzeltilmiş tam halini ver. Sadece Python kodunu tek bir ```python bloğu içinde ver.

```python
def chunks(items, size):
    """Listeyi size uzunluğunda parçalara böler; son parça daha kısa olabilir."""
    return [items[i:i + size] for i in range(0, len(items) - size, size)]
```

## Düşünme

Kullanıcı bir Python fonksiyonunda hata olduğunu söylüyor. `chunks` fonksiyonu listeyi belirli parçalara bölmeli ancak mevcut kodda bir sorun var.

Mevcut kod:
```python
def chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items) - size, size)]
```

Sorun: `range`'ın son parametresi yanlış hesaplanmış. `len(items) - size` kullanılmış ama bu doğru değil. Örneğin `[1, 2, 3, 4, 5]`, size=2 için:
- range(0, 3, 2) = [0, 2]
- items[0:2] = [1, 2] ✓
- items[2:4] = [3, 4] ✓  
- items[4:6] = [5] ✗ (bu parça eksik)

`range(0, len(items), size)` olmalı. Yani en son parçayı da dahil edelim.

Düzeltme: `len(items)` yerine `len(items)` kullanmak yeterli ama aslında bu zaten doğru. Sorun `len(items) - size`. Bu yanlış çünkü son elemanları atıyor.

Doğru çözüm:
```python
def chunks(items, size):
    return [items[i:i + size] for i in range(0, len(items), size)]
```

Bu şekilde:
- items[1,2,3,4,5], size=2 için:
  - i=0: items[0:2] = [1, 2] ✓
  - i=2: items[2:4] = [3, 4] ✓  
  - i=4: items[4:6] = [5] ✓

Şimdi düzeltilmiş kodu tek bir ```python bloğu içinde vereceğim.


## Cevap

```python
def chunks(items, size):
    """Listeyi size uzunluğunda parçalara böler; son parça daha kısa olabilir."""
    return [items[i:i + size] for i in range(0, len(items), size)]
```

## Notlandırılan kod/komut

```
def chunks(items, size):
    """Listeyi size uzunluğunda parçalara böler; son parça daha kısa olabilir."""
    return [items[i:i + size] for i in range(0, len(items), size)]
```
