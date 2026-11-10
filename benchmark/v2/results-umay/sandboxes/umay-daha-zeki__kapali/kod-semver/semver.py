import re
from functools import cmp_to_key

def parse_version(version_string: str) -> tuple:
    # v öneki isteğe bağlı
    if version_string.startswith('v'):
        version_string = version_string[1:]

    # Kural: Baştaki sıfıra izin verilmez (0 hariç). Yani ilk basamak 1-9 olmalı.
    match = re.match(r"^([1-9]\d*)\.([0-9]+)\.([0-9]+)(?:-([0-9a-zA-Z\.\-]+))?(?:\+([0-9a-zA-Z\.\-]+))?$", version_string)
    
    if not match:
        raise ValueError(f"Geçersiz SemVer formatı: {version_string}. Baştaki sıfıra izin verilmez (0 hariç).")

    major, minor, patch, prerelease, build = match.groups()
    major = int(major)
    minor = int(minor)
    patch = int(patch)

    prerelease_parts = []
    if prerelease:
        prerelease_parts = prerelease.split('.')
        
    return (major, minor, patch, prerelease_parts)

def compare(a: str, b: str) -> int:
    try:
        v_a = parse_version(a)
        v_b = parse_version(b)
    except ValueError as e:
        raise e

    # 1. Ana sayısal karşılaştırma (MAJOR.MINOR.PATCH)
    if v_a[0] != v_b[0]:
        return 1 if v_a[0] > v_b[0] else -1
    if v_a[1] != v_b[1]:
        return 1 if v_a[1] > v_b[1] else -1
    if v_a[2] != v_b[2]:
        return 1 if v_a[2] > v_b[2] else -1

    # 2. Ön sürüm karşılaştırması
    prerelease_a = v_a[3]
    prerelease_b = v_b[3]

    if prerelease_a and not prerelease_b:
        return -1  # Ön sürüm olan daha düşüktür
    if not prerelease_a and prerelease_b:
        return 1   # Ön sürümü olmayan daha yüksektir
    if not prerelease_a and not prerelease_b:
        return 0

    # İkisi de ön sürüm ise, SemVer kurallarına göre karşılaştırılır
    def compare_prerelease_parts(parts_a, parts_b):
        len_a = len(parts_a)
        len_b = len(parts_b)
        for i in range(min(len_a, len_b)):
            part_a = parts_a[i]
            part_b = parts_b[i]
            
            try:
                # Sayısal karşılaştırma
                num_a = int(part_a)
                num_b = int(part_b)
                if num_a != num_b:
                    return 1 if num_a > num_b else -1
            except ValueError:
                # Leksikografik karşılaştırma
                if part_a != part_b:
                    return 1 if part_a > part_b else -1
        
        # Daha az parça daha düşüktür
        return 1 if len_a > len_b else -1

    return compare_prerelease_parts(prerelease_a, prerelease_b)

def sort_versions(versions: list[str]) -> list[str]:
    # Stabil sıralama için cmp_to_key kullanılıyor.
    return sorted(versions, key=cmp_to_key(compare))
