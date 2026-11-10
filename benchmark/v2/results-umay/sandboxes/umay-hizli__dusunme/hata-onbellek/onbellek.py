import functools
import time


def onbellekle(ttl=None, saat=time.monotonic):
    """Fonksiyon sonuçlarını argümanlara göre önbelleğe alan dekoratör.

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
        _cache = {}
        isabet = iska = 0

        @functools.wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska

            try:
                anahtar = (args, tuple(sorted(kwargs.items())))
                hash(anahtar)
            except TypeError:
                # Hashlenemeyen argüman: önbelleğe alınmadan doğrudan çalıştır.
                return f(*args, **kwargs)

            zaman = saat()
            if anahtar in _cache:
                deger, kayit_zamani = _cache[anahtar]
                if ttl is None or zaman - kayit_zamani <= ttl:
                    isabet += 1
                    return deger

            iska += 1
            deger = f(*args, **kwargs)
            _cache[anahtar] = (deger, saat())
            return deger

        def temizle():
            _cache.clear()

        def bilgi():
            return {"isabet": isabet, "iska": iska}

        sarmal.temizle = temizle
        sarmal.bilgi = bilgi
        return sarmal

    return dekorator