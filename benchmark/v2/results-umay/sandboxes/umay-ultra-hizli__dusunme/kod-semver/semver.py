import re

def parse_version(version_string: str):
    """SemVer dizesini ayrıştırır ve doğruluk kontrolü yapar."""
    # 1. 'v' önekini kaldır
    if version_string.startswith('v'):
        version_string = version_string[1:]

    # SemVer RegEx: MAJOR.MINOR.PATCH[-prerelease][+build]
    # Bu regex, SemVer 2.0.0 standartlarına uygunluğu sağlar.
    semver_pattern = re.compile(
        r'^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)'
        r'(?:-(?P<prerelease>[0-9A-Za-z\-\.]+))?'
        r'(?:\+(?P<build>[0-9A-Za-z\-\.]+))?$' # Build kısmı önceliği etkilemez
    )

    match = semver_pattern.match(version_string)
    if not match:
        raise ValueError(f"'{version_string}' geçerli bir Semantic Versioning (SemVer 2.0.0) formatında değildir.")

    data = match.groupdict()
    
    # Pre-release etiketlerini sayısal/leksikografik olarak karşılaştırılabilir bir tuple'a dönüştür
    prerelease_parts = []
    if data['prerelease']: 
        # SemVer'de ayrıştırıcılar '.' ile ayrılır
        prerelease_identifiers = data['prerelease'].split('.')
        for identifier in prerelease_identifiers:
            try:
                # Sayısal ise integer olarak kaydet (Örn: '1' -> 1)
                prerelease_parts.append(int(identifier))
            except ValueError:
                # String ise string olarak kaydet (Örn: 'alpha' -> 'alpha')
                prerelease_parts.append(identifier)
                
    return {
        'major': int(data['major']),
        'minor': int(data['minor']),
        'patch': int(data['patch']),
        'prerelease': prerelease_parts,
        'build': data['build'] # Build bilgisi karşılaştırmada kullanılmaz
    }


def compare(a: str, b: str) -> int:
    """İki SemVer dizesini karşılaştırır. a < b ise -1, eşit ise 0, a > b ise 1 döndürür."""
    try:
        data_a = parse_version(a)
        data_b = parse_version(b)
    except ValueError: 
        # Hangi girdinin geçersiz olduğunu bilmek için bu blokta hata yükseltmek daha doğru olur, 
        # ancak talep edilen fonksiyonun sadece compare işlemi yapması beklenir.
        # SemVer doğrulama hatasını dışarıya yayıyoruz.
        raise 

    # 1. Ana sürüm (M.m.p) karşılaştırması
    if data_a['major'] != data_b['major']:
        return 1 if data_a['major'] > data_b['major'] else -1
    if data_a['minor'] != data_b['minor']:
        return 1 if data_a['minor'] > data_b['minor'] else -1
    if data_a['patch'] != data_b['patch']:
        return 1 if data_a['patch'] > data_b['patch'] else -1

    # 2. Ön sürüm karşılaştırması
    prerelease_a = data_a['prerelease']
    prerelease_b = data_b['prerelease']

    # Eğer her ikisi de ön sürüm değilse eşitlerdir (M.m.p eşit olduğu için)
    if not prerelease_a and not prerelease_b:
        return 0

    # Eğer biri ön sürüm, diğeri değilse, ön sürüm daha düşüktür (örn: 1.0.0 > 1.0.0-alpha)
    if not prerelease_a and prerelease_b:
        return 1
    if prerelease_a and not prerelease_b:
        return -1

    # Her ikisi de ön sürüm ise, SemVer kurallarına göre karşılaştır
    # Daha az veya daha basit ön sürüm daha küçüktür.
    len_a = len(prerelease_a)
    len_b = len(prerelease_b)
    
    for i in range(min(len_a, len_b)): # Tüm ortak kısımları karşılaştır
        id_a = prerelease_a[i]
        id_b = prerelease_b[i]

        # Sayısal ve string karşılaştırmasını yap
        if isinstance(id_a, int) and isinstance(id_b, int):
            if id_a < id_b: return -1
            if id_a > id_b: return 1
        elif isinstance(id_a, int) and isinstance(id_b, str):
            # Sayısal değer her zaman string'den küçüktür (örn: 1 < 'alpha')
            return -1
        elif isinstance(id_a, str) and isinstance(id_b, int):
            # String her zaman sayısal değerden büyüktür
            return 1
        elif isinstance(id_a, str) and isinstance(id_b, str):
            if id_a < id_b: return -1
            if id_a > id_b: return 1

    # Ortak kısım eşitse, daha uzun liste daha büyüktür (örn: alpha.1 > alpha)
    if len_a < len_b: return -1
    if len_a > len_b: return 1

    return 0

def sort_versions(versions: list[str]) -> list[str]:
    """SemVer listesini artan önceliğe göre sıralar, eşitler orijinal sırasını korur (stable sort)."""
    
    # Karşılaştırma fonksiyonunu bir key olarak kullanmak için bir wrapper fonksiyonu oluşturuyoruz.
    # functools.cmp_to_key kullanarak compare fonksiyonumuzu Python'un sort() metodunun anlayacağı bir anahtara çeviriyoruz.
    from functools import cmp_to_key
    
    # compare fonksiyonu zaten istenen (-1, 0, 1) formatında olduğu için doğrudan kullanabiliriz.
    return sorted(versions, key=cmp_to_key(compare))
