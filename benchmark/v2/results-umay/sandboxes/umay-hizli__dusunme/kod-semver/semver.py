import re
from functools import cmp_to_key

_VERSION_RE = re.compile(
    r'^v?(?P<major>0|[1-9][0-9]*)\.(?P<minor>0|[1-9][0-9]*)\.(?P<patch>0|[1-9][0-9]*)'
    r'(?:-(?P<pre>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?'
    r'(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$'
)

def _parse(version):
    if not isinstance(version, str):
        raise ValueError(f'Geçersiz sürüm: {version!r}')
    m = _VERSION_RE.match(version)
    if not m:
        raise ValueError(f'Geçersiz sürüm: {version!r}')

    major = int(m.group('major'))
    minor = int(m.group('minor'))
    patch = int(m.group('patch'))

    pre = m.group('pre')
    pre_ids = pre.split('.') if pre else []

    for ident in pre_ids:
        if ident.isdigit() and len(ident) > 1 and ident[0] == '0':
            raise ValueError(f'Geçersiz ön-sürüm kimliği: {ident!r}')

    return (major, minor, patch, pre_ids)

def _compare_pre(a_ids, b_ids):
    for x, y in zip(a_ids, b_ids):
        x_num = x.isdigit()
        y_num = y.isdigit()

        if x_num and y_num:
            xi = int(x)
            yi = int(y)
            if xi < yi:
                return -1
            if xi > yi:
                return 1
        elif x_num and not y_num:
            return -1
        elif not x_num and y_num:
            return 1
        else:
            if x < y:
                return -1
            if x > y:
                return 1

    if len(a_ids) < len(b_ids):
        return -1
    if len(a_ids) > len(b_ids):
        return 1
    return 0

def compare(a: str, b: str) -> int:
    pa = _parse(a)
    pb = _parse(b)

    for i in range(3):
        if pa[i] < pb[i]:
            return -1
        if pa[i] > pb[i]:
            return 1

    a_pre = pa[3]
    b_pre = pb[3]

    if not a_pre and not b_pre:
        return 0
    if not a_pre:
        return 1
    if not b_pre:
        return -1
    return _compare_pre(a_pre, b_pre)

def sort_versions(versions: list[str]) -> list[str]:
    for v in versions:
        _parse(v)
    return sorted(versions, key=cmp_to_key(compare))
