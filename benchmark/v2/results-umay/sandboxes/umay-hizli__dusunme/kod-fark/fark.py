from __future__ import annotations

from typing import List, Tuple


def _lcs_lengths(x: list[str], y: list[str]) -> list[int]:
    """DP satiri: sonuc[j] = x ile y[:j]'nin en uzun ortak alt dizisinin uzunlugu."""
    m = len(y)
    prev = [0] * (m + 1)
    for xi in x:
        cur = [0] * (m + 1)
        for j, yj in enumerate(y, 1):
            if xi == yj:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = prev[j] if prev[j] >= cur[j - 1] else cur[j - 1]
        prev = cur
    return prev


def _hirschberg(x: list[str], y: list[str]) -> list[str]:
    """Hirschberg algoritmasi ile O(len(x)*len(y)) zamanda, O(len(y)) bellekte LCS dondurur."""
    n = len(x)
    m = len(y)
    if n == 0 or m == 0:
        return []
    if n == 1:
        return [x[0]] if x[0] in y else []
    if m == 1:
        return [y[0]] if y[0] in x else []

    mid = n // 2
    L = _lcs_lengths(x[:mid], y)

    xr = x[mid:][::-1]
    yr = y[::-1]
    R = _lcs_lengths(xr, yr)  # R[k] = LCS(xr, yr[:k]) = LCS(x[mid:], y[m-k:])

    best_j = 0
    best_val = -1
    for j in range(m + 1):
        val = L[j] + R[m - j]
        if val > best_val:
            best_val = val
            best_j = j

    left = _hirschberg(x[:mid], y[:best_j])
    right = _hirschberg(x[mid:], y[best_j:])
    return left + right


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """a listesini b'ye ceviren minimal duzenleme dizisini dondurur.

    Her eleman (' ', satir), ('-', satir) veya ('+', satir) olur.
    ' ' ve '-' sirasiyla a'yu, ' ' ve '+' sirasiyla b'yi verir.
    Ortak satir sayisi en buyuk (LCS) sekilde secilir.
    Ardisik degisikliklerde silmeler ('-') eklemelerden ('+') once gelir.
    """
    if a == b:
        return [(" ", line) for line in a]
    if not a:
        return [("+", line) for line in b]
    if not b:
        return [("-", line) for line in a]

    lcs = _hirschberg(a, b)

    # LCS'yi a ve b uzerindeki gercek (artan) indekslere yerlestir.
    matches: list[tuple[int, int]] = []
    i = j = 0
    for line in lcs:
        while i < len(a) and a[i] != line:
            i += 1
        while j < len(b) and b[j] != line:
            j += 1
        if i < len(a) and j < len(b):
            matches.append((i, j))
            i += 1
            j += 1
        else:
            # LCS dogruysa burasi asla calismamali.
            break

    result: list[tuple[str, str]] = []
    i = j = 0
    for ai, bj in matches:
        while i < ai:
            result.append(("-", a[i]))
            i += 1
        while j < bj:
            result.append(("+", b[j]))
            j += 1
        result.append((" ", a[ai]))  # a[ai] == b[bj]
        i = ai + 1
        j = bj + 1

    while i < len(a):
        result.append(("-", a[i]))
        i += 1
    while j < len(b):
        result.append(("+", b[j]))
        j += 1

    return result


if __name__ == "__main__":
    assert satir_farki([], []) == []
    assert satir_farki(["x"], ["x"]) == [(" ", "x")]
    assert satir_farki(["x"], ["y"]) == [("-", "x"), ("+", "y")]
    assert satir_farki(["a", "b", "c"], ["a", "x", "c"]) == [
        (" ", "a"), ("-", "b"), ("+", "x"), (" ", "c")
    ]

    a = ["a", "b", "c", "d"]
    b = ["a", "x", "c", "y", "d"]
    r = satir_farki(a, b)
    assert [line for op, line in r if op in (" ", "-")] == a
    assert [line for op, line in r if op in (" ", "+")] == b
    ops = [op for op, _ in r]
    for k in range(len(ops) - 1):
        assert not (ops[k] == "+" and ops[k + 1] == "-")

    print("Basit testler gecti.")
