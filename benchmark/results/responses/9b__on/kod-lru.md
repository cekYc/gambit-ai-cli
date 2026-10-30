# kod-lru · puan 0.17

**Not:** 1/6 test; başarısız: lru_basic() -> NameError("name 'Node' is not defined") | lru_update() -> NameError("name 'Node' is not defined") | lru_capacity_one() -> NameError("name 'Node' is not defined") | lru_get_refreshes() -> NameError("name 'Node' is not defined") | lru_fast() -> NameError("name 'Node' is not defined")

## Prompt

Python'da bir `LRUCache` sınıfı yaz. `LRUCache(capacity)` ile oluşturulsun; `get(key)` anahtar yoksa -1
döndürsün; `put(key, value)` eklesin ya da güncellesin. Kapasite aşılınca en uzun süredir kullanılmayan anahtar
silinsin. `get` ve `put` çağrıları anahtarı "kullanılmış" sayar. İki işlem de O(1) olsun.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

The user wants me to write an LRU Cache class in Python with the following requirements:

1. Constructor `LRUCache(capacity)` - initializes cache with given capacity
2. `get(key)` method - returns value if key exists, otherwise returns -1
3. `put(key, value)` method - adds or updates a key-value pair
4. When capacity is exceeded, remove the least recently used item
5. Both `get` and `put` should mark the key as "used" (most recently used)
6. Both operations must be O(1) time complexity

To achieve O(1) for both get and put operations with LRU cache, I need to use:
- A hash map (dictionary in Python) for O(1) access by key
- A doubly linked list to maintain the order of usage (most recently used at one end, least recently used at the other)

Let me write a complete implementation:

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> node
        
        class Node:
            def __init__(self, key=None, value=None):
                self.key = key
                self.value = value
                self.prev = None
                self.next = None
        
        self.head = Node()  # Most recently used (dummy head)
        self.tail = Node()  # Least recently used (dummy tail)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node):
        """Add node right after head"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove a node from the list"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node):
        """Move existing node to head (mark as most recently used)"""
        self._remove_node(node)
        self._add_to_head(node)
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key: int, value: int):
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new key
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            
            if len(self.cache) > self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove_node(lru_node)

I'll complete the implementation by adding a Node class definition and ensuring proper cache management. The key is maintaining O(1) operations through efficient linked list manipulation and hash map lookups.


## Cevap

```python
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        class Node:
            def __init__(self, key=None, value=None):
                self.key = key
                self.value = value
                self.prev = None
                self.next = None
        
        self.head = Node()  # Most recently used (dummy head)
        self.tail = Node()  # Least recently used (dummy tail)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node):
        """Add node right after head"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove a node from the list"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node):
        """Move existing node to head (mark as most recently used)"""
        self._remove_node(node)
        self._add_to_head(node)
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key: int, value: int):
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new key
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            
            if len(self.cache) > self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove_node(lru_node)
```

## Notlandırılan kod/komut

```
class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        
        class Node:
            def __init__(self, key=None, value=None):
                self.key = key
                self.value = value
                self.prev = None
                self.next = None
        
        self.head = Node()  # Most recently used (dummy head)
        self.tail = Node()  # Least recently used (dummy tail)
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _add_to_head(self, node):
        """Add node right after head"""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
    
    def _remove_node(self, node):
        """Remove a node from the list"""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _move_to_head(self, node):
        """Move existing node to head (mark as most recently used)"""
        self._remove_node(node)
        self._add_to_head(node)
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        
        node = self.cache[key]
        self._move_to_head(node)
        return node.value
    
    def put(self, key: int, value: int):
        if key in self.cache:
            # Update existing key
            node = self.cache[key]
            node.value = value
            self._move_to_head(node)
        else:
            # Add new key
            node = Node(key, value)
            self.cache[key] = node
            self._add_to_head(node)
            
            if len(self.cache) > self.capacity:
                # Remove least recently used (node before tail)
                lru_node = self.tail.prev
                del self.cache[lru_node.key]
                self._remove_node(lru_node)
```
