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
        cache = {}
        isabet = iska = 0

        def sarmal(*args, **kwargs):
            nonlocal isabet, iska
            
            # Argümanları hashlenir hale getir: pozisyonel argümanlar ve sıralanmış anahtar kelime argümanları
            sorted_kwargs = tuple(sorted(kwargs.items()))
            anahtar = (args, sorted_kwargs)
            
            if anahtar in cache:
                deger, zaman = cache[anahtar]
                # TTL kontrolü: süre TTL'ye eşit veya daha az ise geçerlidir.
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger
            
            iska += 1
            deger = f(*args, **kwargs)
            cache[anahtar] = (deger, saat())
            return deger

        sarmal.temizle = cache.clear
        sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
        return sarmal
    return dekorator"}