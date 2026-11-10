# fatura

KDV hesaplama yardımcıları.

```python
from fatura import kdv_hesapla
kdv_hesapla(100)        # 20.0
hesapKdvDahil(100)      # 120.0
```

`kdv_hesapla(tutar, oran=0.20)` tutarın KDV'sini döndürür.
Eski `hesapKdv` adı geri uyumluluk için burada kalmaktadır.
