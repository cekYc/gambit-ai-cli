# okuma-takma-ad · puan 1.00

**Not:** doğru

## Prompt

Aşağıdaki Python kodu çalıştırılınca ekrana tam olarak ne yazdırılır? Kodu kafanda çalıştır. Sadece çıktıyı tek bir ```text bloğu içinde ver.

```python
a = [1, 2, 3]
b = a
b += [4]
c = a[:]
c.append(5)
print(a, b, c)
```

## Cevap

Kod satır satır analiz edelim:

1. `a = [1, 2, 3]`: `a` adında bir liste oluşturulur. İçeriği `[1, 2, 3]`.
2. `b = a`: `b`, `a`'nın referansını alır. Yani `a` ve `b` aynı nesneyi işaret eder.
3. `b += [4]`: Python'da listeler için `+=` operatörü **in-place (yerinde)** genişletme yapar (`extend` gibi). Bu nedenle `b`'nin işaret ettiği liste (ki bu aynı zamanda `a`) sonuna 4 eklenir.
   - Şu an hem `a` hem de `b`: `[1, 2, 3, 4]`
4. `c = a[:]`: `c`, `a`'nın **kopyasıdır**. Yani yeni bir liste nesnesi oluşturulur.
   - `c` şu an: `[1, 2, 3, 4]` (ama bağımsız bir nesne)
5. `c.append(5)`: `c` listesinin sonuna 5 eklenir. Bu işlem `a` veya `b`'yi etkilemez çünkü `c` ayrı bir listedir.
   - `c` artık: `[1, 2, 3, 4, 5]`
6. `print(a, b, c)`: Üç değişkenin değerleri yazdırılır.
   - `a`: `[1, 2, 3, 4]`
   - `b`: `[1, 2, 3, 4]` (a ile aynı nesne olduğu için aynı değerde)
   - `c`: `[1, 2, 3, 4, 5]`

Çıktı:

```text
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```

## Notlandırılan kod/komut

```
[1, 2, 3, 4] [1, 2, 3, 4] [1, 2, 3, 4, 5]
```
