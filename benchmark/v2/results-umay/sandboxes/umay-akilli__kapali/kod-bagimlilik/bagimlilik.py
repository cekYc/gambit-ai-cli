from collections import deque


class DonguHatasi(ValueError):
    """Bağımlılık grafiğinde döngü tespit edildiğinde fırlatılan istisna."""
    
    def __init__(self, dongu: list[str]):
        self.dongu = dongu
        super().__init__(f"Döngü tespit edildi: {' -> '.join(dongu)} -> {dongu[0]}")


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """
    Bağımlılık grafiğine göre paketlerin kurulum sırasını belirler (topolojik sıralama).
    
    Args:
        deps: Her paketin kurulumdan önce kurulması gereken paketlerin listesi.
              Anahtarlar paket isimleri, değerler bağımlılık listeleri.
    
    Returns:
        Tüm paketlerin, her paket kendi bağımlılıklarından sonra geleceği şekilde
        sıralanmış listesi. Aynı anda kurulabilecek paketler alfabetik sırada.
    
    Raises:
        DonguHatasi: Bağımlılık grafiğinde döngü varsa, döngü paketleriyle birlikte.
    """
    # Tüm düğümleri topla (anahtarlar + bağımlılıklarda geçenler)
    all_nodes = set(deps.keys())
    for dep_list in deps.values():
        all_nodes.update(dep_list)
    
    # Her düğüm için bağımlılık seti (tekrarları temizle)
    adj = {node: set(deps.get(node, [])) for node in all_nodes}
    
    # Giriş dereceleri (in-degree) hesapla
    in_degree = {node: 0 for node in all_nodes}
    for node in all_nodes:
        for dep in adj[node]:
            in_degree[dep] += 1
    
    # Giriş derecesi 0 olan düğümleri alfabetik sırada işlemek için sıralı liste
    # heapq yerine basit liste + sort kullanıyoruz (küçük veri için yeterli,
    # binlerce paket için de O(V log V) kabul edilebilir)
    zero_degree = [node for node in all_nodes if in_degree[node] == 0]
    zero_degree.sort()
    
    result = []
    
    while zero_degree:
        # Alfabetik en küçüğü al
        current = zero_degree.pop(0)
        result.append(current)
        
        # Komşuların giriş derecesini azalt
        for neighbor in sorted(adj[current]):  # Deterministik sıra için sıralı
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                # Alfabetik sırayı korumak için insert et
                # bisect kullanabiliriz ama basit append + sort da olur
                zero_degree.append(neighbor)
                zero_degree.sort()
    
    # Tüm düğümler işlendiyse döngü yok
    if len(result) == len(all_nodes):
        return result
    
    # Döngü var - Kahn algoritması ile tespit edilemeyen düğümler döngüdedir
    # Döngüyü bulmak için DFS kullan
    remaining = [node for node in all_nodes if node not in result]
    
    # Alt graf üzerinde döngü bul
    subgraph = {node: adj[node] for node in remaining}
    
    # DFS ile döngü bul
    visited = set()
    rec_stack = set()
    parent = {}
    cycle_start = None
    
    def dfs(node):
        nonlocal cycle_start
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in sorted(subgraph.get(node, [])):  # Deterministik için sıralı
            if neighbor not in visited:
                parent[neighbor] = node
                if dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                # Döngü bulundu
                cycle_start = neighbor
                return True
        
        rec_stack.remove(node)
        return False
    
    for node in sorted(remaining):  # Alfabetik sırayla başla
        if node not in visited:
            parent[node] = None
            if dfs(node):
                break
    
    if cycle_start is not None:
        # Döngüyü yeniden oluştur
        cycle = []
        node = cycle_start
        while True:
            cycle.append(node)
            node = parent[node]
            if node == cycle_start or node is None:
                break
        cycle.reverse()
        
        # Döngüyü alfabetik en küçükle başlat
        min_idx = cycle.index(min(cycle))
        cycle = cycle[min_idx:] + cycle[:min_idx]
        
        raise DonguHatasi(cycle)
    
    # Buraya gelmemeli ama güvenlik için
    raise DonguHatasi(sorted(remaining)[:1])
