# kod-ifade · puan 0.00

**Not:** 0/11 test; başarısız: import: SyntaxError('unterminated string literal (detected at line 38)', ('<temp>\\solution.py', 38, 42, "            return result if token == '+'' else -result", 38, 42))

## Prompt

Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
import re

def eval_expr(s):
    tokens = re.findall(r'(\d+\.\d+|\d+|[+\-*/()])', s)
    pos = 0

    def parse_expression():
        result = parse_term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            right = parse_term()
            if op == '+': result += right
            else: result -= right
        return result

    def parse_term():
        result = parse_factor()
        while pos < len(tokens) and tokens[pos] in ('*', '/'):
            op = tokens[pos]
            pos += 1
            right = parse_factor()
            if op == '*': result *= right
            else: result /= right
        return result

    def parse_factor():
        token = tokens[pos]
        if token == '-':
            pos += 1
            return -parse_factor()
        if token in ('(', '+', '-'):
            # Handle unary plus, leading minus before paren, or a raw plus/minus at start of expr
            if not (pos > 0 and tokens[pos-1] in ('+', '-', '*', '/')): # valid only as unary op here
                raise SyntaxError(f"Unexpected token {token}")
            # We treat the next factor after an unary sign
            result = parse_factor()
            return result if token == '+'' else -result

        if token == '(' and pos + 1 < len(tokens):
            pos += 1
            result = parse_expression()
            pos += 1 # skip ')'
            return result

        pos += 1
        return float(token)

    return parse_expression()
```

## Notlandırılan kod/komut

```
import re

def eval_expr(s):
    tokens = re.findall(r'(\d+\.\d+|\d+|[+\-*/()])', s)
    pos = 0

    def parse_expression():
        result = parse_term()
        while pos < len(tokens) and tokens[pos] in ('+', '-'):
            op = tokens[pos]
            pos += 1
            right = parse_term()
            if op == '+': result += right
            else: result -= right
        return result

    def parse_term():
        result = parse_factor()
        while pos < len(tokens) and tokens[pos] in ('*', '/'):
            op = tokens[pos]
            pos += 1
            right = parse_factor()
            if op == '*': result *= right
            else: result /= right
        return result

    def parse_factor():
        token = tokens[pos]
        if token == '-':
            pos += 1
            return -parse_factor()
        if token in ('(', '+', '-'):
            # Handle unary plus, leading minus before paren, or a raw plus/minus at start of expr
            if not (pos > 0 and tokens[pos-1] in ('+', '-', '*', '/')): # valid only as unary op here
                raise SyntaxError(f"Unexpected token {token}")
            # We treat the next factor after an unary sign
            result = parse_factor()
            return result if token == '+'' else -result

        if token == '(' and pos + 1 < len(tokens):
            pos += 1
            result = parse_expression()
            pos += 1 # skip ')'
            return result

        pos += 1
        return float(token)

    return parse_expression()
```
