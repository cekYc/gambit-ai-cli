# kod-ifade · puan 1.00

**Not:** 11/11 test

## Prompt

Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
def eval_expr(s: str) -> float:
    import re
    tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', s)
    
    def parse_expression(i):
        left, i = parse_term(i)
        while i < len(tokens) and tokens[i] in ['+', '-']:
            op = tokens[i]
            right, i = parse_term(i + 1)
            if op == '+':
                left += right
            else:
                left -= right
        return left, i

    def parse_term(i):
        left, i = parse_factor(i)
        while i < len(tokens) and tokens[i] in ['*', '/']:
            op = tokens[i]
            right, i = parse_factor(i + 1)
            if op == '*':
                left *= right
            else:
                left /= right
        return left, i

    def parse_factor(i):
        token = tokens[i]
        if token == '(':
            left, i = parse_expression(i + 1)
            if i < len(tokens) and tokens[i] == ')':
                return left, i + 1
            else:
                raise ValueError("Parantez kapatılmadı")
        elif token == '-':
            right, i = parse_factor(i + 1)
            return -right, i
        else:
            try:
                return float(token), i + 1
            except ValueError:
                raise ValueError(f"Geçersiz ifade: {token}")

    result, _ = parse_expression(0)
    return result
```

## Notlandırılan kod/komut

```
def eval_expr(s: str) -> float:
    import re
    tokens = re.findall(r'\d+\.?\d*|[+\-*/()]', s)
    
    def parse_expression(i):
        left, i = parse_term(i)
        while i < len(tokens) and tokens[i] in ['+', '-']:
            op = tokens[i]
            right, i = parse_term(i + 1)
            if op == '+':
                left += right
            else:
                left -= right
        return left, i

    def parse_term(i):
        left, i = parse_factor(i)
        while i < len(tokens) and tokens[i] in ['*', '/']:
            op = tokens[i]
            right, i = parse_factor(i + 1)
            if op == '*':
                left *= right
            else:
                left /= right
        return left, i

    def parse_factor(i):
        token = tokens[i]
        if token == '(':
            left, i = parse_expression(i + 1)
            if i < len(tokens) and tokens[i] == ')':
                return left, i + 1
            else:
                raise ValueError("Parantez kapatılmadı")
        elif token == '-':
            right, i = parse_factor(i + 1)
            return -right, i
        else:
            try:
                return float(token), i + 1
            except ValueError:
                raise ValueError(f"Geçersiz ifade: {token}")

    result, _ = parse_expression(0)
    return result
```
