import re
from typing import List, Tuple, Union


class Version:
    """SemVer 2.0.0 sürümünü temsil eden sınıf."""
    
    def __init__(self, version_str: str):
        self.original = version_str
        self.major: int
        self.minor: int
        self.patch: int
        self.prerelease: List[Union[int, str]]
        self.build: List[str]
        self._parse(version_str)
    
    def _parse(self, version_str: str) -> None:
        """SemVer 2.0.0 formatında sürüm metnini ayrıştır."""
        if not isinstance(version_str, str):
            raise ValueError(f"Geçersiz sürüm: {version_str}")
        
        # Baştaki 'v' karakterini kaldır
        if version_str.startswith('v') or version_str.startswith('V'):
            version_str = version_str[1:]
        
        if not version_str:
            raise ValueError(f"Geçersiz sürüm: {self.original}")
        
        # Derleme bilgisini ayır (+)
        if '+' in version_str:
            core, build_str = version_str.split('+', 1)
            self.build = build_str.split('.')
            if not self.build or any(not self._is_valid_build_identifier(b) for b in self.build):
                raise ValueError(f"Geçersiz sürüm: {self.original}")
            # Derleme kimliklerinde sayısal olanlarda baştaki sıfır kontrolü
            for b in self.build:
                if b.isdigit() and len(b) > 1 and b.startswith('0'):
                    raise ValueError(f"Geçersiz sürüm: {self.original}")
        else:
            core = version_str
            self.build = []
        
        # Ön sürüm bilgisini ayır (-)
        if '-' in core:
            version_core, prerelease_str = core.split('-', 1)
            self.prerelease = prerelease_str.split('.')
            # Ön sürüm kimliklerini işle (sayısal olanları int'e çevir)
            processed_prerelease = []
            for ident in self.prerelease:
                if not ident:
                    raise ValueError(f"Geçersiz sürüm: {self.original}")
                if self._is_numeric_identifier(ident):
                    # Baştaki sıfır kontrolü
                    if len(ident) > 1 and ident.startswith('0'):
                        raise ValueError(f"Geçersiz sürüm: {self.original}")
                    processed_prerelease.append(int(ident))
                elif self._is_valid_prerelease_identifier(ident):
                    processed_prerelease.append(ident)
                else:
                    raise ValueError(f"Geçersiz sürüm: {self.original}")
            self.prerelease = processed_prerelease
        else:
            version_core = core
            self.prerelease = []
        
        # Ana sürüm numarasını ayrıştır (MAJOR.MINOR.PATCH)
        parts = version_core.split('.')
        if len(parts) != 3:
            raise ValueError(f"Geçersiz sürüm: {self.original}")
        
        try:
            self.major = int(parts[0])
            self.minor = int(parts[1])
            self.patch = int(parts[2])
        except ValueError:
            raise ValueError(f"Geçersiz sürüm: {self.original}")
        
        # Baştaki sıfır kontrolü (0 hariç)
        for name, value in [('major', self.major), ('minor', self.minor), ('patch', self.patch)]:
            part_str = parts[{'major': 0, 'minor': 1, 'patch': 2}[name]]
            if len(part_str) > 1 and part_str.startswith('0'):
                raise ValueError(f"Geçersiz sürüm: {self.original}")
        
        if self.major < 0 or self.minor < 0 or self.patch < 0:
            raise ValueError(f"Geçersiz sürüm: {self.original}")
    
    def _is_numeric_identifier(self, ident: str) -> bool:
        """Sadece rakamlardan oluşuyor mu?"""
        return ident.isdigit()
    
    def _is_valid_prerelease_identifier(self, ident: str) -> bool:
        """Geçerli ön sürüm kimliği mi? (ASCII alfanümerik ve tire)"""
        return bool(re.match(r'^[0-9A-Za-z-]+$', ident))
    
    def _is_valid_build_identifier(self, ident: str) -> bool:
        """Geçerli derleme kimliği mi? (ASCII alfanümerik ve tire)"""
        return bool(re.match(r'^[0-9A-Za-z-]+$', ident))
    
    def __lt__(self, other: 'Version') -> bool:
        return self._compare(other) < 0
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._compare(other) == 0
    
    def _compare(self, other: 'Version') -> int:
        """SemVer 2.0.0 kurallarına göre karşılaştır."""
        # MAJOR, MINOR, PATCH karşılaştırması
        for self_val, other_val in [(self.major, other.major), (self.minor, other.minor), (self.patch, other.patch)]:
            if self_val < other_val:
                return -1
            elif self_val > other_val:
                return 1
        
        # Ön sürüm karşılaştırması
        # Ön sürümü olmayan sürüm, ön sürümü olan sürümden daha büyüktür
        if not self.prerelease and not other.prerelease:
            return 0
        if not self.prerelease:
            return 1  # self daha büyük (kararlı sürüm)
        if not other.prerelease:
            return -1  # other daha büyük (kararlı sürüm)
        
        # Her iki sürümde de ön sürüm var, kimlik kimlik karşılaştır
        for i in range(max(len(self.prerelease), len(other.prerelease))):
            if i >= len(self.prerelease):
                return -1  # self daha kısa, dolayısıyla daha küçük
            if i >= len(other.prerelease):
                return 1  # other daha kısa, dolayısıyla self daha büyük
            
            self_id = self.prerelease[i]
            other_id = other.prerelease[i]
            
            # Sayısal kimlikler her zaman alfasayısal kimliklerden küçüktür
            self_is_num = isinstance(self_id, int)
            other_is_num = isinstance(other_id, int)
            
            if self_is_num and other_is_num:
                if self_id < other_id:
                    return -1
                elif self_id > other_id:
                    return 1
            elif self_is_num and not other_is_num:
                return -1  # sayısal < alfasayısal
            elif not self_is_num and other_is_num:
                return 1  # alfasayısal > sayısal
            else:
                # Her ikisi de string, ASCII sıralaması
                if self_id < other_id:
                    return -1
                elif self_id > other_id:
                    return 1
        
        return 0


def compare(a: str, b: str) -> int:
    """
    İki SemVer sürümünü karşılaştır.
    
    Args:
        a: İlk sürüm metni
        b: İkinci sürüm metni
    
    Returns:
        -1: a < b
         0: a == b (öncelik olarak eşit)
         1: a > b
    
    Raises:
        ValueError: Geçersiz sürüm formatında
    """
    version_a = Version(a)
    version_b = Version(b)
    return version_a._compare(version_b)


def sort_versions(versions: List[str]) -> List[str]:
    """
    Sürüm listesini SemVer 2.0.0 öncelik kurallarına göre artan sırada sırala.
    Eşit öncelikli sürümler girdideki sıralarını korur (stable sort).
    
    Args:
        versions: Sürüm metinleri listesi
    
    Returns:
        Sıralanmış yeni liste
    
    Raises:
        ValueError: Geçersiz sürüm formatında
    """
    # Her sürüm için (Version nesnesi, orijinal indeks, orijinal string) tuple'ı oluştur
    version_objects = []
    for idx, v_str in enumerate(versions):
        version_obj = Version(v_str)
        version_objects.append((version_obj, idx, v_str))
    
    # Stable sort: önce Version'a göre, sonra orijinal indekse göre
    version_objects.sort(key=lambda x: (x[0], x[1]))
    
    return [v[2] for v in version_objects]
