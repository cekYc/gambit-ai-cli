import time
import functools
import inspect


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
        onbellek = {}
        isabet = 0
        iska = 0
        sig = inspect.signature(f)

        @functools.wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska
            try:
                # Tüm argümanları isimli (keyword) formuna bağla
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                # Sırasız keyword argümanları tuple'ı (sıralı)
                anahtar = tuple(sorted(bound.arguments.items()))
                hash(anahtar)  # hashlene bilirlik testi
            except TypeError:
                # Hashlenemez argüman (ör. liste) -> önbelleksiz çalıştır
                iska += 1
                return f(*args, **kwargs)

            if anahtar in onbellek:
                deger, zaman = onbellek[anahtar]
                if ttl is None or saat() - zaman <= ttl:  # tam ttl anında hâlâ geçerli
                    isabet += 1
                    return deger
                # TTL dolmuş, silip yeniden hesapla
                del onbellek[anahtar]

            iska += 1
            deger = f(*args, **kwargs)
            onbellek[anahtar] = (deger, saat())
            return deger

        def temizle():
            nonlocal isabet, iska
            onbellek.clear()
            isabet = 0
            iska = 0

        def bilgi():
            return {"isabet": isabet, "iska": iska}

        sarmal.temizle = temizle
        sarmal.bilgi = bilgi
        return sarmal
    return dekorator
