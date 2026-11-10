import re
from functools import cmp_to_key

def parse_version(version_str: str) -> tuple[int, int, int, dict]:
    if version_str.startswith('v'):
        version_str = version_str[1:]

    # Ana SemVer formatı: MAJOR.MINOR.PATCH
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version_str)
    if not match:
        raise ValueError(f"Geçersiz SemVer ana formatı: {version_str}")

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

    # SemVer kuralı: Baştaki sıfıra izin verilmez (0 hariç)
    if (len(match.group(1)) > 1 and match.group(1).startswith('0')) or \
       (len(match.group(2)) > 1 and match.group(2).startswith('0')) or \
       (len(match.group(3)) > 1 and match.group(3).startswith('0')):
        raise ValueError(f"Sürüm bileşenlerinde baştaki sıfır (0 hariç) kullanılamaz: {version_str}")

    # Ön sürüm ve derleme bilgisini ayıkla (sadece varlık kontrolü için basitleştirildi)
    pre_release = {}
    build_metadata = ""

    pre_match = re.search(r"-\w+(\.\d+)*", version_str)
    if pre_match:
        pre_release = {"pre": True}

    build_match = re.search(r"\+\w+(\.\d+)*", version_str)
    if build_match:
        build_metadata = build_match.group(0)[1:]

    return major, minor, patch, pre_release

def compare(a: str, b: str) -> int:
    try:
        major_a, minor_a, patch_a, pre_a = parse_version(a)
        major_b, minor_b, patch_b, pre_b = parse_version(b)
    except ValueError:
        raise ValueError("Karşılaştırılan sürüm metni SemVer kurallarına uymuyor.")

    # Ön sürüm kontrolü: Ön sürüm olmayan her zaman önceliklidir
    if pre_a and not pre_b:
        return -1 # a ön sürüm, b değil -> a < b
    if not pre_a and pre_b:
        return 1  # a değil, b ön sürüm -> a > b

    # Sayısal karşılaştırma
    if major_a != major_b:
        return -1 if major_a < major_b else 1
    if minor_a != minor_b:
        return -1 if minor_a < minor_b else 1
    if patch_a != patch_b:
        return -1 if patch_a < patch_b else 1

    return 0

def sort_versions(versions: list[str]) -> list[str]:
    return sorted(versions, key=cmp_to_key(compare))