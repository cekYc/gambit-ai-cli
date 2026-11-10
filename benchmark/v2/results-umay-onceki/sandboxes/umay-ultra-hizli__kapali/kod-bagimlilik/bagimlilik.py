import heapq

class DonguHatasi(ValueError):
    def __init__(self, dongu):
        self.dongu = dongu
        super().__init__(f'Dongu tespit edildi: {dongu}')


def kurulum_sirasi(deps: dict[str, list[str]]) -> list[str]:
    # Collect all package names (keys and values)
    all_packages = set(deps.keys())
    for lst in deps.values():
        for d in lst:
            all_packages.add(d)

    # Deduplicate dependencies per package and build adjacency
    in_degree = {p: 0 for p in all_packages}
    reverse_adj = {p: [] for p in all_packages}

    for pkg, lst in deps.items():
        seen = set()
        unique_deps = []
        for d in lst:
            if d not in seen:
                seen.add(d)
                unique_deps.append(d)
        for d in unique_deps:
            in_degree[pkg] += 1
            reverse_adj[d].append(pkg)

    # Kahn's algorithm with min-heap for alphabetical ordering
    heap = []
    for p in all_packages:
        if in_degree[p] == 0:
            heapq.heappush(heap, p)

    result = []
    while heap:
        node = heapq.heappop(heap)
        result.append(node)
        for dependent in reverse_adj[node]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                heapq.heappush(heap, dependent)

    if len(result) != len(all_packages):
        # Cycle detection via DFS
        state = {p: 0 for p in all_packages}  # 0=unvisited,1=in-progress,2=done
        cycle_list = []
        found = False

        def dfs(u):
            nonlocal found, cycle_list
            if found:
                return
            state[u] = 1
            path.append(u)
            for v in deps.get(u, []):
                if v not in all_packages:
                    continue
                if state[v] == 0:
                    dfs(v)
                elif state[v] == 1:
                    idx = path.index(v)
                    cycle_list = path[idx:]
                    found = True
                    return
            path.pop()
            state[u] = 2

        path = []
        for start in sorted(all_packages):
            if state[start] == 0:
                dfs(start)
                if found:
                    break

        if not found:
            raise DonguHatasi(dongu=[])

        # Rotate so that alphabetically smallest package is first
        min_pkg = min(cycle_list)
        min_idx = cycle_list.index(min_pkg)
        rotated = cycle_list[min_idx:] + cycle_list[:min_idx]

        raise DonguHatasi(dongu=rotated)

    return result