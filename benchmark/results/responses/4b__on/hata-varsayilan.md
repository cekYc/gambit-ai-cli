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

## Düşünme

Kullanıcı Python kodunda bir hata var. Sorun, değişken (tags) varsayılan değer olarak tanımlanmış ve değiştirilebilir (list). Her çağrıda aynı liste objesi kullanılıyor.

Sorunu çözmek için:
1. `None` yerine yeni listeler oluşturmalıyız
2. Varsayılan değeri `None` yapmalıyız, sonra `if tags is None` kontrolü ekleyip yeni liste oluşturalım

Düzeltmiş kodu vermem gerekiyor.


## Cevap

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
