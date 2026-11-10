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
            
            # Anahtar oluşturma: Sıralamadan bağımsız hale getirmek için args ve kwargs'u birleştirip hash'lenebilir bir tuple yapıyoruz.
            try:
                # Varsayılan argümanlar ve verilen argümanları birleştirerek anahtar oluşturma
                arg_tuple = args + tuple(sorted(kwargs.items()))
                
                # Hashlenemeyen bir tip varsa önbelleğe almayı atla (ör: liste)
                for item in args + tuple(kwargs.values()):
                    # Basit hashlenebilir tipler kontrol ediliyor. Liste, dict, set vb. dışlanıyor.
                    if isinstance(item, (list, dict, set)):
                        return f(*args, **kwargs) # Önbelleğe almadan çalıştır
                
                anahtar = arg_tuple
            except TypeError:
                # Hashlenemeyen bir argüman varsa (liste vb.) doğrudan çalıştır
                return f(*args, **kwargs)

            if anahtar in _onbellek:
                deger, zaman = _onbellek[anahtar]
                # TTL kontrolü: Saat - Zaman > TTL ise geçersiz.
                if ttl is None or saat() - zaman > ttl:
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