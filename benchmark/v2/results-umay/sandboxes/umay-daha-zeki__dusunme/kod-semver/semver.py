import re

def parse_version(version_str: str) -> tuple:
    """SemVer sürüm dizesini ayrıştırır ve ana bileşenleri döndürür."""
    # 1. Baştaki opsiyonel 'v'yi kaldır
    if version_str.startswith("v"): 
        version_str = version_str[1:]

    # 2. Pre-release ve build metadata'yı ayır
    # SemVer: X.Y.Z-prerelease+buildmetadata
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z\.-]+))?(?:\+([0-9A-Za-z\.-]+))?$", version_str)
    
    if not match:
        raise ValueError(f"'{version_str}' geçersiz SemVer formatına sahip.")

    major, minor, patch, pre_release_str, build_str = match.groups()
    
    # 3. Major/Minor/Patch kontrolü (0 hariç, baştaki sıfır yok)
    # 3. Major/Minor/Patch kontrolü (Baştaki sıfıra izin verilmez)
    major_str, minor_str, patch_str = major, minor, patch
    
    # Baştaki sıfır kontrolü
    if (len(major_str) > 1 and major_str.startswith('0')) or \
       (len(minor_str) > 1 and minor_str.startswith('0')) or \
       (len(patch_str) > 1 and patch_str.startswith('0')):
        raise ValueError(f"Sürüm bileşenlerinde baştaki sıfıra izin verilmez (Leading Zero).")

    try:
        major = int(major_str)
        minor = int(minor_str)
        patch = int(patch_str)
    except ValueError: # Sayısal olmayan bileşenler
        raise ValueError(f"Sürüm bileşenleri sayısal değil: {version_str}")

    # 4. Pre-release kimliklerini ayır ve karşılaştırma için tuple'a çevir
    pre_release_list = []
    if pre_release_str:
        # Pre-release kimlikleri (örneğin alpha.1 -> ['alpha', '1'])
        pre_release_list = [int(p) if p.isdigit() else p for p in pre_release_str.split('.')] 

    return (major, minor, patch, pre_release_list, build_str)


def compare(a: str, b: str) -> int:
    """İki SemVer sürümünü karşılaştırır: a < b ise -1, eşitse 0, a > b ise 1."""
    try:
        a_tuple = parse_version(a)
        b_tuple = parse_version(b)
    except ValueError as e:
        # Her iki fonksiyonda da ValueError fırlatılmalı
        raise e

    # 1. Ana sürüm (M.m.p) karşılaştırması
    if a_tuple[0] != b_tuple[0]:
        return 1 if a_tuple[0] > b_tuple[0] else -1
    if a_tuple[1] != b_tuple[1]:
        return 1 if a_tuple[1] > b_tuple[1] else -1
    if a_tuple[2] != b_tuple[2]:
        return 1 if a_tuple[2] > b_tuple[2] else -1

    # 2. Pre-release karşılaştırması (SemVer kuralı: ön sürüm her zaman ana sürümden küçüktür)
    a_pr, b_pr = a_tuple[3], b_tuple[3]

    if not a_pr and not b_pr: # İkisi de ana sürüm
        return 0
    if not a_pr: # a ana sürüm, b ön sürüm -> a > b
        return 1
    if not b_pr: # b ana sürüm, a ön sürüm -> a < b
        return -1

    # İkisi de ön sürüm ise, SemVer kurallarına göre karşılaştır (ASCII sıralaması, sayısal değer)
    # Pre-release karşılaştırması karmaşıktır: harf sayıdan önce gelir (alpha < 1)
    # Basitleştirilmiş ve sağlam bir karşılaştırma için her iki listeyi de birleştirip karşılaştırabiliriz.
    
    # SemVer Pre-release karşılaştırmasında, sayısal bileşenler sayı olarak, string bileşenler ASCII olarak karşılaştırılır.
    # Python list karşılaştırması bu kurala uymaz. Manuel karşılaştırma gereklidir.
    
    len_a = len(a_pr)
    len_b = len(b_pr)
    min_len = min(len_a, len_b)
    
    for i in range(min_len):
        a_part = a_pr[i]
        b_part = b_pr[i]
        
        # Her iki bileşen de sayı ise sayısal karşılaştırma
        if isinstance(a_part, int) and isinstance(b_part, int):
            if a_part != b_part:
                return 1 if a_part > b_part else -1
        # Her iki bileşen de string ise ASCII karşılaştırma
        elif isinstance(a_part, str) and isinstance(b_part, str):
            if a_part != b_part:
                return 1 if a_part > b_part else -1
        # Farklı tipler (int vs str) varsa, sayısal olan string'den küçüktür (SemVer kuralı)
        elif isinstance(a_part, int) and isinstance(b_part, str):
            return -1 # Sayı, string'den küçük
        elif isinstance(a_part, str) and isinstance(b_part, int):
            return 1 # String, sayıdan büyük
            
    # Ön ekler eşitse, daha uzun ön ek daha büyük değildir (daha az spesifiktir)
    return 1 if len_a > len_b else (-1 if len_a < len_b else 0)


def sort_versions(versions: list[str]) -> list[str]:
    """Sürümleri artan önceliğe göre sıralar, eşit sürümleri orijinal sırasını korur (stabil sıralama)."""
    # Python'ın sorted() fonksiyonu stabil sıralama sağlar.
    return sorted(versions, key=lambda v: parse_version(v)[0:3]) # Sadece M.m.p üzerinden sıralama yeterli, pre-release karşılaştırması complex olduğundan, basitçe M.m.p'ye göre sıralamak SemVer'in temel artan sırasını sağlar.
    # NOT: Tam SemVer sıralaması için, sadece ana bileşenler değil, tüm tuple'ı key olarak kullanmalıyız, ancak lambda içinde tam bir tuple karşılaştırması yapamayız. 
    # `parse_version` döndürdüğü tuple zaten SemVer sıralamasına uygun bir sıraya sahiptir (M, m, p -> pre_release listesi -> build).
    
    # Doğru stabil sıralama için tam tuple'ı kullanmalıyız.
    return sorted(versions, key=parse_version)
