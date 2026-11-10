import time
import functools

_onbellek = {}


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
        isabet = iska = 0

        @functools.wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska
            anahtar = args + tuple(sorted(kwargs.items()))
            if ttl is None:
                if anahtar in _onbellek:
                    deger, zaman = _onbellek[anahtar]
                    isabet += 1
                    return deger
            else:
                if anahtar in _onbellek:
                    deger, zaman = _onbellek[anahtar]
                    if saat() - zaman <= ttl:
                        isabet += 1
                        return deger
            iska += 1
            deger = f(*args, **kwargs)
            _onbellek[anahtar] = (deger, saat())
            return deger

        sarmal.temizle = lambda: _onbellek.clear()
        sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
        return sarmal
    return dekorator