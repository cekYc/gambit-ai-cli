import collections
from typing import Dict, List

class DonguHatasi(ValueError):
    """Bağımlılık döngüsünü işaretleyen özel hata sınıfı."""
    def __init__(self, dongu: List[str]):
        self.dongu = dongu
        super().__init__(f"Bağımlılık döngüsü tespit edildi: {dongu}")

def kurulum_sirasi(deps: Dict[str, List[str]]) -> List[str]:
    """Paket bağımlılıklarına göre kurulma sırasını belirler (Topological Sort)."""
    # 1. Tüm düğümleri (paketleri) ve grafik yapısını oluşturma
    packages = set(deps.keys())
    for dependencies in deps.values():
        packages.update(dependencies)

    # Bağımlılık -> Bağımlılığı gerektirenler (Adjacency List)
    # dependency_to_dependents[dep] = [pkg1, pkg2, ...]
    dependency_to_dependents = collections.defaultdict(list)
    # In-Degree: Paketin kurulmadan önce çözülmesi gereken bağımlılık sayısı
    in_degree = collections.defaultdict(int)

    for pkg in packages:
        in_degree[pkg] = 0

    for pkg, dependencies in deps.items():
        for dep in dependencies:
            # dep, pkg'nın bağımlılığıdır. Yani dep -> pkg kenarı var.
            dependency_to_dependents[dep].append(pkg)
            in_degree[pkg] += 1

    # 2. Sıfır in-degree'lü paketlerle başlama (Alfabetik sıralama için min-heap kullanacağız)
    import heapq
    queue = []
    for pkg in packages:
        if in_degree[pkg] == 0:
            heapq.heappush(queue, pkg)

    sorted_order = []

    # 3. Kahn Algoritması
    while queue:
        # En küçük alfabetik paketi seçme (deterministik sonuç için kritik)
        u = heapq.heappop(queue)
        sorted_order.append(u)

        # Bağımlı paketleri güncelleme
        for v in dependency_to_dependents[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(queue, v)

    # 4. Döngü Kontrolü
    if len(sorted_order) != len(packages):
        # Döngü var. Hangi döngü olduğunu bulmalıyız.
        remaining_packages = [pkg for pkg in packages if in_degree[pkg] > 0]
        
        # Döngüdeki herhangi bir düğümden DFS ile döngü yolunu bulma
        # Sadece kalan düğümler üzerinde DFS çalıştırılır.
        def find_cycle(start_node):
            stack = [(start_node, [start_node], {start_node})]
            visited_in_path = set()
            
            while stack:
                current, path, path_set = stack.pop()
                
                # Döngü kontrolü: eğer mevcut düğüm, path içindeki ilk düğüme (başlangıç) bağlıysa
                # Bu kontrol, döngüyü netleştirmek için yeterli değildir, daha kapsamlı bir DFS gerekir.
                
                # Basit döngü bulma (daha sağlam bir DFS yapısı gerekiyor)
                # Sadece kalan düğümler arasındaki bağımlılıkları takip etmeliyiz.
                
                # Basit döngü tespiti için: bir düğüm hem yığınta hem de path içinde olmalı.
                
                # Yeniden yapılandırılmış DFS döngü bulucu:
                # state: 0=Gezinmiyor, 1=Geziniyor (yığın/path içinde), 2=Gezindi (bitirildi)
                # cycles: Bulunan döngüleri tutar.
                pass
        
        # Basitleştirilmiş döngü bulma: Kalan düğümlerden rastgele birini alıp DFS yapalım.
        def dfs_cycle_detector(start_node):
            # state: 0=Gezinmiyor, 1=Geziniyor, 2=Gezindi
            state = {pkg: 0 for pkg in remaining_packages}
            path_stack = []
            
            def dfs(u):
                state[u] = 1  # Geziniyor
                path_stack.append(u)
                
                # u'yu gerektirenleri bulmalıyız (bağımlılık yönünde).
                # Bu durumda, ters grafiğe ihtiyacımız var. 
                # dependencies: {pkg: [dep1, dep2]}
                
                for dep in deps.get(u, []):
                    if dep in remaining_packages: # Sadece döngüdeki paketler
                        if state[dep] == 1: # Döngü bulundu!
                            # Döngü, path_stack içinde dep'ten sonraki elemanlardan oluşur.
                            cycle_start_index = path_stack.index(dep)
                            cycle = path_stack[cycle_start_index:]
                            # Döngü listesinin alfabetik olarak en küçük paketle başlamasını sağla
                            min_pkg = min(cycle)
                            min_index = cycle.index(min_pkg)
                            return cycle[min_index:] + cycle[:min_index]
                        
                        elif state[dep] == 0:
                            result = dfs(dep)
                            if result: # Döngü bulunduysa yay
                                return result
                
                state[u] = 2  # Gezindi
                path_stack.pop()
                return None
            
            return dfs(start_node)
        
        # Döngüdeki ilk paketi belirle (alfabetik olarak en küçük)
        min_remaining_pkg = min(remaining_packages)
        
        # Döngüyü bul ve hatayı fırlat
        cycle = dfs_cycle_detector(min_remaining_pkg)
        
        if cycle: # Döngü bulunursa (her zaman bulunmalı)
            raise DonguHatasi(cycle)
        else:
            # Teorik olarak olmamalı, ancak güvenlik için
            raise DonguHatasi([min_remaining_pkg]) # En azından bir paket döngüde kabul edilir

    return sorted_order
