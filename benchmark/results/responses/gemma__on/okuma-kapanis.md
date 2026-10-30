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

*   `fs = [lambda: i for i in range(3)]`
    *   This is a list comprehension creating three lambda functions.
    *   The variable `i` is defined in the scope of the list comprehension (in Python 3, list comprehensions have their own local scope, but let's look closer at how closures work).
    *   Wait, in Python 3, `[lambda: i for i in range(3)]` creates a list where each lambda refers to the variable `i`.
    *   In Python 2, `i` would be part of the function scope if it were a generator expression or loop, but here it's inside a list comprehension. However, even in Python 3, the name `i` is being looked up in the enclosing scope when the lambda is *called*.
    *   Let's trace:
        1.  `range(3)` produces 0, 1, 2.
        2.  The list comprehension executes. The variable `i` is updated to 0, then 1, then 2.
        3.  Because the lambda functions are defined as `lambda: i`, they don't capture the *value* of `i` at definition time; they capture the *variable* `i`.
        4.  By the time the loop finishes, `i` is 2.
        5.  When `f()` is called for each lambda in `[f() for f in fs]`, it looks up `i`. Since `i` is now 2 (the last value assigned to it in that scope), all lambdas return 2.
    *   Wait, let's double-check Python 3 list comprehension scoping. In Python 3, the loop variable `i` in a list comprehension is local to the comprehension. However, the lambda function is defined inside that comprehension. The lambda captures the name `i`. Since the lambda refers to `i`, and `i` is part of the scope where the lambda was created (the comprehension's scope), it will look for `i` in its enclosing scope when called.
    *   Actually, let's be precise: In Python 3, list comprehensions have their own scope. The variable `i` exists within that scope during the execution of the comprehension. Once the comprehension is finished, what happens to `i`?
    *   Let's test mentally or via standard behavior knowledge:
        ```python
        fs = [lambda: i for i in range(3)]
        # The list fs contains 3 functions.
        # Each function looks up 'i'.
        # In Python 3, the variable 'i' from a list comprehension is NOT leaked to the outer scope.
        # HOWEVER, the lambda captures the name 'i' from its enclosing scope (the comprehension).
        # When the comprehension finishes, the local scope of the comprehension is destroyed? No, the closures keep it alive.
        # The value of 'i' at the end of the loop was 2.
        ```
    *   Let's re-verify: `[lambda: i for i in range(3)]`. In Python 3, the list comprehension creates a new scope. The variable `i` is local to that scope. When the lambdas are called later, they look up `i` in their closure. Since `i` was part of the loop, and it's now at its final value (2), all functions return 2.
    *   Result for first print: `[2, 2, 2]`

    *   `gs = [lambda i=i: i for i in range(3)]`
    *   This is a common Python idiom to solve the "late binding" issue.
    *   Here, we are using a default argument `i=i`.
    *   Default arguments are evaluated at *definition time*.
    *   Trace:
        1.  Loop 1: `i` is 0. Lambda defined as `lambda i=0: i`.
        2.  Loop 2: `i` is 1. Lambda defined as `lambda i=1: i`.
        3.  Loop 3: `i` is 2. Lambda defined as `lambda i=2: i`.
    *   When `g()` is called, it uses the default value provided at definition time.
    *   Result for second print: `[0, 1, 2]`

    *   Line 1: `print([f() for f in fs])` -> `[2, 2, 2]`
    *   Line 2: `print([g() for g in gs])` -> `[0, 1, 2]`

    *   Python 3 list comprehension scope: The variable `i` is local to the comprehension.
    *   The lambda functions are defined inside the comprehension's scope.
    *   They capture the name `i`.
    *   After the loop finishes, `i` remains in that closure with its final value (2).
    *   Therefore, `[f() for f in fs]` results in `[2, 2, 2]`.

    ```text
    [2, 2, 2]
    [0, 1, 2]
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
