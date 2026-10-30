# okuma-kapanis · puan 0.00

**Not:** beklenen '[2, 2, 2]\n[0, 1, 2]', cevap '[0, 1, 2]\n[0, 0, 0]'

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
fs = [lambda: i for i in range(3)]
print([f() for f in fs])
gs = [lambda i=i: i for i in range(3)]
print([g() for g in gs])
```

## Cevap

```text
[0, 1, 2]
[0, 0, 0]
```

## Notlandırılan kod/komut

```
[0, 1, 2]
[0, 0, 0]
```
