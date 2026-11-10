import re
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


@dataclass(frozen=True, order=True)
class Identifier:
    """SemVer identifier with natural ordering."""
    is_numeric: bool
    value: Union[int, str]

    @staticmethod
    def parse(token: str) -> "Identifier":
        if token.isdigit():
            # Leading zeros not allowed for numeric identifiers
            if len(token) > 1 and token[0] == '0':
                raise ValueError(f"Invalid numeric identifier with leading zeros: {token}")
            return Identifier(True, int(token))
        # Alphanumeric + hyphen, ASCII only
        if not re.fullmatch(r'[0-9A-Za-z-]+', token):
            raise ValueError(f"Invalid alphanumeric identifier: {token}")
        return Identifier(False, token)

    def __lt__(self, other: "Identifier") -> bool:
        if not isinstance(other, Identifier):
            return NotImplemented
        if self.is_numeric != other.is_numeric:
            # Numeric identifiers always have lower precedence than non-numeric
            return self.is_numeric
        if self.is_numeric:
            return self.value < other.value
        return self.value < other.value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Identifier):
            return NotImplemented
        return self.is_numeric == other.is_numeric and self.value == other.value


@dataclass(frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: Tuple[Identifier, ...]
    build: Tuple[str, ...]

    @staticmethod
    def parse(version_str: str) -> "Version":
        if not version_str:
            raise ValueError("Empty version string")
        
        # Optional leading 'v'
        if version_str.startswith('v') or version_str.startswith('V'):
            version_str = version_str[1:]
        
        # Split build metadata
        build_part = ()
        if '+' in version_str:
            version_str, build_str = version_str.split('+', 1)
            if not build_str:
                raise ValueError("Empty build metadata")
            build_identifiers = build_str.split('.')
            for ident in build_identifiers:
                if not ident:
                    raise ValueError("Empty build identifier")
                if not re.fullmatch(r'[0-9A-Za-z-]+', ident):
                    raise ValueError(f"Invalid build identifier: {ident}")
            build_part = tuple(build_identifiers)
        
        # Split prerelease
        prerelease_part = ()
        if '-' in version_str:
            version_str, prerelease_str = version_str.split('-', 1)
            if not prerelease_str:
                raise ValueError("Empty prerelease")
            prerelease_idents = prerelease_str.split('.')
            prerelease_part = tuple(Identifier.parse(ident) for ident in prerelease_idents)
        
        # Parse core version
        core_parts = version_str.split('.')
        if len(core_parts) != 3:
            raise ValueError(f"Invalid core version format: {version_str}")
        
        def parse_core(part: str, name: str) -> int:
            if not part.isdigit():
                raise ValueError(f"{name} must be numeric: {part}")
            if len(part) > 1 and part[0] == '0':
                raise ValueError(f"{name} has leading zeros: {part}")
            return int(part)
        
        major = parse_core(core_parts[0], "Major")
        minor = parse_core(core_parts[1], "Minor")
        patch = parse_core(core_parts[2], "Patch")
        
        return Version(major, minor, patch, prerelease_part, build_part)

    def __lt__(self, other: "Version") -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        # Compare core version
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        
        # Core versions equal, compare prerelease
        # A version without prerelease has higher precedence than one with
        if not self.prerelease and not other.prerelease:
            return False  # Equal
        if not self.prerelease:
            return False  # self is release, other is prerelease -> self > other
        if not other.prerelease:
            return True   # self is prerelease, other is release -> self < other
        
        # Both have prerelease, compare identifiers left to right
        for a, b in zip(self.prerelease, other.prerelease):
            if a != b:
                return a < b
        # All compared identifiers equal, longer prerelease has higher precedence
        return len(self.prerelease) < len(other.prerelease)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (
            self.major == other.major and
            self.minor == other.minor and
            self.patch == other.patch and
            self.prerelease == other.prerelease
            # build metadata is ignored for precedence
        )


def compare(a: str, b: str) -> int:
    """
    Compare two semantic version strings.
    Returns -1 if a < b, 0 if equal precedence, 1 if a > b.
    Raises ValueError for invalid version strings.
    """
    va = Version.parse(a)
    vb = Version.parse(b)
    if va < vb:
        return -1
    if va == vb:
        return 0
    return 1


def sort_versions(versions: List[str]) -> List[str]:
    """
    Sort version strings by precedence (ascending).
    Equal precedence versions maintain their input order (stable sort).
    Raises ValueError for any invalid version string.
    """
    # Use enumerate to maintain stability for equal elements
    indexed = [(Version.parse(v), i, v) for i, v in enumerate(versions)]
    indexed.sort(key=lambda x: (x[0], x[1]))
    return [v for _, _, v in indexed]
