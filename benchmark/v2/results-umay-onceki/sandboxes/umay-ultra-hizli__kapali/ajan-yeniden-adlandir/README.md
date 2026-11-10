# fatura

KDV hesaplama yardımcıları.

```python
from fatura import kdv_hesapla, hesapKdv, hesapKdvDahil, toplam_tutar

kdv_hesapla(100)      # 20.0
# hesapKdv(100)       # 20.0 (DeprecationWarning)
hesapKdvDahil(100)    # 120.0
```

`kdv_hesapla(tutar, oran=0.20)` tutarın KDV'sini döndürür.