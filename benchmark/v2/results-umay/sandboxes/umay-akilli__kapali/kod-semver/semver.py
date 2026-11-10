import re
from typing import List

# Regex pattern for SemVer 2.0.0
# Matches: optional 'v', major.minor.patch, optional pre-release, optional build metadata
SEMVER_PATTERN = re.compile(
    r'^v?(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
    r'(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
)


def _parse_identifier(identifier: str):
    """Parse a pre-release identifier into a comparable tuple.
    Returns (sort_key, value) where sort_key ensures numeric < alphanumeric."""
    if identifier.isdigit():
        # Numeric identifiers have lower precedence: use 0 as sort key
        return (0, int(identifier))
    # Alphanumeric identifiers have higher precedence: use 1 as sort key
    return (1, identifier)


def _parse_version(version: str):
    """Parse a version string and return comparable components."""
    match = SEMVER_PATTERN.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Invalid version: {version}")
    
    major = int(match.group('major'))
    minor = int(match.group('minor'))
    patch = int(match.group('patch'))
    
    prerelease_str = match.group('prerelease')
    if prerelease_str is None:
        # Release versions have higher precedence than any pre-release.
        # Identifiers are (0, int) for numeric, (1, str) for alphanumeric.
        # Use (2, '') as sentinel that compares greater than any valid identifier.
        prerelease = ((2, ''),)
    else:
        prerelease = tuple(_parse_identifier(part) for part in prerelease_str.split('.'))
    
    return (major, minor, patch, prerelease)


def compare(a: str, b: str) -> int:
    """Compare two SemVer version strings.
    Returns -1 if a < b, 0 if equal precedence, 1 if a > b."""
    a_parts = _parse_version(a)
    b_parts = _parse_version(b)
    
    if a_parts < b_parts:
        return -1
    if a_parts > b_parts:
        return 1
    return 0


def sort_versions(versions: List[str]) -> List[str]:
    """Sort version strings by precedence (ascending).
    Stable sort preserves original order for equal precedence."""
    # Use enumerate to maintain stable sort for equal versions
    indexed = list(enumerate(versions))
    indexed.sort(key=lambda x: (_parse_version(x[1]), x[0]))
    return [v for _, v in indexed]
