# okuma-kapanis · puan 1.00

**Not:** doğru

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
[2, 2, 2]
[0, 1, 2]
```

## Notlandırılan kod/komut

```
[2, 2, 2]
[0, 1, 2]
```
