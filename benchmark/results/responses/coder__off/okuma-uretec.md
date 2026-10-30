# okuma-uretec · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
def gen():
    try:
        yield 1
        yield 2
    finally:
        print("bitti")

for x in gen():
    print(x)
    break
print("son")
```

## Cevap

1
bitti
son

## Notlandırılan kod/komut

```
1
bitti
son
```
