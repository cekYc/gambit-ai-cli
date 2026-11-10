import heapq


class DonguHatasi(ValueError):
    """Döngü tespit edildiğinde fırlatılan özel değer."""
    def __init__(self, dongu: list[str]):
        self.dongu = dongu
        super().__init__(f"Döngü tespit edildi: {dongu}")


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    """
    Paket bağımlılıklarını alır ve kurulum sırasını belirler.
    - Her paket kendi bağımlılıklarından sonra gelir.
    - Birden fazla paket aynı anda kurulabilirse alfabetik olarak en küçüğü önce seçilir.
    - Döngü varsa DonguHatasi (ValueError alt sınıfı) fırlatılır.
    """
    # 1. Tüm paket adlarını topla (anahtarlar ve değerlerdeki bağımlılıklar)
    all_pkgs: set[str] = set(deps.keys())
    for lst in deps.values():
        all_pkgs.update(lst)

    # 2. Bağımlılıkları tekrarlı olmayan sıralı listelere dönüştür
    pkg_deps: dict[str, list[str]] = {}
    for pkg in all_pkgs:
        raw = deps.get(pkg, [])
        # dict.fromkeys() sıralı tekrarlıları kaldırır
        pkg_deps[pkg] = list(dict.fromkeys(raw))

    # 3. Giriş derecelerini ve bağımlıları (dependents) hesapla
    in_degree: dict[str, int] = {pkg: 0 for pkg in all_pkgs}
    dependents: dict[str, list[str]] = {pkg: [] for pkg in all_pkgs}

    for pkg, lst in pkg_deps.items():
        for dep in lst:
            # her bağımlılık paketinin giriş derecesini bir artırır
            in_degree[pkg] += 1
            dependents[dep].append(pkg)

    # 4. Başlangıçta hazır (giriş derecesi 0) paketleri min-heap'e ekle
    heap: list[str] = []
    for pkg in all_pkgs:
        if in_degree[pkg] == 0:
            heapq.heappush(heap, pkg)

    # 5. Kahn algoritması ile sıralıları çıkar
    result: list[str] = []
    while heap:
        u = heapq.heappop(heap)   # alfabetik olarak en Küçük
        result.append(u)
        for v in dependents[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                heapq.heappush(heap, v)

    # 6. Eğer tüm paketler işlenmediyse döngü var
    if len(result) != len(all_pkgs):
        remaining: set[str] = all_pkgs - set(result)

        # Döngüyü adım adım izleyerek bir cycle çıkar
        # Kalan herhangi bir paketi başlatma noktası olarak seçelim
        start = min(remaining)  # deterministik seçim
        current = start
        path: list[str] = []
        node_index: dict[str, int] = {}

        while current not in node_index:
            node_index[current] = len(path)
            path.append(current)
            # current'in remaining içinde olan, alfabetik sıralı bağımlılıklardan birini seç
            next_node = None
            for dep in sorted(pkg_deps.get(current, [])):
                if dep in remaining:
                    next_node = dep
                    break
            # Eğer remaining içinde bir bağımsız dep yoksa (teorik olarak possível olmayacak)
            # herhangi bir dep olarak geriye döndürürüz
            if next_node is None:
                if pkg_deps.get(current):
                    next_node = pkg_deps[current][0]
                else:
                    # Hiçbağımlıysa döngü mümkün değil; break yap
                    break
            current = next_node

        # Döngü bulunur: path'ten node_index[current] indeksinden sona kadar
        cycle_start_idx = node_index[current]
        cycle = path[cycle_start_idx:]

        # Döngüyü alfabetik olarak en küçük elemanla başlat
        smallest = min(cycle)
        idx = cycle.index(smallest)
        dongu = cycle[idx:] + cycle[:idx]

        raise DonguHatasi(dongu)

    return result
