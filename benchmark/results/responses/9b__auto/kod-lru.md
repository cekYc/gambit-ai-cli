# kod-lru · puan 0.17

**Not:** 1/6 test; başarısız: lru_basic() -> AttributeError("'dict' object has no attribute 'move_to_end'") | lru_update() -> AttributeError("'dict' object has no attribute 'move_to_end'") | lru_capacity_one() -> AttributeError("'dict' object has no attribute 'move_to_end'") | lru_get_refreshes() -> AttributeError("'dict' object has no attribute 'move_to_end'") | lru_fast() -> AttributeError("'dict' object has no attribute 'mo

## Prompt

Python'da bir `LRUCache` sınıfı yaz. `LRUCache(capacity)` ile oluşturulsun; `get(key)` anahtar yoksa -1
döndürsün; `put(key, value)` eklesin ya da güncellesin. Kapasite aşılınca en uzun süredir kullanılmayan anahtar
silinsin. `get` ve `put` çağrıları anahtarı "kullanılmış" sayar. İki işlem de O(1) olsun.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Cache'e erişim yaptığımız için en son kullanılmış sayalım.
        # Python 3.7+ dict'leri sıralı tutar ve ekleme/güncelleme sırasında
        # anahtarı sona taşır. Bu özellikten yararlanarak O(1) işlem yapabiliriz.
        self.cache.move_to_end(key)
        
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Anahtar zaten varsa güncelle ve sona taşı
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Yeni anahtar ekle
            self.cache[key] = value
            
            # Kapasite aşıldıysa en baştaki (en uzun süredir kullanılmayan) anahtarı sil
            if len(self.cache) > self.capacity:
                # İlk elemanı al ve sil
                first_key, _ = next(iter(self.cache.items()))
                del self.cache[first_key]
```

## Notlandırılan kod/komut

```
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        # Cache'e erişim yaptığımız için en son kullanılmış sayalım.
        # Python 3.7+ dict'leri sıralı tutar ve ekleme/güncelleme sırasında
        # anahtarı sona taşır. Bu özellikten yararlanarak O(1) işlem yapabiliriz.
        self.cache.move_to_end(key)
        
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Anahtar zaten varsa güncelle ve sona taşı
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Yeni anahtar ekle
            self.cache[key] = value
            
            # Kapasite aşıldıysa en baştaki (en uzun süredir kullanılmayan) anahtarı sil
            if len(self.cache) > self.capacity:
                # İlk elemanı al ve sil
                first_key, _ = next(iter(self.cache.items()))
                del self.cache[first_key]
```
