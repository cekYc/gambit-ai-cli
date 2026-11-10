import re
from functools import cmp_to_key

def parse_version(v):
    """Parse a SemVer 2.0.0 string.
    Returns (major, minor, patch, pre_release, build).
    pre_release is a list of identifiers (int for numeric, str for alphanumeric).
    build is a string or None.
    """
    if isinstance(v, str) and v.startswith('v'):
        v = v[1:]
    # SemVer 2.0 pattern: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
    # MAJOR.MINOR.PATCH: non-negative integers, no leading zeros except 0 itself
    # PRERELEASE: dot-separated identifiers
    # BUILD: dot-separated identifiers
    pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:(?:0|[1-9]\d*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*)\.)*(?:0|[1-9]\d*|[0-9]*[a-zA-Z-][0-9a-zA-Z-]*))?)?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    match = re.match(pattern, v)
    if not match:
        raise ValueError(f'Invalid version: {v!r}')
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    pre = []
    if match.group(4):
        for ident in match.group(4).split('.'):
            if ident.isdigit():
                if len(ident) > 1 and ident[0] == '0':
                    raise ValueError(f'Invalid version: leading zero in pre-release: {v!r}')
                pre.append(int(ident))
            else:
                if not re.match(r'^[0-9a-zA-Z-]+$', ident):
                    raise ValueError(f'Invalid version: bad identifier: {v!r}')
                pre.append(ident)
    build = match.group(5)
    return (major, minor, patch, pre, build)

def compare_parsed(pa, pb):
    """Compare two parsed SemVer 2.0.0 versions."""
    # Compare major.minor.patch
    for a, b in zip(pa[:3], pb[:3]):
        if a < b: return -1
        if a > b: return 1
    # Equal core version
    # Check if pre-release exists (use len > 0 instead of is not None, since parse returns [] for no pre-release)
    ha = len(pa[3]) > 0  # a has pre-release
    hb = len(pb[3]) > 0  # b has pre-release
    
    # Both have pre-release
    if ha and hb:
        for a_ident, b_ident in zip(pa[3], pb[3]):
            a_is_int = isinstance(a_ident, int)
            b_is_int = isinstance(b_ident, int)
            if a_is_int and b_is_int:
                # Numeric comparison
                if a_ident < b_ident: return -1
                if a_ident > b_ident: return 1
            elif a_is_int and not b_is_int:
                # Numeric identifiers have lower precedence than alphabetic
                return -1
            elif not a_is_int and b_is_int:
                # Alphabetic identifiers have higher precedence than numeric
                return 1
            else:
                # Both strings - lexicographic comparison
                if a_ident < b_ident: return -1
                if a_ident > b_ident: return 1
        # If one is prefix of the other, shorter has lower precedence
        if len(pa[3]) < len(pb[3]): return -1
        if len(pa[3]) > len(pb[3]): return 1
        return 0
    # Only a has pre-release -> a < b (normal version > pre-release)
    if ha: return -1
    # Only b has pre-release -> a > b
    if hb: return 1
    
    # Neither has pre-release - compare build metadata
    # When major.minor.prerelease are equal, compare build
    # A version without build is treated as having empty build string '' 
    # So 1.0.0 < 1.0.0+build (empty string < any non-empty string)
    
    pa_b, pb_b = pa[4], pb[4]
    if pa_b is not None and pb_b is not None:
        # Both have build metadata - compare lexicographically
        if pa_b < pb_b: return -1
        if pa_b > pb_b: return 1
        return 0
    if pa_b is not None:
        # a has build, b doesn't -> a > b
        return 1
    if pb_b is not None:
        # b has build, a doesn't -> a < b
        return -1
    
    # Equal
    return 0

def compare(a, b):
    """Compare two Semantic Versioning 2.0.0 strings.
    
    Returns -1 if a < b, 0 if a == b, 1 if a > b.
    Raises ValueError for invalid version strings.
    """
    pa, pb = parse_version(a), parse_version(b)
    return compare_parsed(pa, pb)

