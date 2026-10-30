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

## Cevap

Hata `range` fonksiyonundaki durdurma değerinden kaynaklanmaktadır (`len(items) - size`); bu durumda son elemanı içeren en son parça döngüye dahil edilemez. Durdurma değerini doğrudan `len(items)` yaparak tüm parçaların oluşturulması sağlanır ve Python'un dilimleme (slicing) özelliği doğal olarak son grubu daha kısa olsa bile doğru şekilde döndürür.

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
