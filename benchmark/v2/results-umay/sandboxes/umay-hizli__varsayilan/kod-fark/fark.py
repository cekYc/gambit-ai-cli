"""fark.py: Minimal diff-like edit sequence between two string lists."""

from __future__ import annotations

from typing import List, Tuple


def _lcs_indices(a: List[str], b: List[str]) -> Tuple[List[int], List[int]]:
    """Return LCS index pairs (ia, ib) using Hirschberg linear-space algorithm."""

    n = len(a)
    m = len(b)

    if n == 0 or m == 0:
        return [], []

    # Small inputs: classic O(n*m) DP backtrack.
    if n * m <= 250_000:
        dp = [[0] * (m + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            ai = a[i - 1]
            row = dp[i]
            prev_row = dp[i - 1]
            for j in range(1, m + 1):
                if ai == b[j - 1]:
                    row[j] = prev_row[j - 1] + 1
                else:
                    row[j] = row[j - 1] if row[j - 1] >= prev_row[j] else prev_row[j]

        ia_list: List[int] = []
        ib_list: List[int] = []
        i, j = n, m
        while i > 0 and j > 0:
            if a[i - 1] == b[j - 1]:
                ia_list.append(i - 1)
                ib_list.append(j - 1)
                i -= 1
                j -= 1
            elif dp[i - 1][j] >= dp[i][j - 1]:
                i -= 1
            else:
                j -= 1
        ia_list.reverse()
        ib_list.reverse()
        return ia_list, ib_list

    # Hirschberg divide & conquer for large inputs.
    if n == 1:
        try:
            j = b.index(a[0])
            return [0], [j]
        except ValueError:
            return [], []

    mid = n // 2
    a_left = a[:mid]
    a_right = a[mid:]

    def lcs_row(x: List[str], y: List[str]) -> List[int]:
        prev = [0] * (len(y) + 1)
        for xi in x:
            cur = [0] * (len(y) + 1)
            for j in range(1, len(y) + 1):
                if xi == y[j - 1]:
                    cur[j] = prev[j - 1] + 1
                else:
                    cur[j] = cur[j - 1] if cur[j - 1] >= prev[j] else prev[j]
            prev = cur
        return prev

    left_scores = lcs_row(a_left, b)

    rev_a_right = list(reversed(a_right))
    rev_b = list(reversed(b))
    right_scores_rev = lcs_row(rev_a_right, rev_b)
    right_scores = [0] * (m + 1)
    right_scores = [right_scores_rev[m - j] for j in range(m + 1)]

    best_k = 0
    best_val = -1
    for k in range(m + 1):
        val = left_scores[k] + right_scores[k]
        if val > best_val:
            best_val = val
            best_k = k

    left_ia, left_ib = _lcs_indices(a_left, b[:best_k])
    right_ia, right_ib = _lcs_indices(a_right, b[best_k:])
    right_ia = [mid + x for x in right_ia]
    right_ib = [best_k + x for x in right_ib]

    return left_ia + right_ia, left_ib + right_ib


def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    """Return minimal edit sequence turning list a into list b.

    Each element is one of:
      (" ", line)  common line
      ("-", line)  deleted from a
      ("+", line)  inserted into b

    " " and "-" lines in order reproduce a; " " and "+" lines reproduce b.
    Deletions precede insertions within a contiguous change block.
    """

    ia, ib = _lcs_indices(a, b)

    result: List[Tuple[str, str]] = []
    i = j = 0
    n = len(a)
    m = len(b)

    for a_idx, b_idx in zip(ia, ib):
        while i < a_idx:
            result.append(("-", a[i]))
            i += 1
        while j < b_idx:
            result.append(("+", b[j]))
            j += 1
        result.append((" ", a[a_idx]))
        i += 1
        j += 1

    while i < n:
        result.append(("-", a[i]))
        i += 1
    while j < m:
        result.append(("+", b[j]))
        j += 1

    return result


if __name__ == "__main__":  # pragma: no cover
    a = ["merhaba", "dunya", "foo", "bar"]
    b = ["merhaba", "dünya", "foo", "baz"]
    for tag, line in satir_farki(a, b):
        print(tag, line)
    out_a = [line for tag, line in satir_farki(a, b) if tag in (" ", "-")]
    out_b = [line for tag, line in satir_farki(a, b) if tag in (" ", "+")]
    assert out_a == a, out_a
    assert out_b == b, out_b
    tags = [tag for tag, _ in satir_farki(a, b)]
    for x, y in zip(tags, tags[1:]):
        assert not (x == "+" and y == "-"), tags
    print("smoke OK")
