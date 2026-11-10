import time
from functools import wraps


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
        _onbellek = {}
        isabet = iska = 0

        @wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska
            try:
                anahtar = (args, tuple(sorted(kwargs.items())))
                hash(anahtar)
            except TypeError:
                iska += 1
                return f(*args, **kwargs)

            if anahtar in _onbellek:
                deger, zaman = _onbellek[anahtar]
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger

            iska += 1
            deger = f(*args, **kwargs)
            _onbellek[anahtar] = (deger, saat())
            return deger

        def temizle():
            _onbellek.clear()

        def bilgi():
            return {"isabet": isabet, "iska": iska}

        sarmal.temizle = temizle
        sarmal.bilgi = bilgi
        return sarmal

    return dekorator