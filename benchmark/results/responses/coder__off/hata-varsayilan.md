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

Python kodunda hata olan yer `tags` parametresinin değeri değiştirildiği için ikinci çağırdan sonra ilgili listeyi kaybetmiş oluyor. Buşukluğu düzeltmek için, `tags` parametresini bir `if` koşuluyla güncellemeliyiz. Buşukluğunu düzeltmenin yöntemi şu şekildedir:

```python
def add_tag(tag, tags=None):
    """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

Buşukluğunu düzelttiğinde, ikinci çağrının `['b']` olarak dönen yerine `['a', 'b']` olacaktır. Buşukluğunun açıklaması şudur:
1. Fonksiyon içinde `tags=None` ile parametre tanımladım.
2. Fonksiyon kullanıldığında `tags` parametresi belirtilmezse (yani `None` değerini alır), buşukluğun içine bir boş liste atıyorum (`tags = []`).
3. Buşukluğunu düzelttiğinden, ikinci çağrı da belirli bir liste kullanabilir ve istenen listeyi döndürebilir.

Buşukluğu düzeltmenin sonucu şudur:
```python
def add_tag(tag, tags=None):
    """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

# Kullanım örneği
print(add_tag('a'))  # ['a']
print(add_tag('b', ['a']))  # ['a', 'b']
```

Buşukluğunu düzelttiğinden kodunuz artık beklenen şekilde çalışır. ikinci çağrının `['b']` olarak döndürmesini sağlar.

## Notlandırılan kod/komut

```
def add_tag(tag, tags=None):
    """tag'i verilen listeye ekler ve aynı listeyi döndürür; liste verilmezse yeni bir liste kullanır."""
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

# Kullanım örneği
print(add_tag('a'))  # ['a']
print(add_tag('b', ['a']))  # ['a', 'b']
```
