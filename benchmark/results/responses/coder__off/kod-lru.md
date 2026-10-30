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
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return -1

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)  # En son kullanılmış anahtarı hemen sağa taşı
        if len(self.cache) > self.capacity:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
```

Buun `LRUCache` sınıfı, Python'da bir süper performanslı LRU (Least Recently Used) kesişim belleği (cache) implementasyonunu içerir. Bellek, kapasite sınırları ile sınırlanır ve anahtarlar için O(1) işlem hizmeti verilir. `get(key)` metodu anahtarda bulunuyorsa, anahtara sahip değeri hemen sağa taşıarak en son kullanılmış olarak işaretler, yoksa -1 döndürür. `put(key, value)` metodu anahtar ve değer ekler veya günceller. Bellek kapasitesi aşılınca en uzun süredir kullanılan anahtarı siler.

## Notlandırılan kod/komut

```
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return -1

    def put(self, key, value):
        self.cache[key] = value
        self.cache.move_to_end(key)  # En son kullanılmış anahtarı hemen sağa taşı
        if len(self.cache) > self.capacity:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
```
