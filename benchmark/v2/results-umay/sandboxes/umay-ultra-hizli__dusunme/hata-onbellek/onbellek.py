import time

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
        # Fonksiyona özel önbellek ve sayaçlar
        cache = {}
        isabet = iska = 0

        def sarmal(*args, **kwargs):
            nonlocal isabet, iska

            # Argümanların hashlenip hashlenemediğini kontrol eden yardımcı fonksiyon
            def is_hashable(obj):
                return isinstance(obj, (tuple, int, str, float, bool, type(None)))
            
            # Argümanları hashable formata dönüştürme ve anahtar oluşturma
            try:
                # Konumsal argümanların içindeki listeleri/setleri tuple'a dönüştür
                hashable_args = tuple(tuple(arg) if isinstance(arg, (list, set)) else arg for arg in args)
                # İsimli argümanları sıralı tuple'a dönüştür (sıra önemsizliği sağlamak için)
                hashable_kwargs = tuple(sorted((k, tuple(v) if isinstance(v, (list, set)) else v) for k, v in kwargs.items()))
                key = hashable_args + hashable_kwargs
            except TypeError:
                # Hashlenemeyen argümanlar varsa önbelleğe almadan doğrudan çalıştır
                return f(*args, **kwargs)

            if key in cache:
                deger, zaman = cache[key]
                # TTL kontrolü: ttl geçtikten SONRA geçersiz olur (tam ttl anında geçerlidir)
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger
                else:
                    # TTL dolmuşsa önbellekten kaldır ve yeniden çalıştır
                    del cache[key]

            # Önbellekte yok veya TTL dolmuş
            iska += 1
            deger = f(*args, **kwargs)
            cache[key] = (deger, saat())
            return deger

        # Dekorasyonlanmış fonksiyon nesnesine metotları ekleme
        sarmal.temizle = cache.clear
        sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
        
        # Orijinal fonksiyonun adını ve docstring'ini koruma
        sarmal.__name__ = f.__name__
        sarmal.__doc__ = f.__doc__

        return sarmal

    return dekorator