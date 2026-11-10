import time
import functools
import hashlib

def _hashable(item):
    # Liste gibi hashlenemeyen tipleri tuple'a dönüştürerek hashlenabilir hale getirir
    if isinstance(item, list):
        return tuple(item)
    return item

def onbellekle(ttl=None, saat=time.monotonic):
    """Fonksiyon sonuçlarını argümanlarına göre önbelleğe alan dekoratör.

    - Aynı argümanlarla (konumsal ve isimli; isimli argümanların yazılış sırası önemsiz) yapılan çağrılar
      fonksiyonu yeniden çalıştırmaz.
    - ttl (saniye) verilirse kayıt eklendiği andan ttl saniye geçtikten SONRA geçersiz olur (tam ttl anında
      hâlâ geçerlidir); geçersiz kayıt için fonksiyon yeniden çalıştırılır.
    - Her dekore edilen fonksiyonun önbelleği ayrıdır.
    - Hashlenemeyen argümanlarla (ör. liste) yapılan çağrılar önbelleğe alınmadan doğrudan çalıştırılır.
    - Sarılan fonksiyon adını ve docstring'ini korur. `temizle()` yalnızca kendi önbelleğini boşaltır;
      `bilgi()` {"isabet": n, "iska": m} döndürür (iska: fonksiyonun gerçekten çalıştırıldığı çağrılar).
    """
    def dekorator(f):
        # Her fonksiyon için özel durum tutucular
        cache = {}
        isabet = 0
        iska = 0

        @functools.wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska

            # Argümanları standardize etme: İsimli argümanları sırala ve hashlenabilir hale getir
            sorted_kwargs = tuple(sorted(kwargs.items()))
            
            # Anahtar: (args, sorted_kwargs)
            key = (_hashable(args), sorted_kwargs)

            if key in cache:
                deger, zaman = cache[key]
                # TTL kontrolü: saat() - zaman > ttl ise geçersiz demektir
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger
                else:
                    # TTL süresi dolmuş, kaydı kaldır ve yeniden çalıştır
                    del cache[key]
            
            iska += 1
            
            # Hashlenemeyen argüman kontrolü (basitleştirildi: liste varsa önbelleğe almayı atlar)
            if any(isinstance(arg, list) for arg in args) or any(isinstance(v, list) for v in kwargs.values()):
                return f(*args, **kwargs)

            # Fonksiyonu çalıştır ve önbelleğe al
            deger = f(*args, **kwargs)
            cache[key] = (deger, saat())
            return deger

        # Özel metotlar ekleme
        sarmal.temizle = cache.clear
        sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
        return sarmal
    return dekorator