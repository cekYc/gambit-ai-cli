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

## Düşünme

Goal: determine the exact output of two `list comprehension` calls over a list of lambda functions and return only that as text.

Case 1 (`fs`): Each lambda is defined directly with `lambda: i`. In Python, `i` inside the lambda refers to the variable in the enclosing scope at definition time (late binding). All three lambdas capture the same reference to `i`, which after the loop ends holds `2`. So each call `f()` evaluates `i` and returns 2. Expected output: `[2, 2, 2]`.

Case 2 (`gs`): Each lambda uses a default argument trick `lambda i=i`: at definition time Python evaluates the expression on the right of `=` and binds it to the local name `i` in that function's scope (early binding). The loop runs for `i = 0, 1, 2`; each call `g()` takes the default value bound when defined. Expected output: `[0, 1, 2]`.

Final answer format: two lines of stdout from both print calls in one code block.


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
