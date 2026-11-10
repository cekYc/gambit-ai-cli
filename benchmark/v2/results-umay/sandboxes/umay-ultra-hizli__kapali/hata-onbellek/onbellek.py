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
    # Her fonksiyon için ayrı bir önbellek ve sayaçlar
    bellek = {}
    isabet = iska = 0

    def sarmal(*args, **kwargs):
        nonlocal isabet, iska
        
        # İsimli argümanları anahtar için standart hale getir (sıra bağımsızlık için)
        # Hashlenemeyen tipler (liste vb.) kontrol edilmeli. Basit tip kontrolü yapılıyor.
        hashlenebilir_kwargs = {k: v for k, v in kwargs.items() if isinstance(v, (tuple, str, int, float, bool))}
        
        # Anahtar: Sıralanmış konumsal argümanlar + Sıralanmış ve standartlaştırılmış isimli argümanlar
        anahtar_parts = list(args) + list(sorted(hashlenebilir_kwargs.items()))
        anahtar = tuple(anahtar_parts)

        if anahtar in bellek:
            deger, zaman = bellek[anahtar]
            # TTL kontrolü: ttl geçtikten SONRA geçersiz olmalı, yani saat() - zaman <= ttl ise geçerlidir.
            if ttl is None or saat() - zaman <= ttl:
                isabet += 1
                return deger
            else:
                # TTL dolmuş, önbelleği geçersiz say ve yeniden çalıştır
                del bellek[anahtar]
        
        iska += 1
        deger = f(*args, **kwargs)
        bellek[anahtar] = (deger, saat())
        return deger

    # Metotları sarmal fonksiyonuna ekleme
    sarmal.temizle = bellek.clear
    sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
    
    # Orijinal fonksiyon meta verilerini koruma
    sarmal.__name__ = f.__name__
    sarmal.__doc__ = f.__doc__
    
    return sarmal

return dekorator
