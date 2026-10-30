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

*   Function: `add_tag(tag, tags=[])`
    *   Behavior observed: Calling `add_tag('a')` then `add_tag('b')` results in `['a', 'b']`.
    *   Expected behavior (according to user): The second call should return `['b']`.
    *   Problem identified: This is a classic Python "mutable default argument" issue. In Python, default arguments are evaluated only once at the time of function definition, not every time the function is called. Therefore, the same list object is reused across multiple calls if no explicit list is provided.

    *   To fix this, use `None` as the default value for the mutable argument and initialize it inside the function body if it's `None`.

    ```python
    def add_tag(tag, tags=None):
        if tags is None:
            tags = []
        tags.append(tag)
        return tags
    ```

    *   `add_tag('a')`: `tags` becomes `[]`, appends `'a'`, returns `['a']`.
    *   `add_tag('b')`: `tags` is `None`, so it initializes a *new* list `[]`, appends `'b'`, returns `['b']`.
    *   This matches the user's requirement.

    *   "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Provide only the Python code in a single ```python block.)

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
