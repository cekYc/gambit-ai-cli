from __future__ import annotations
import heapq
from collections import defaultdict, deque


class DonguHatasi(ValueError):
    """Topolojik sıralama sırasında döngü tespit edildiğinde fırlatılır."""
    def __init__(self, dongu: list[str]):
        super().__init__("Bağımlılık grafiğinde döngü var: " + " -> ".join(dongu) + " -> " + dongu[0])
        self.dongu = dongu


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """
    Bağımlılık sözlüğüne göre paketlerin kurulum sırasını döndürür.
    
    Args:
        deps: {paket: [bağımlılıklar]} sözlüğü. Her paket kendi bağımlılıklarından sonra gelir.
    
    Returns:
        Topolojik sırayla sıralanmış paket listesi (alfabetik kırpma ile).
    
    Raises:
        DonguHatasi: Grafikte döngü varsa, dongu özniteliği döngüyü tutar.
    """
    # Tüm düğümleri topla (anahtarlar + bağımlılık olarak geçenler)
    all_nodes: set[str] = set(deps.keys())
    for dep_list in deps.values():
        all_nodes.update(dep_list)
    
    # Giriş dereceleri ve komşuluk listesi
    in_degree: dict[str, int] = {node: 0 for node in all_nodes}
    adj: dict[str, list[str]] = {node: [] for node in all_nodes}
    
    # Kenarları ekle (bağımlılık -> paket)
    for paket, bagimliliklar in deps.items():
        # Tekrar eden bağımlılıkları temizle
        unique_deps = set(bagimliliklar)
        for dep in unique_deps:
            adj[dep].append(paket)
            in_degree[paket] += 1
    
    # Komşuları alfabetik sırala (deterministik çıktı için)
    for node in adj:
        adj[node].sort()
    
    # Kahn algoritması + min-heap (alfabetik kırpma)
    heap = [node for node in all_nodes if in_degree[node] == 0]
    heapq.heapify(heap)
    
    result: list[str] = []
    
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                heapq.heappush(heap, neighbor)
    
    # Döngü kontrolü: işlenmeyen düğüm kaldıysa döngü var
    if len(result) != len(all_nodes):
        # Döngüyü bulmak için DFS kullan
        remaining = {node for node in all_nodes if node not in result}
        dongu = _find_cycle(remaining, adj, deps)
        raise DonguHatasi(dongu)
    
    return result


def _find_cycle(remaining: set[str], adj: dict[str, list[str]], deps: dict[str, list[str]]) -> list[str]:
    """Kalan düğümlerde bir döngü bulur ve alfabetik en küçüğü başlangıç yapar."""
    # Bağımlılık yönünde graf: paket -> bağımlılıkları
    dep_adj = {node: [] for node in remaining}
    for pkg in remaining:
        for dep in deps.get(pkg, []):
            if dep in remaining:
                dep_adj[pkg].append(dep)
    for node in dep_adj:
        dep_adj[node].sort()
    
    visited = set()
    rec_stack = []  # DFS yolu
    on_stack = set()
    
    def dfs(node: str) -> list[str] | None:
        visited.add(node)
        rec_stack.append(node)
        on_stack.add(node)
        
        for neighbor in dep_adj.get(node, []):
            if neighbor not in visited:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
            elif neighbor in on_stack:
                # Döngü bulundu: neighbor'dan node'a kadar olan kısım
                idx = rec_stack.index(neighbor)
                cycle = rec_stack[idx:]
                return _normalize_cycle(cycle)
        
        rec_stack.pop()
        on_stack.remove(node)
        return None
    
    # Alfabetik sırayla başla (en küçük döngüyü bulmak için)
    for node in sorted(remaining):
        if node not in visited:
            cycle = dfs(node)
            if cycle:
                return cycle
    
    # Fallback (olmamalı)
    return sorted(remaining)[:1]


def _normalize_cycle(cycle: list[str]) -> list[str]:
    """Döngüyü alfabetik en küçük elemanla başlatacak şekilde döndürür."""
    if not cycle:
        return cycle
    min_idx = min(range(len(cycle)), key=lambda i: cycle[i])
    return cycle[min_idx:] + cycle[:min_idx]
