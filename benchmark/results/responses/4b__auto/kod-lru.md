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
        if key not in self.cache:
            return -1
        
        # Anahtarın kullanıldığını işaret et (en sona taşı) ve değer döndür
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        # Eğer anahtar zaten varsa, güncelle ve en sona taşı
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
        
        else:
            # Kapasite aşılarsa en eski elemanı sil
            if len(self.cache) >= self.capacity:
                # İlk elemanı (en çok zaman önce kullanılan) sil
                self.cache.popitem(last=False)
            
            # Yeni anahtarı ekle
            self.cache[key] = value
```

## Notlandırılan kod/komut

```
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        
        # Anahtarın kullanıldığını işaret et (en sona taşı) ve değer döndür
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        # Eğer anahtar zaten varsa, güncelle ve en sona taşı
        if key in self.cache:
            self.cache.move_to_end(key)
            self.cache[key] = value
        
        else:
            # Kapasite aşılarsa en eski elemanı sil
            if len(self.cache) >= self.capacity:
                # İlk elemanı (en çok zaman önce kullanılan) sil
                self.cache.popitem(last=False)
            
            # Yeni anahtarı ekle
            self.cache[key] = value
```
