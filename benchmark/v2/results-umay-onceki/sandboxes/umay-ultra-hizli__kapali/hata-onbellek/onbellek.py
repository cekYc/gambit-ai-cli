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

            # Hashlenebilir bir cache anahtarı oluştur: fonksiyon adı + args + sorted kwargs
            try:
                if kwargs:
                    key = (f.__name__, args) + tuple(sorted(kwargs.items()))
                else:
                    key = (f.__name__, args)
            except TypeError:
                # Argümanlar hashlenemez (ör. liste) -> doğrudan çalıştır
                iska += 1
                return f(*args, **kwargs)

            # Anahtar çakışmasını önlemek ve doğru cache ayrımı sağlamak için key kontrolü
            if key in _onbellek:
                deger, zaman = _onbellek[key]
                # TTL kontrolü: geçerli olduğu anda ttl saniye sonra hala geçerlidir
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger
                # TTL dolmuş, tekrar çalıştır
            iska += 1
            deger = f(*args, **kwargs)
            _onbellek[key] = (deger, saat())
            return deger

        sarmal.temizle = lambda: _onbellek.clear()
        sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
        return sarmal
    return dekorator
