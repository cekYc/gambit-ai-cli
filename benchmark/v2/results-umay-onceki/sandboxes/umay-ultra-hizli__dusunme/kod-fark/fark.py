def satir_farki(a: list[str], b: list[str]) -> list[tuple[str, str]]:
    m, n = len(a), len(b)
    if m == 0 and n == 0:
        return []
    if m == 0:
        return [("+", x) for x in b]
    if n == 0:
        return [("-", x) for x in a]

    # DP for LCS
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        ai = a[i-1]
        row = dp[i]
        prev_row = dp[i-1]
        for j in range(1, n + 1):
            if ai == b[j-1]:
                row[j] = prev_row[j-1] + 1
            else:
                row[j] = max(prev_row[j], row[j-1])

    # backtrack to get LCS index pairs
    lcs_pairs = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i-1] == b[j-1]:
            lcs_pairs.append((i-1, j-1))
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    lcs_pairs.reverse()  # increasing i and j

    ops = []
    prev_i, prev_j = -1, -1

    for curr_i, curr_j in lcs_pairs:
        # segment before this match
        a_start = prev_i + 1
        a_end = curr_i - 1
        b_start = prev_j + 1
        b_end = curr_j - 1

        for idx in range(a_start, a_end + 1):
            ops.append(("-", a[idx]))
        for idx in range(b_start, b_end + 1):
            ops.append(("+", b[idx]))

        # the common element
        ops.append((" ", a[curr_i]))

        prev_i, prev_j = curr_i, curr_j

    # segment after last match
    a_start = prev_i + 1
    a_end = m - 1
    b_start = prev_j + 1
    b_end = n - 1

    for idx in range(a_start, a_end + 1):
        ops.append(("-", a[idx]))
    for idx in range(b_start, b_end + 1):
        ops.append(("+", b[idx]))

    return ops
