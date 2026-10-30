# kod-lru · puan 0.83

**Not:** 5/6 test; başarısız: lru_update()

## Prompt

Python'da bir `LRUCache` sınıfı yaz. `LRUCache(capacity)` ile oluşturulsun; `get(key)` anahtar yoksa -1
döndürsün; `put(key, value)` eklesin ya da güncellesin. Kapasite aşılınca en uzun süredir kullanılmayan anahtar
silinsin. `get` ve `put` çağrıları anahtarı "kullanılmış" sayar. İki işlem de O(1) olsun.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> (value, node)
        # Doubly linked list for O(1) access to LRU and MRU nodes
        self.head = Node()  # dummy head
        self.tail = Node()  # dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key):
        if key not in self.cache:
            return -1
        value, node = self.cache[key]
        self._move_to_front(node)
        return value

    def put(self, key, value):
        if key in self.cache:
            _, node = self.cache[key]
            node.val = value
            self._move_to_front(node)
        else:
            node = Node(key, value)
            self.cache[key] = (value, node)
            self._add_to_front(node)
            if len(self.cache) > self.capacity:
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]

    def _move_to_front(self, node):
        self._remove(node)
        self._add_to_front(node)

    def _add_to_front(self, node):
        # Insert node right after head (before MRU position)
        next_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next_node
        next_node.prev = node

    def _remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node


class Node:
    __slots__ = ('key', 'val', 'prev', 'next')

    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None
```

## Notlandırılan kod/komut

```
class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # key -> (value, node)
        # Doubly linked list for O(1) access to LRU and MRU nodes
        self.head = Node()  # dummy head
        self.tail = Node()  # dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key):
        if key not in self.cache:
            return -1
        value, node = self.cache[key]
        self._move_to_front(node)
        return value

    def put(self, key, value):
        if key in self.cache:
            _, node = self.cache[key]
            node.val = value
            self._move_to_front(node)
        else:
            node = Node(key, value)
            self.cache[key] = (value, node)
            self._add_to_front(node)
            if len(self.cache) > self.capacity:
                lru_node = self.tail.prev
                self._remove(lru_node)
                del self.cache[lru_node.key]

    def _move_to_front(self, node):
        self._remove(node)
        self._add_to_front(node)

    def _add_to_front(self, node):
        # Insert node right after head (before MRU position)
        next_node = self.head.next
        self.head.next = node
        node.prev = self.head
        node.next = next_node
        next_node.prev = node

    def _remove(self, node):
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node


class Node:
    __slots__ = ('key', 'val', 'prev', 'next')

    def __init__(self, key=None, val=None):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None
```
