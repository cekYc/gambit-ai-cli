import time
import functools


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
        isabet = iska = 0

        @functools.wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska
            
            # Hashlenebilirlik kontrolü
            try:
                # kwargs sırasından bağımsız anahtar oluştur
                anahtar = (args, tuple(sorted(kwargs.items())))
                hash(anahtar)
            except TypeError:
                # Hashlenemeyen argüman -> önbelleğe almadan çalıştır
                iska += 1
                return f(*args, **kwargs)

            # Önbellekte var mı ve geçerli mi?
            if anahtar in onbellek:
                deger, zaman = onbellek[anahtar]
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger
                # TTL dolmuş -> silip yeniden hesapla
                del onbellek[anahtar]

            # Önbellekte yok veya geçersiz
            iska += 1
            deger = f(*args, **kwargs)
            onbellek[anahtar] = (deger, saat())
            return deger

        def temizle():
            onbellek.clear()

        def bilgi():
            return {"isabet": isabet, "iska": iska}

        sarmal.temizle = temizle
        sarmal.bilgi = bilgi
        return sarmal
    return dekorator
