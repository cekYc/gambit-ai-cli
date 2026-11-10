"""Semantic Versioning 2.0.0 implementation."""  

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import List, Tuple, Union


@total_ordering
@dataclass(frozen=True)
class Version:
    """Parsed semantic version."""
    major: int
    minor: int
    patch: int
    prerelease: Tuple[Union[int, str], ...] = ()
    build: Tuple[str, ...] = ()

    @staticmethod
    def parse(version_str: str) -> 'Version':
        """Parse a version string according to SemVer 2.0.0."""
        if not isinstance(version_str, str):
            raise ValueError(f"Version must be a string, got {type(version_str).__name__}")
        
        original = version_str
        version_str = version_str.strip()
        
        if not version_str:
            raise ValueError("Empty version string")
        
        # Remove leading 'v' or 'V'
        if version_str[0] in ('v', 'V'):
            version_str = version_str[1:]
        
        # Split build metadata
        if '+' in version_str:
            core, build_part = version_str.split('+', 1)
            if not build_part:
                raise ValueError(f"Empty build metadata in {original!r}")
            build_identifiers = build_part.split('.')
            if not all(build_identifiers):
                raise ValueError(f"Empty build identifier in {original!r}")
            # Validate build identifiers per SemVer: ASCII alphanumerics and hyphens only
            for bid in build_identifiers:
                if not re.fullmatch(r'[0-9A-Za-z-]+', bid):
                    raise ValueError(f"Invalid build identifier {bid!r} in {original!r}: must be ASCII alphanumerics and hyphens")
            build = tuple(build_identifiers)
        else:
            core = version_str
            build = ()
        
        # Split prerelease
        if '-' in core:
            version_core, prerelease_part = core.split('-', 1)
            prerelease = tuple(_parse_identifiers(prerelease_part))
        else:
            version_core = core
            prerelease = ()
        
        # Parse major.minor.patch
        parts = version_core.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version core {version_core!r} in {original!r}: must be MAJOR.MINOR.PATCH")
        
        major = _parse_numeric_id(parts[0], "major", original)
        minor = _parse_numeric_id(parts[1], "minor", original)
        patch = _parse_numeric_id(parts[2], "patch", original)
        
        return Version(major, minor, patch, prerelease, build)

    def __lt__(self, other: 'Version') -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        # Compare major, minor, patch
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        # Pre-release has lower precedence than release
        if not self.prerelease and not other.prerelease:
            return False  # equal
        if not self.prerelease:
            return False  # release > pre-release
        if not other.prerelease:
            return True   # pre-release < release
        # Compare prerelease identifiers
        return _compare_prerelease(self.prerelease, other.prerelease) < 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major == other.major and 
                self.minor == other.minor and 
                self.patch == other.patch and 
                self.prerelease == other.prerelease)


def _parse_numeric_id(s: str, name: str, original: str) -> int:
    """Parse a numeric identifier (no leading zeros except '0')."""
    if not s:
        raise ValueError(f"Empty {name} in {original!r}")
    if not s.isdigit():
        raise ValueError(f"Non-numeric {name} {s!r} in {original!r}")
    if len(s) > 1 and s[0] == '0':
        raise ValueError(f"Leading zeros in {name} {s!r} in {original!r}")
    return int(s)


def _parse_identifiers(s: str) -> List[Union[int, str]]:
    """Parse dot-separated prerelease identifiers."""
    if not s:
        raise ValueError("Empty prerelease identifier")
    parts = s.split('.')
    result = []
    for part in parts:
        if not part:
            raise ValueError("Empty prerelease identifier")
        # Numeric identifier: digits only, no leading zeros
        if part.isdigit():
            if len(part) > 1 and part[0] == '0':
                raise ValueError(f"Leading zeros in prerelease numeric identifier {part!r}")
            result.append(int(part))
        else:
            # Alphanumeric identifier: ASCII alphanumerics and hyphen
            if not re.fullmatch(r'[0-9A-Za-z-]+', part):
                raise ValueError(f"Invalid prerelease identifier {part!r}: must be ASCII alphanumerics and hyphens")
            result.append(part)
    return result


def _compare_prerelease(a: Tuple[Union[int, str], ...], b: Tuple[Union[int, str], ...]) -> int:
    """Compare two prerelease identifier tuples. Returns -1, 0, or 1."""
    for i in range(max(len(a), len(b))):
        if i >= len(a):
            return -1  # a has fewer identifiers -> lower precedence
        if i >= len(b):
            return 1   # b has fewer identifiers -> lower precedence
        
        ai, bi = a[i], b[i]
        
        # Numeric identifiers have lower precedence than non-numeric
        if isinstance(ai, int) and isinstance(bi, int):
            if ai < bi:
                return -1
            if ai > bi:
                return 1
        elif isinstance(ai, int) and isinstance(bi, str):
            return -1  # numeric < alphanumeric
        elif isinstance(ai, str) and isinstance(bi, int):
            return 1   # alphanumeric > numeric
        else:
            # Both strings: ASCII sort
            if ai < bi:
                return -1
            if ai > bi:
                return 1
    return 0


def compare(a: str, b: str) -> int:
    """Compare two version strings.
    
    Returns:
        -1 if a < b
         0 if a == b (same precedence)
         1 if a > b
    
    Raises:
        ValueError: if either version string is invalid.
    """
    va = Version.parse(a)
    vb = Version.parse(b)
    if va < vb:
        return -1
    if va > vb:
        return 1
    return 0


def sort_versions(versions: list[str]) -> list[str]:
    """Sort version strings by precedence (ascending).
    
    Stable sort: versions with equal precedence keep their input order.
    
    Raises:
        ValueError: if any version string is invalid.
    """
    if not isinstance(versions, list):
        raise ValueError("versions must be a list")
    # Parse all versions first (to validate)
    parsed = [(Version.parse(v), i, v) for i, v in enumerate(versions)]
    # Stable sort by version, then by original index
    parsed.sort(key=lambda x: (x[0], x[1]))
    return [v for _, _, v in parsed]


if __name__ == "__main__":
    # Quick manual tests
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
        "1.0.0+build.1",
        "1.0.0+build.2",
    ]
    print("Sorted:")
    for v in sort_versions(test_versions):
        print(f"  {v}")
    
    print("\nComparisons:")
    print(f"compare('1.0.0', '2.0.0') = {compare('1.0.0', '2.0.0')}")
    print(f"compare('1.0.0-alpha', '1.0.0') = {compare('1.0.0-alpha', '1.0.0')}")
    print(f"compare('1.0.0-alpha.1', '1.0.0-alpha.beta') = {compare('1.0.0-alpha.1', '1.0.0-alpha.beta')}")
    print(f"compare('1.0.0-beta.2', '1.0.0-beta.11') = {compare('1.0.0-beta.2', '1.0.0-beta.11')}")
    print(f"compare('1.0.0+build.1', '1.0.0+build.2') = {compare('1.0.0+build.1', '1.0.0+build.2')}")
