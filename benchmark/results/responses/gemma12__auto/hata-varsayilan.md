# hata-varsayilan · puan 1.00

**Not:** 3/3 test

## Prompt

Aşağıdaki Python kodunda hata var. add_tag('a') ve ardından add_tag('b') çağrılınca ikinci çağrı ['b'] döndürmeli, ama ['a', 'b'] döndürüyor.
Hatayı düzelt ve kodun düzeltilmiş tam halini ver. Sadece Python kodunu tek bir ```python bloğu içinde ver.

```python
def add_tag(tag, tags=[]):
    """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
    tags.append(tag)
    return tags
```

## Cevap

Sorun Python'daki "mutable default argument" davranışından kaynaklanıyor: `[]` parametre tanıminde sadece fonksiyon ilk tanımlandığında bir kez oluşturulur ve her çağrıda aynı liste nesnesi kullanılır. İkinci çağırma, ilk eklenen 'a'yı koruduğu için beklenen sonucu vermez. Çözüm, varsayılan değeri `None` yapıp içeride yeni bir liste başlatmaktır.

```python
def add_tag(tag, tags=None):
    """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

## Notlandırılan kod/komut

```
def add_tag(tag, tags=None):
    """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```
