# kod-lru · puan 1.00

**Not:** 6/6 test

## Prompt

Python'da bir `LRUCache` sınıfı yaz. `LRUCache(capacity)` ile oluşturulsun; `get(key)` anahtar yoksa -1
döndürsün; `put(key, value)` eklesin ya da güncellesin. Kapasite aşılınca en uzun süredir kullanılmayan anahtar
silinsin. `get` ve `put` çağrıları anahtarı "kullanılmış" sayar. İki işlem de O(1) olsun.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Anahtarı en sona (en güncel/kullanılmış) taşı
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Varsa güncelle ve en sona taşı
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Kapasite aşıldıysa en eski (ilk) öğeyi sil
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

## Notlandırılan kod/komut

```
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Anahtarı en sona (en güncel/kullanılmış) taşı
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Varsa güncelle ve en sona taşı
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Kapasite aşıldıysa en eski (ilk) öğeyi sil
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```
