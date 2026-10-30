# kod-lru · puan 1.00

**Not:** 6/6 test

## Prompt

Python'da bir `LRUCache` sınıfı yaz. `LRUCache(capacity)` ile oluşturulsun; `get(key)` anahtar yoksa -1
döndürsün; `put(key, value)` eklesin ya da güncellesin. Kapasite aşılınca en uzun süredir kullanılmayan anahtar
silinsin. `get` ve `put` çağrıları anahtarı "kullanılmış" sayar. İki işlem de O(1) olsun.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

*   Goal: Implement an `LRUCache` class in Python.
    *   Constructor: `LRUCache(capacity)`.
    *   Method `get(key)`: Returns value if key exists, else -1. Marks key as "used".
    *   Method `put(key, value)`: Adds or updates key-value pair. If capacity is exceeded, remove the Least Recently Used (LRU) item. Marks key as "used".
    *   Complexity Requirement: Both `get` and `put` must be $O(1)$.
    *   Output Format: Only Python code in a single ```python block.

    *   To achieve $O(1)$ for both lookup (via hash map) and ordering (to track usage), the standard approach is to use a combination of a **Hash Map** (dictionary) and a **Doubly Linked List**.
    *   In Python, `collections.OrderedDict` provides exactly this functionality out of the box. It maintains an internal doubly linked list for insertion order and allows moving items to the end (most recent).

    *   Using `collections.OrderedDict`:
        *   `__init__(self, capacity)`: Store capacity. Initialize `OrderedDict`.
        *   `get(key)`: If key in dict, move it to the end (`move_to_end`) and return value. Else, return -1.
        *   `put(key, value)`: If key exists, delete/update and move to end. If new, add. If size > capacity, pop item from start (`popitem(last=False)`).

    ```python
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.cache = OrderedDict()

        def get(self, key: int) -> int:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]

        def put(self, key: int, value: int) -> None:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    ```

    *   `get`: `OrderedDict.__getitem__` is $O(1)$, `move_to_end` is $O(1)$. Total $O(1)$.
    *   `put`: `OrderedDict.__setitem__` is $O(1)$, `popitem(last=False)` is $O(1)$. Total $O(1)$.

    *   The user asked for "Sadece Python kodunu tek bir ```python bloğu içinde ver" (Give only the Python code in a single ```python block).

    ```python
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.cache = OrderedDict()

        def get(self, key: int) -> int:
            if key not in self.cache:
                return -1
            # Anahtarı en sona (en son kullanılan) taşı
            self.cache.move_to_end(key)
            return self.cache[key]

        def put(self, key: int, value: int) -> None:
            if key in self.cache:
                # Zaten varsa, güncellenmesi için en sona taşı
                self.cache.move_to_end(key)
            self.cache[key] = value
            
            # Kapasite aşıldıysa en eski (baştaki) öğeyi sil
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    ```

    *   `LRUCache(capacity)`? Yes.
    *   `get(key)` returns -1 if not found? Yes.
    *   `put(key, value)` adds/updates? Yes.
    *   Evict LRU when capacity exceeded? Yes (`popitem(last=False)`).
    *   $O(1)$ for both? Yes (using `OrderedDict`).

    Wait, I should check if there's any ambiguity about "Sadece Python kodunu... ver". Usually, this means no explanation text outside the block.

    Let's refine the code to be as clean as possible.

    ```python
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.cache = OrderedDict()

        def get(self, key: int) -> int:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]

        def put(self, key: int, value: int) -> None:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    ```

    One detail: In `put`, if I update an existing key, the order should change to "most recent". My code does this by calling `move_to_end` before setting or just letting `OrderedDict` handle it? Actually, in Python 3.7+, standard dicts maintain insertion order, but `OrderedDict` has `move_to_end`. If I do `self.cache[key] = value`, and the key already exists, the position doesn't change in a normal dict, so `move_to_end` is necessary to ensure it becomes "most recent".

    Correct logic for `put`:
    1. If key in cache: move to end (mark as used).
    2. Set/Update value.
    3. If size > capacity: pop item from the beginning (LRU).

    Wait, if I do `self.cache[key] = value` on an existing key in `OrderedDict`, it does *not* move it to the end automatically. It stays in its current position. So `move_to_end` is required for both `get` and `put` (when updating).

    Let's re-verify:
    ```python
    from collections import OrderedDict
    d = OrderedDict({'a': 1, 'b': 2})
    d['a'] = 3
    print(d) # Output: OrderedDict([('a', 3), ('b', 2)]) -> 'a' is still at the start!
    ```
    So yes, `move_to_end` is mandatory for $O(1)$ LRU logic.

    Final Code Structure:
    ```python
    from collections import OrderedDict

    class LRUCache:
        def __init__(self, capacity: int):
            self.capacity = capacity
            self.cache = OrderedDict()

        def get(self, key: int) -> int:
            if key not in self.cache:
                return -1
            self.cache.move_to_end(key)
            return self.cache[key]

        def put(self, key: int, value: int) -> None:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                self.cache.popitem(last=False)
    ```

    Wait, if I call `put` for an existing key, and then check capacity... the logic holds. If it's a new key, length increases, we might pop. If it was an update, length stays same, no pop needed (but code handles it fine).

    One edge case: Capacity 0? Usually not allowed in these problems, but `capacity` is assumed $>0$.

    Final check on requirements:
    - $O(1)$ for both? Yes.
    - Single python block? Yes.
    - Only Python code? Yes.

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
        # Anahtarı en son kullanılan (most recently used) yapmak için sona taşı
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Anahtar zaten varsa, güncellenmesi için en sona taşı
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Kapasite aşılmışsa, en eski (least recently used) öğeyi sil
        if len(self.cache) > self.capacity:
            # last=False, FIFO sırasına göre yani baştaki (en eski) öğeyi çıkarır
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
        # Anahtarı en son kullanılan (most recently used) yapmak için sona taşı
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Anahtar zaten varsa, güncellenmesi için en sona taşı
            self.cache.move_to_end(key)
        self.cache[key] = value
        
        # Kapasite aşılmışsa, en eski (least recently used) öğeyi sil
        if len(self.cache) > self.capacity:
            # last=False, FIFO sırasına göre yani baştaki (en eski) öğeyi çıkarır
            self.cache.popitem(last=False)
```
