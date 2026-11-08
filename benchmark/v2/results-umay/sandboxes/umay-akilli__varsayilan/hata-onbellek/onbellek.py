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
        onbellek = {}
        isabet = iska = 0

        @wraps(f)
        def sarmal(*args, **kwargs):
            nonlocal isabet, iska
            try:
                # kwargs sırasını önemsiz yapmak için frozenset kullan
                anahtar = (args, frozenset(kwargs.items()))
                hash(anahtar)  # hashlenebilir mi kontrol et
            except TypeError:
                # Hashlenemeyen argüman: önbellek atla, doğrudan çalıştır
                iska += 1
                return f(*args, **kwargs)

            if anahtar in onbellek:
                deger, zaman = onbellek[anahtar]
                # ttl None ise süresiz; ttl varsa zaman farkı <= ttl ise geçerli (eşitlikte de geçerli)
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger
                # süre dolmuş, önbellekten sil ve yeniden hesapla
                del onbellek[anahtar]

            iska += 1
            deger = f(*args, **kwargs)
            onbellek[anahtar] = (deger, saat())
            return deger

        def temizle():
            nonlocal isabet, iska
            onbellek.clear()
            isabet = iska = 0

        def bilgi():
            return {"isabet": isabet, "iska": iska}

        sarmal.temizle = temizle
        sarmal.bilgi = bilgi
        return sarmal
    return dekorator