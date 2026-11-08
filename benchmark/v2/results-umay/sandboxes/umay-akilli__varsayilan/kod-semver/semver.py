"""
Semantic Versioning 2.0.0 implementation.
"""
import re
from typing import List, Tuple, Union


class Version:
    """Parsed semantic version."""
    __slots__ = ('major', 'minor', 'patch', 'prerelease', 'build')

    def __init__(self, major: int, minor: int, patch: int,
                 prerelease: Tuple[str, ...], build: Tuple[str, ...]):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch, self.prerelease) == \
               (other.major, other.minor, other.patch, other.prerelease)

    def __lt__(self, other: 'Version') -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        # Compare major, minor, patch
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        # Compare prerelease: empty prerelease > any prerelease
        if not self.prerelease and not other.prerelease:
            return False
        if not self.prerelease:
            return False  # release > prerelease
        if not other.prerelease:
            return True   # prerelease < release
        # Both have prerelease: compare identifier by identifier
        return _compare_prerelease(self.prerelease, other.prerelease) < 0

    def __le__(self, other: 'Version') -> bool:
        return self == other or self < other

    def __gt__(self, other: 'Version') -> bool:
        return not (self <= other)

    def __ge__(self, other: 'Version') -> bool:
        return not (self < other)


def _compare_prerelease(a: Tuple[str, ...], b: Tuple[str, ...]) -> int:
    """Compare two prerelease identifier tuples.
    Returns -1 if a < b, 0 if equal, 1 if a > b."""
    for ai, bi in zip(a, b):
        a_is_num = ai.isdigit()
        b_is_num = bi.isdigit()
        if a_is_num and b_is_num:
            # Numeric identifiers compared numerically
            ai_num = int(ai)
            bi_num = int(bi)
            if ai_num != bi_num:
                return -1 if ai_num < bi_num else 1
        elif a_is_num:
            # Numeric identifiers have lower precedence than non-numeric
            return -1
        elif b_is_num:
            return 1
        else:
            # Both non-numeric: ASCII sort
            if ai != bi:
                return -1 if ai < bi else 1
    # All compared equal so far; shorter tuple has lower precedence
    if len(a) != len(b):
        return -1 if len(a) < len(b) else 1
    return 0


def _parse_version(version: str) -> Version:
    """Parse a version string into a Version object.
    Raises ValueError for invalid versions."""
    if not isinstance(version, str):
        raise ValueError(f"Version must be a string, got {type(version).__name__}")
    
    original = version
    
    # Reject leading/trailing whitespace
    if version != version.strip():
        raise ValueError(f"Version string has leading/trailing whitespace: {original!r}")
    
    if not version:
        raise ValueError("Empty version string")
    
    # Optional leading 'v'
    if version.startswith('v') or version.startswith('V'):
        version = version[1:]
    
    # Split build metadata
    if '+' in version:
        version, build_str = version.split('+', 1)
        build = tuple(build_str.split('.'))
        if not build_str or any(not _is_valid_identifier(b) for b in build):
            raise ValueError(f"Invalid build metadata in: {original}")
    else:
        build = ()
    
    # Split prerelease
    if '-' in version:
        version, prerelease_str = version.split('-', 1)
        prerelease = tuple(prerelease_str.split('.'))
        if not prerelease_str or any(not _is_valid_identifier(p) for p in prerelease):
            raise ValueError(f"Invalid prerelease in: {original}")
    else:
        prerelease = ()
    
    # Parse core version: MAJOR.MINOR.PATCH
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version core (expected MAJOR.MINOR.PATCH): {original}")
    
    try:
        major = _parse_numeric_identifier(parts[0], "major")
        minor = _parse_numeric_identifier(parts[1], "minor")
        patch = _parse_numeric_identifier(parts[2], "patch")
    except ValueError as e:
        raise ValueError(f"Invalid version core in {original}: {e}")
    
    return Version(major, minor, patch, prerelease, build)