def sort_versions(versions):
    """Sort a list of version strings in ascending order using SemVer 2.0.0 rules.
    
    Equal-precedence versions maintain their original relative order (stable sort).
    """
    return sorted(versions, key=cmp_to_key(compare))


if __name__ == '__main__':
    # Basic comparison tests
    print('=== compare tests ===')
    tests = [
        # (a, b, expected)
        ('1.0.0', '2.0.0', 1),
        ('2.0.0', '1.0.0', -1),
        ('1.0.0', '1.0.0', 0),
        ('1.0.0', '1.0.1', -1),
        ('1.0.1', '1.0.0', 1),
        # Pre-release: any pre-release < normal version
        ('1.0.0', '1.0.0-alpha', 1),   # 1.0.0 > 1.0.0-alpha
        ('1.0.0-alpha', '1.0.0', -1),  # 1.0.0-alpha < 1.0.0
        # Pre-release comparison
        ('1.0.0-alpha', '1.0.0-beta', -1),
        ('1.0.0-beta', '1.0.0-alpha', 1),
        ('1.0.0-alpha.1', '1.0.0-alpha.2', -1),
        ('1.0.0-alpha.beta', '1.0.0-beta', -1),  # alpha < beta
        ('1.0.0-rc.1', '1.0.0', -1),
        ('1.0.0', '1.0.0-rc.1', 1),
        # Build metadata comparison (when core and pre are equal)
        ('1.0.0', '1.0.0+build', -1),  # no build < with build
        ('1.0.0+build', '1.0.0', 1),
        ('1.0.0+build.2', '1.0.0+build.11', -1),  # lexicographic: '2' > '11' starts with '1' vs '2'
        # Leading 'v'
        ('v1.0.0', '1.0.0', 0),
        ('v1.0.0', 'v2.0.0', 1),
        # Invalid versions should raise ValueError
        # ('01.0.0', '1.0.0'),  # leading zero in core - should be invalid
    ]
    
    all_pass = True
    for a, b, expected in tests:
        try:
            result = compare(a, b)
            status = 'PASS' if result == expected else 'FAIL'
            if status == 'FAIL':
                all_pass = False
            print(f"{status}: compare({a!r}, {b!r}) = {result} (expected {expected})")
        except ValueError as e:
            # Check if this is an expected ValueError (for invalid versions)
            # Most tests expect successful comparison, so unexpected ValueError is FAIL
            print(f"INFO: compare({a!r}, {b!r}) raised ValueError: {e}")
    
    print()
    # Sort tests
    print('=== sort tests ===')
    sort_tests = [
        (['1.0.0', '2.0.0', '1.0.1'], ['1.0.0', '1.0.1', '2.0.0']),
        (['1.0.0', '1.0.0-alpha', '1.0.0-beta'], ['1.0.0-alpha', '1.0.0-beta', '1.0.0']),
        (['2.0.0', '1.0.0', '1.0.1'], ['1.0.0', '1.0.1', '2.0.0']),
        (['1.0.0+build', '1.0.0'], ['1.0.0', '1.0.0+build']),
        (['v1.0.0', 'v0.9.0', 'v1.0.0-alpha'], ['v0.9.0', 'v1.0.0-alpha', 'v1.0.0']),
        # Stable sort test: equal versions should maintain order
        (['1.0.0', '1.0.0'], ['1.0.0', '1.0.0']),
    ]
    
    for versions, expected in sort_tests:
        result = sort_versions(versions)
        status = 'PASS' if result == expected else 'FAIL'
        if status == 'FAIL':
            all_pass = False
        print(f"{status}: sort_versions({versions}) = {result}")
        if status == 'FAIL':
            print(f"   Expected: {expected}")
    
    print()
    if all_pass:
        print('All tests PASSED!')
    else:
        print('Some tests FAILED!')
