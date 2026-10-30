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
