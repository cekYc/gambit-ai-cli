import time
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
    
    def is_hashable(obj):
        try:
            hash(obj)
            return True
        except TypeError:
            return False

    def dekorator(f):
        cache = {}
        isabet = iska = 0
        
        try:
            sig = inspect.signature(f)
        except ValueError:
            # Dekorasyonun yapıldığı fonksiyonun imzasını alamazsak, önbellekleme yapamayız.
            sig = None

        def sarmal(*args, **kwargs):
            nonlocal isabet, iska

            anahtar = None
            
            if sig:
                try:
                    # Argümanları fonksiyon imzasını kullanarak bağla (konumsal ve isimli fark etmeksizin)
                    bound_args = sig.bind(*args, **kwargs)
                    bound_args.apply_defaults()
                    
                    # Tüm argümanların hashlenip hashlenemediğini kontrol et
                    if all(is_hashable(v) for v in bound_args.arguments.values()):
                        # Canonical anahtar: Bağlanmış argümanların değerlerinin tuple'ı
                        anahtar = tuple(bound_args.arguments[k] for k in sig.parameters)
                except TypeError: 
                    # Argümanlar fonksiyon imzasıyla uyuşmuyorsa (ör: eksik argüman)
                    pass
            
            if anahtar is not None and anahtar in cache:
                deger, zaman = cache[anahtar]
                # TTL kontrolü: ttl geçtikten SONRA geçersiz.
                if ttl is None or saat() - zaman <= ttl:
                    isabet += 1
                    return deger

            iska += 1
            deger = f(*args, **kwargs)
            
            if anahtar is not None:
                cache[anahtar] = (deger, saat())
            
            return deger

        sarmal.temizle = cache.clear
        sarmal.bilgi = lambda: {"isabet": isabet, "iska": iska}
        return sarmal
    return dekorator
