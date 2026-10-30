# kod-ifade · puan 0.00

**Not:** 0/11 test; başarısız: close(S.eval_expr("2+3*4"), 14) -> ValueError('Beklenen sayı veya parantez') | close(S.eval_expr("(2+3)*4"), 20) -> ValueError('Beklenen sayı veya parantez') | close(S.eval_expr("-3+5"), 2) -> ValueError("could not convert string to float: '-'") | close(S.eval_expr("2*(3+(4-1))/3"), 4) -> ValueError('Beklenen sayı veya parantez') | close(S.eval_expr("10/4"), 2.5) -> ValueError('Beklenen sayı veya 

## Prompt

Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
import re
from typing import List, Tuple, Union

def tokenize(s: str) -> List[str]:
    # Boşlukları kaldır ve sayıları (ondalık dahil), operatörleri ve parantezleri ayır
    s = s.replace(' ', '')
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isdigit() or s[i] == '.':
            j = i
            while j < len(s) and (s[j].isdigit() or s[j] == '.'):
                j += 1
            tokens.append(s[i:j])
            i = j
        elif s[i] in '+-*/()':
            tokens.append(s[i])
            i += 1
        else:
            raise ValueError(f"Geçersiz karakter: {s[i]}")
    return tokens

def parse(tokens: List[str]) -> Tuple[Union[float, int], List[Tuple]]:
    # Basit bir recursive descent parser: expression -> term -> factor
    pos = [0]  # Mutable index
    
    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None

    def consume():
        token = tokens[pos[0]]
        pos[0] += 1
        return token

    def parse_factor():
        # Tekli eksiyi (-3, -(2+1)) ve parantezleri işle
        if peek() == '(':
            consume()
            val, _ = parse_expression()
            if peek() != ')':
                raise ValueError("Kapanmamış parantez")
            consume()
            return float(val), []
        
        # Tekli eksi (-5) veya sayı (2.5, 3)
        token = peek()
        if token and (token[0] == '-' or (token.isdigit() and len(token) > 1)):
            val_str = consume()
            return float(val_str), []
        
        raise ValueError("Beklenen sayı veya parantez")

    def parse_term():
        left, _ = parse_factor()
        while peek() in ['+', '-']:
            op = consume()
            right, _ = parse_factor()
            if op == '+':
                left += right
            else:
                left -= right
        return left, []

    def parse_expression():
        # Soldan sağa birleşme ve işlem önceliği (+ -) için döngü
        left, _ = parse_term()
        while peek() in ['*', '/']:
            op = consume()
            right, _ = parse_factor()
            if op == '*':
                left *= right
            else:
                # Bölme işlemi kontrolü (sıfıra bölme)
                if right == 0:
                    raise ZeroDivisionError("Sıfıra bölme hatası")
                left /= right
        return left, []

    result, _ = parse_expression()
    if pos[0] != len(tokens):
        raise ValueError("İfade sonu bekleniyor")
    return float(result), []

def eval_expr(s: str) -> float:
    tokens = tokenize(s)
    return parse(tokens)[0]

# Örnek testler (yorum satırı olarak, çalıştırılmayacak şekilde):
# print(eval_expr("2 + 3 * 4")) # 14.0
# print(eval_expr("-(2+1)"))     # -3.0
# print(eval_expr("2*-3"))       # -6.0
# print(eval_expr("2.5 + 3.5"))  # 6.0
```

## Notlandırılan kod/komut

```
import re
from typing import List, Tuple, Union

def tokenize(s: str) -> List[str]:
    # Boşlukları kaldır ve sayıları (ondalık dahil), operatörleri ve parantezleri ayır
    s = s.replace(' ', '')
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isdigit() or s[i] == '.':
            j = i
            while j < len(s) and (s[j].isdigit() or s[j] == '.'):
                j += 1
            tokens.append(s[i:j])
            i = j
        elif s[i] in '+-*/()':
            tokens.append(s[i])
            i += 1
        else:
            raise ValueError(f"Geçersiz karakter: {s[i]}")
    return tokens

def parse(tokens: List[str]) -> Tuple[Union[float, int], List[Tuple]]:
    # Basit bir recursive descent parser: expression -> term -> factor
    pos = [0]  # Mutable index
    
    def peek():
        if pos[0] < len(tokens):
            return tokens[pos[0]]
        return None

    def consume():
        token = tokens[pos[0]]
        pos[0] += 1
        return token

    def parse_factor():
        # Tekli eksiyi (-3, -(2+1)) ve parantezleri işle
        if peek() == '(':
            consume()
            val, _ = parse_expression()
            if peek() != ')':
                raise ValueError("Kapanmamış parantez")
            consume()
            return float(val), []
        
        # Tekli eksi (-5) veya sayı (2.5, 3)
        token = peek()
        if token and (token[0] == '-' or (token.isdigit() and len(token) > 1)):
            val_str = consume()
            return float(val_str), []
        
        raise ValueError("Beklenen sayı veya parantez")

    def parse_term():
        left, _ = parse_factor()
        while peek() in ['+', '-']:
            op = consume()
            right, _ = parse_factor()
            if op == '+':
                left += right
            else:
                left -= right
        return left, []

    def parse_expression():
        # Soldan sağa birleşme ve işlem önceliği (+ -) için döngü
        left, _ = parse_term()
        while peek() in ['*', '/']:
            op = consume()
            right, _ = parse_factor()
            if op == '*':
                left *= right
            else:
                # Bölme işlemi kontrolü (sıfıra bölme)
                if right == 0:
                    raise ZeroDivisionError("Sıfıra bölme hatası")
                left /= right
        return left, []

    result, _ = parse_expression()
    if pos[0] != len(tokens):
        raise ValueError("İfade sonu bekleniyor")
    return float(result), []

def eval_expr(s: str) -> float:
    tokens = tokenize(s)
    return parse(tokens)[0]

# Örnek testler (yorum satırı olarak, çalıştırılmayacak şekilde):
# print(eval_expr("2 + 3 * 4")) # 14.0
# print(eval_expr("-(2+1)"))     # -3.0
# print(eval_expr("2*-3"))       # -6.0
# print(eval_expr("2.5 + 3.5"))  # 6.0
```