def _parse_numeric_identifier(s: str, name: str) -> int:
    """Parse a numeric identifier (MAJOR, MINOR, PATCH).
    Must be non-negative integer with no leading zeros (except '0')."""
    if not s:
        raise ValueError(f"{name} is empty")
    if not s.isdigit():
        raise ValueError(f"{name} must be numeric: {s}")
    if len(s) > 1 and s[0] == '0':
        raise ValueError(f"{name} has leading zeros: {s}")
    return int(s)


def _is_valid_identifier(s: str) -> bool:
    """Check if a prerelease or build identifier is valid.
    Must contain only ASCII alphanumerics and hyphen, and not be empty.
    Numeric identifiers must not have leading zeros."""
    if not s:
        return False
    # ASCII alphanumerics and hyphen only
    if not all(c.isalnum() or c == '-' for c in s):
        return False
    # Numeric identifiers must not have leading zeros
    if s.isdigit() and len(s) > 1 and s[0] == '0':
        return False
    return True


def compare(a: str, b: str) -> int:
    """Compare two semantic version strings.
    
    Args:
        a: First version string.
        b: Second version string.
    
    Returns:
        -1 if a < b, 0 if a == b, 1 if a > b.
    
    Raises:
        ValueError: If either version string is invalid.
    """
    va = _parse_version(a)
    vb = _parse_version(b)
    
    if va < vb:
        return -1
    elif va > vb:
        return 1
    return 0


def sort_versions(versions: List[str]) -> List[str]:
    """Sort version strings by precedence (ascending).
    
    Stable sort: versions with equal precedence retain their input order.
    
    Args:
        versions: List of version strings.
    
    Returns:
        New list sorted by precedence.
    
    Raises:
        ValueError: If any version string is invalid.
    """
    if not isinstance(versions, list):
        raise ValueError("versions must be a list")
    
    # Parse all versions, keeping original index for stable sort
    parsed = []
    for idx, v in enumerate(versions):
        parsed.append((_parse_version(v), idx, v))
    
    # Stable sort by version, then by original index
    parsed.sort(key=lambda x: (x[0], x[1]))
    
    return [v for _, _, v in parsed]


if __name__ == "__main__":
    # Basic sanity tests
    test_versions = [
        "1.0.0",
        "2.0.0",
        "1.1.0",
        "1.0.1",
        "1.0.0-alpha",
        "1.0.0-alpha.1",
        "1.0.0-alpha.beta",
        "1.0.0-beta",
        "1.0.0-beta.2",
        "1.0.0-beta.11",
        "1.0.0-rc.1",
        "1.0.0",
    ]
    print("Sorted:")
    for v in sort_versions(test_versions):
        print(f"  {v}")
    
    print("\nComparisons:")
    print(f"compare('1.0.0', '2.0.0') = {compare('1.0.0', '2.0.0')}")
    print(f"compare('1.0.0', '1.0.0') = {compare('1.0.0', '1.0.0')}")
    print(f"compare('2.0.0', '1.0.0') = {compare('2.0.0', '1.0.0')}")
    print(f"compare('1.0.0-alpha', '1.0.0') = {compare('1.0.0-alpha', '1.0.0')}")
    print(f"compare('1.0.0-alpha.1', '1.0.0-alpha.beta') = {compare('1.0.0-alpha.1', '1.0.0-alpha.beta')}")
    print(f"compare('1.0.0-beta.2', '1.0.0-beta.11') = {compare('1.0.0-beta.2', '1.0.0-beta.11')}")
    print(f"compare('v1.2.3', '1.2.3') = {compare('v1.2.3', '1.2.3')}")
    print(f"compare('1.0.0+build.1', '1.0.0+build.2') = {compare('1.0.0+build.1', '1.0.0+build.2')}")
    
    # Test invalid versions
    print("\nInvalid version tests:")
    for invalid in ["", "1.2", "1.2.3.4", "01.2.3", "1.02.3", "1.2.03",
                    "1.0.0-", "1.0.0+\n", "1.0.0-alpha..1", "v", "1.0.0-alpha.1 "]:
        try:
            compare(invalid, "1.0.0")
            print(f"  FAIL: '{invalid}' should have raised")
        except ValueError as e:
            print(f"  OK: '{invalid}' -> {e}")
