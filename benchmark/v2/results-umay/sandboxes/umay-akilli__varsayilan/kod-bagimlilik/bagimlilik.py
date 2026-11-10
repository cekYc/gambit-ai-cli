from __future__ import annotations
from collections import defaultdict, deque


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde döngü tespit edildiğinde fırlatılır."""
    def __init__(self, dongu: list[str]):
        self.dongu = dongu
        super().__init__(f"Bağımlılık döngüsü tespit edildi: {' -> '.join(dongu)}")


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """
    Bağımlılık grafiğini toplolojik olarak sıralar (Kahn algoritması).
    
    Args:
        deps: {paket: [bağımlılıklar]} sözlüğü. Bağımlılıklar paketten önce kurulmalıdır.
    
    Returns:
        Kurulabilir paketlerin listesi (bağımlılıklar önce, sonra paket).
        Aynı anda kurulabilecek paketler alfabetik sırada alınır.
    
    Raises:
        DonguHatasi: Grafikta döngü varsa, döngü paketleriyle birlikte fırlatılır.
    """
    # Tüm düğümleri topla (anahtarlar + bağımlılıklar)
    all_nodes: set[str] = set(deps.keys())
    for dep_list in deps.values():
        all_nodes.update(dep_list)
    
    # Giriş dereceleri (in-degree) ve ters komşuluk listesi
    in_degree: dict[str, int] = defaultdict(int)
    reverse_adj: dict[str, list[str]] = defaultdict(list)
    
    for node in all_nodes:
        # Her düğüm için giriş derecesi 0'dan başlar
        in_degree[node] = 0
    
    for node, dep_list in deps.items():
        # Tekrar eden bağımlılıkları tekilleştir
        unique_deps = set(dep_list)
        for dep in unique_deps:
            reverse_adj[dep].append(node)
            in_degree[node] += 1
    
    # Sıfır giriş dereceli düğümleri alfabetik sıra ile işlemek için deque
    # İlk başta sıralı bir liste olarak al
    zero_queue = deque(sorted([n for n in all_nodes if in_degree[n] == 0]))
    
    result: list[str] = []
    
    while zero_queue:
        current = zero_queue.popleft()
        result.append(current)
        
        # Komşuların giriş derecesini azalt
        for neighbor in reverse_adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                zero_queue.append(neighbor)
        
        # Her adımda kuyruğu yeniden sırala (alfabetik sıra için)
        # Ancak bu O(n log n) olabilir. Daha verimli: heap kullan.
        # Basitlik için kuyruğu sıralı tutalım - ama Python'da deque sıralı değil.
        # Doğru yaklaşım: heapq kullan.
    
    # Yukarıdaki mantık hatalı: deque sıralı tutmuyor. Yeniden yazalım.
    
    # ... (fonksiyon tamamlanacak)
    return result


def kurulum_sirasi_v2(deps: dict[str, list[str]]) -> list[str]:
    """Doğru implementasyon: heapq ile alfabetik sıra."""
    import heapq
    
    all_nodes: set[str] = set(deps.keys())
    for dep_list in deps.values():
        all_nodes.update(dep_list)
    
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    reverse_adj: dict[str, list[str]] = defaultdict(list)
    
    for node, dep_list in deps.items():
        unique_deps = set(dep_list)
        for dep in unique_deps:
            reverse_adj[dep].append(node)
            in_degree[node] += 1
    
    # Min-heap ile alfabetik sıra
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result: list[str] = []
    
    while heap:
        current = heapq.heappop(heap)
        result.append(current)
        
        for neighbor in reverse_adj[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    if len(result) != len(all_nodes):
        # Döngü var - döngüyü bul
        cycle = _find_cycle(deps, all_nodes)
        raise DonguHatasi(cycle)
    
    return result


def _find_cycle(deps: dict[str, list[str]], all_nodes: set[str]) -> list[str]:
    """DFS ile döngü bulur, alfabetik en küçük paketten başlayacak şekilde döndürür."""
    # Renkler: 0=beyaz (ziyaret edilmedi), 1=gri (işleniyor), 2=siyah (bitirildi)
    color: dict[str, int] = {node: 0 for node in all_nodes}
    parent: dict[str, str | None] = {node: None for node in all_nodes}
    cycle_path: list[str] | None = None
    
    # Komşuluk listesi (ileri yönlü: paket -> bağımlılıkları)
    adj: dict[str, list[str]] = defaultdict(list)
    for node, dep_list in deps.items():
        for dep in set(dep_list):
            adj[node].append(dep)
    
    # Alfabetik sırayla DFS başlat - en küçük paketten başlayan döngüyü bulmak için
    for start_node in sorted(all_nodes):
        if color[start_node] == 0:
            stack: list[tuple[str, int]] = [(start_node, 0)]  # (node, next_child_index)
            color[start_node] = 1
            
            while stack:
                node, child_idx = stack[-1]
                
                if child_idx < len(adj[node]):
                    neighbor = adj[node][child_idx]
                    stack[-1] = (node, child_idx + 1)
                    
                    if color[neighbor] == 0:
                        color[neighbor] = 1
                        parent[neighbor] = node
                        stack.append((neighbor, 0))
                    elif color[neighbor] == 1:
                        # Döngü bulundu! neighbor -> ... -> node -> neighbor
                        cycle = [neighbor]
                        curr = node
                        while curr != neighbor:
                            cycle.append(curr)
                            curr = parent[curr]
                        cycle.reverse()  # neighbor -> ... -> node sırasına getir
                        
                        # Döngüyü alfabetik en küçük paketle başlat
                        min_idx = cycle.index(min(cycle))
                        cycle = cycle[min_idx:] + cycle[:min_idx]
                        
                        return cycle
                else:
                    color[node] = 2
                    stack.pop()
    
    # Bulunamazsa (olmamalı), boş liste döndür
    return []


# Ana fonksiyon olarak v2'yi kullan
kurulum_sirasi = kurulum_sirasi_v2
