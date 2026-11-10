# fatura

KDV hesaplama yardımcıları.

```python
from fatura import kdv_hesapla
hesapKdv(100)        # 20.0
hesapKdvDahil(100)   # 120.0
```

`hesapKdv(tutar, oran=0.20)` tutarın KDV'sini döndürür.
