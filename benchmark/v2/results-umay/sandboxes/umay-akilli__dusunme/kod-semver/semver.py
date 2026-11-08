"""
Semantic Versioning 2.0.0 implementation.
"""
import re
from typing import List, Tuple, Union


class _Version:
    """Internal parsed version representation."""
    __slots__ = ('major', 'minor', 'patch', 'prerelease', 'build', 'original')

    def __init__(self, major: int, minor: int, patch: int,
                 prerelease: Tuple[str, ...], build: Tuple[str, ...],
                 original: str):
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build
        self.original = original

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Version):
            return NotImplemented
        return (self.major, self.minor, self.patch, self.prerelease) == \
               (other.major, other.minor, other.patch, other.prerelease)

    def __lt__(self, other: '_Version') -> bool:
        # Compare major, minor, patch
        self_core = (self.major, self.minor, self.patch)
        other_core = (other.major, other.minor, other.patch)
        if self_core != other_core:
            return self_core < other_core

        # Core versions equal - compare prerelease
        # Empty prerelease (release) has higher precedence than any prerelease
        if not self.prerelease and not other.prerelease:
            return False  # equal
        if not self.prerelease:
            return False  # release > prerelease
        if not other.prerelease:
            return True   # prerelease < release

        # Both have prerelease - compare identifiers
        for s_id, o_id in zip(self.prerelease, other.prerelease):
            s_num = s_id.isdigit()
            o_num = o_id.isdigit()
            if s_num and o_num:
                # Both numeric - compare as integers
                s_val = int(s_id)
                o_val = int(o_id)
                if s_val != o_val:
                    return s_val < o_val
            elif s_num and not o_num:
                # Numeric < alphanumeric
                return True
            elif not s_num and o_num:
                return False
            else:
                # Both alphanumeric - lexicographic ASCII sort
                if s_id != o_id:
                    return s_id < o_id

        # All compared identifiers equal - shorter prerelease has lower precedence
        return len(self.prerelease) < len(other.prerelease)


def _parse_version(version: str) -> _Version:
    """Parse a version string into _Version. Raises ValueError if invalid."""
    if not isinstance(version, str):
        raise ValueError(f'Version must be a string, got {type(version).__name__}')

    original = version
    version = version.strip()

    if not version:
        raise ValueError('Empty version string')

    # Optional leading 'v'
    if version.startswith('v') or version.startswith('V'):
        version = version[1:]

    # Split build metadata
    build_parts = []
    if '+' in version:
        version, build_str = version.split('+', 1)
        if not build_str:
            raise ValueError(f'Empty build metadata in {original!r}')
        build_parts = build_str.split('.')
        for part in build_parts:
            if not part:
                raise ValueError(f'Empty build identifier in {original!r}')
            if not re.fullmatch(r'[0-9A-Za-z-]+', part):
                raise ValueError(f'Invalid build identifier {part!r} in {original!r}')

    # Split prerelease
    prerelease_parts = []
    if '-' in version:
        version, prerelease_str = version.split('-', 1)
        if not prerelease_str:
            raise ValueError(f'Empty prerelease in {original!r}')
        prerelease_parts = prerelease_str.split('.')
        for part in prerelease_parts:
            if not part:
                raise ValueError(f'Empty prerelease identifier in {original!r}')
            if not re.fullmatch(r'[0-9A-Za-z-]+', part):
                raise ValueError(f'Invalid prerelease identifier {part!r} in {original!r}')
            # Check leading zeros for numeric prerelease identifiers
            if part.isdigit() and len(part) > 1 and part[0] == '0':
                raise ValueError(f'Leading zeros in numeric prerelease identifier {part!r} in {original!r}')

    # Parse core version (MAJOR.MINOR.PATCH)
    core_parts = version.split('.')
    if len(core_parts) != 3:
        raise ValueError(f'Invalid core version format in {original!r} (expected MAJOR.MINOR.PATCH)')

    try:
        major = int(core_parts[0])
        minor = int(core_parts[1])
        patch = int(core_parts[2])
    except ValueError:
        raise ValueError(f'Non-numeric core version part in {original!r}')

    # Check leading zeros for core version
    for i, part in enumerate(core_parts):
        if len(part) > 1 and part[0] == '0':
            raise ValueError(f'Leading zeros in core version part {part!r} in {original!r}')

    if major < 0 or minor < 0 or patch < 0:
        raise ValueError(f'Negative version number in {original!r}')

    return _Version(major, minor, patch,
                    tuple(prerelease_parts), tuple(build_parts), original)


def compare(a: str, b: str) -> int:
    """
    Compare two semantic version strings.

    Returns:
        -1 if a < b
         0 if a == b (same precedence)
         1 if a > b

    Raises:
        ValueError: If either version string is invalid.
    """
    va = _parse_version(a)
    vb = _parse_version(b)

    if va < vb:
        return -1
    if vb < va:
        return 1
    return 0


def sort_versions(versions: List[str]) -> List[str]:
    """
    Sort a list of semantic version strings by precedence (ascending).

    Stable sort: versions with equal precedence retain their input order.

    Returns:
        New list with versions sorted by precedence.

    Raises:
        ValueError: If any version string is invalid.
    """
    if not isinstance(versions, list):
        raise ValueError(f'Expected list, got {type(versions).__name__}')

    # Parse all versions first (to validate all before sorting)
    parsed = []
    for i, v in enumerate(versions):
        parsed.append((_parse_version(v), i))

    # Stable sort by version, then by original index
    parsed.sort(key=lambda x: (x[0], x[1]))

    return [v.original for v, _ in parsed]
