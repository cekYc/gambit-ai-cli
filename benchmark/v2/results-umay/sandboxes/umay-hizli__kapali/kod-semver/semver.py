import re
from typing import List

_VERSION_RE = re.compile(
    r'^'
    r'v?'
    r'(?P<major>0|[1-9]\d*)'
    r'\.(?P<minor>0|[1-9]\d*)'
    r'\.(?P<patch>0|[1-9]\d*)'
    r'(?:-(?P<pre>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?'
    r'(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?'
    r'$'
)

_NUMERIC_ID = re.compile(r'^[0-9]+$')


def _split_pre(pre: str):
    return pre.split('.')


def _compare_pre_ids(a_id: str, b_id: str) -> int:
    a_is_num = _NUMERIC_ID.match(a_id) is not None
    b_is_num = _NUMERIC_ID.match(b_id) is not None

    if a_is_num and b_is_num:
        a_val = int(a_id)
        b_val = int(b_id)
        return (a_val > b_val) - (a_val < b_val)
    if a_is_num:
        return -1
    if b_is_num:
        return 1
    return (a_id > b_id) - (a_id < b_id)


def _compare_pre(a_pre, b_pre) -> int:
    if a_pre is None and b_pre is None:
        return 0
    if a_pre is None:
        return 1
    if b_pre is None:
        return -1

    a_ids = _split_pre(a_pre)
    b_ids = _split_pre(b_pre)

    for aid, bid in zip(a_ids, b_ids):
        c = _compare_pre_ids(aid, bid)
        if c != 0:
            return c

    return (len(a_ids) > len(b_ids)) - (len(a_ids) < len(b_ids))


def parse(version: str):
    if not isinstance(version, str):
        raise ValueError(f'Geçersiz sürüm: {version!r}')

    m = _VERSION_RE.match(version)
    if not m:
        raise ValueError(f'Geçersiz sürüm: {version!r}')

    major = int(m.group('major'))
    minor = int(m.group('minor'))
    patch = int(m.group('patch'))
    pre = m.group('pre')

    return (major, minor, patch, pre)


def compare(a: str, b: str) -> int:
    a_major, a_minor, a_patch, a_pre = parse(a)
    b_major, b_minor, b_patch, b_pre = parse(b)

    for av, bv in ((a_major, b_major), (a_minor, b_minor), (a_patch, b_patch)):
        if av < bv:
            return -1
        if av > bv:
            return 1

    return _compare_pre(a_pre, b_pre)


def sort_versions(versions: List[str]) -> List[str]:
    if not isinstance(versions, list):
        raise ValueError('versions bir liste olmalıdır')

    parsed = [parse(v) for v in versions]

    indexed = list(enumerate(versions))
    indexed.sort(key=lambda item: parsed[item[0]])
    return [v for _, v in indexed]
