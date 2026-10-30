# kod-ifade · puan 1.00

**Not:** 11/11 test

## Prompt

Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
import re

def eval_expr(s: str) -> float:
    # Boşlukları temizle ve sayıları/operatörleri tokenize et
    s = s.replace(" ", "")
    tokens = re.findall(r'\d*\.\d+|\d+|[+\-*/()]', s)
    
    def get_precedence(op):
        if op in ('+', '-'): return 1
        if op in ('*', '/'): return 2
        return 0

    def apply_op(operators, values):
        if len(values) < 2: return
        b = values.pop()
        a = values.pop()
        op = operators.pop()
        if op == '+': values.append(a + b)
        elif op == '-': values.append(a - b)
        elif op == '*': values.append(a * b)
        elif op == '/': values.append(a / b)

    def parse_expression(tokens):
        values = []
        operators = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == '(':
                # Parantez içini bulmak için dengeli parantezi takip et
                count = 1
                j = i + 1
                while count > 0:
                    if tokens[j] == '(': count += 1
                    elif tokens[j] == ')': count -= 1
                    j += 1
                values.append(parse_expression(tokens[i+1:j-1]))
                i = j - 1
            elif token in '+*/':
                while operators and get_precedence(operators[-1]) >= get_precedence(token):
                    apply_op(operators, values)
                operators.append(token)
            elif token == '-':
                # Tekli eksi kontrolü: 
                # İfadenin başındaysa veya bir operatörden/parantezden hemen sonra geliyorsa unary'dir
                is_unary = (i == 0 or tokens[i-1] in '(+-*/')
                if is_unary:
                    # Unary minus'ı -(...) şeklinde işlemek için parantez içine alıp devam et
                    # Veya doğrudan bir sonraki değeri negatif yap. En güvenli yol:
                    if i + 1 < len(tokens):
                        if tokens[i+1] == '(':
                            # -(...) durumu
                            count = 1
                            j = i + 2
                            while count > 0:
                                if tokens[j] == '(': count += 1
                                elif tokens[j] == ')': count -= 1
                                j += 1
                            values.append(-parse_expression(tokens[i+2:j-1]))
                            i = j - 1
                        else:
                            # -3 veya -2.5 durumu
                            val = float(tokens[i+1])
                            values.append(-val)
                            i += 1
                    else:
                        raise ValueError("Geçersiz ifade")
                else:
                    while operators and get_precedence(operators[-1]) >= get_precedence(token):
                        apply_op(operators, values)
                    operators.append(token)
            elif token == ')':
                pass # Zaten parantez içindeyken hallediliyor
            else:
                # Sayısal değer
                values.append(float(token))

            i += 1

        while operators:
            apply_op(operators, values)
        return values[0]

    # Tekli eksinin karmaşık yapısını (örn: --3 veya -(2+1)) yönetmek için 
    # önce unary operatörleri normalize edip sonra standart Shunting-yard/Recursive Descent mantığıyla çözüyoruz.
    # Ancak yukarıdaki yapı çoğu durumu kapsar. Daha sağlam bir yaklaşım için tokenları ön işleme tabi tutalım:
    
    def preprocess(tokens):
        new_tokens = []
        for i, t in enumerate(tokens):
            if t == '-' and (i == 0 or tokens[i-1] in '(+-*/'):
                # Unary minus'ı bir sayıya dönüştürmek yerine parantez içine alarak normalize edelim
                new_tokens.append('(-') # Bu basit mantık yetmeyebilir, daha iyisi:
            else:
                new_tokens.append(t)
        return new_tokens

    # Basitleştirilmiş ama sağlam bir yöntem: Recursive Descent Parser
    def parse(idx):
        def get_term(i):
            if tokens[i] == '(':
                val, next_i = parse(i + 1)
                return val, next_i + 1
            elif tokens[i] == '-':
                val, next_i = get_term(i + 1)
                return -val, next_i
            else:
                return float(tokens[i]), i + 1

        def get_expr(i):
            val, i = get_term(i)
            while i < len(tokens) and tokens[i] in ('+', '-'):
                op = tokens[i]
                next_val, next_i = get_term(i + 1)
                if op == '+': val += next_val
                else: val -= next_val
                i = next_i
            return val, i

        def get_mul_div(i):
            val, i = get_expr(i) # Bu yapı basitleştirme için; aslında hiyerarşik olmalı
            # Ancak istenen sadece +-*/ ve parantez olduğu için:
            return val, i

        # Gerçek bir parser yapısı (Precedence based)
        def expression(i):
            val, i = term(i)
            while i < len(tokens) and tokens[i] in ('+', '-'):
                op = tokens[i]
                right, i = term(i + 1)
                if op == '+': val += right
                else: val -= right
            return val, i

        def term(i):
            val, i = factor(i)
            while i < len(tokens) and tokens[i] in ('*', '/'):
                op = tokens[i]
                right, i = factor(i + 1)
                if op == '*': val *= right
                else: val /= right
            return val, i

        def factor(i):
            if tokens[i] == '-':
                val, next_i = factor(i + 1)
                return -val, next_i
            elif tokens[i] == '(':
                val, next_i = expression(i + 1)
                return val, next_i + 1
            else:
                # Sayısal değer (float veya int)
                try:
                    return float(tokens[i]), i + 1
                except ValueError:
                    raise ValueError("Geçersiz token")

        return expression(0)[0]

    return parse(0)
```

## Notlandırılan kod/komut

```
import re

def eval_expr(s: str) -> float:
    # Boşlukları temizle ve sayıları/operatörleri tokenize et
    s = s.replace(" ", "")
    tokens = re.findall(r'\d*\.\d+|\d+|[+\-*/()]', s)
    
    def get_precedence(op):
        if op in ('+', '-'): return 1
        if op in ('*', '/'): return 2
        return 0

    def apply_op(operators, values):
        if len(values) < 2: return
        b = values.pop()
        a = values.pop()
        op = operators.pop()
        if op == '+': values.append(a + b)
        elif op == '-': values.append(a - b)
        elif op == '*': values.append(a * b)
        elif op == '/': values.append(a / b)

    def parse_expression(tokens):
        values = []
        operators = []
        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == '(':
                # Parantez içini bulmak için dengeli parantezi takip et
                count = 1
                j = i + 1
                while count > 0:
                    if tokens[j] == '(': count += 1
                    elif tokens[j] == ')': count -= 1
                    j += 1
                values.append(parse_expression(tokens[i+1:j-1]))
                i = j - 1
            elif token in '+*/':
                while operators and get_precedence(operators[-1]) >= get_precedence(token):
                    apply_op(operators, values)
                operators.append(token)
            elif token == '-':
                # Tekli eksi kontrolü: 
                # İfadenin başındaysa veya bir operatörden/parantezden hemen sonra geliyorsa unary'dir
                is_unary = (i == 0 or tokens[i-1] in '(+-*/')
                if is_unary:
                    # Unary minus'ı -(...) şeklinde işlemek için parantez içine alıp devam et
                    # Veya doğrudan bir sonraki değeri negatif yap. En güvenli yol:
                    if i + 1 < len(tokens):
                        if tokens[i+1] == '(':
                            # -(...) durumu
                            count = 1
                            j = i + 2
                            while count > 0:
                                if tokens[j] == '(': count += 1
                                elif tokens[j] == ')': count -= 1
                                j += 1
                            values.append(-parse_expression(tokens[i+2:j-1]))
                            i = j - 1
                        else:
                            # -3 veya -2.5 durumu
                            val = float(tokens[i+1])
                            values.append(-val)
                            i += 1
                    else:
                        raise ValueError("Geçersiz ifade")
                else:
                    while operators and get_precedence(operators[-1]) >= get_precedence(token):
                        apply_op(operators, values)
                    operators.append(token)
            elif token == ')':
                pass # Zaten parantez içindeyken hallediliyor
            else:
                # Sayısal değer
                values.append(float(token))

            i += 1

        while operators:
            apply_op(operators, values)
        return values[0]

    # Tekli eksinin karmaşık yapısını (örn: --3 veya -(2+1)) yönetmek için 
    # önce unary operatörleri normalize edip sonra standart Shunting-yard/Recursive Descent mantığıyla çözüyoruz.
    # Ancak yukarıdaki yapı çoğu durumu kapsar. Daha sağlam bir yaklaşım için tokenları ön işleme tabi tutalım:
    
    def preprocess(tokens):
        new_tokens = []
        for i, t in enumerate(tokens):
            if t == '-' and (i == 0 or tokens[i-1] in '(+-*/'):
                # Unary minus'ı bir sayıya dönüştürmek yerine parantez içine alarak normalize edelim
                new_tokens.append('(-') # Bu basit mantık yetmeyebilir, daha iyisi:
            else:
                new_tokens.append(t)
        return new_tokens

    # Basitleştirilmiş ama sağlam bir yöntem: Recursive Descent Parser
    def parse(idx):
        def get_term(i):
            if tokens[i] == '(':
                val, next_i = parse(i + 1)
                return val, next_i + 1
            elif tokens[i] == '-':
                val, next_i = get_term(i + 1)
                return -val, next_i
            else:
                return float(tokens[i]), i + 1

        def get_expr(i):
            val, i = get_term(i)
            while i < len(tokens) and tokens[i] in ('+', '-'):
                op = tokens[i]
                next_val, next_i = get_term(i + 1)
                if op == '+': val += next_val
                else: val -= next_val
                i = next_i
            return val, i

        def get_mul_div(i):
            val, i = get_expr(i) # Bu yapı basitleştirme için; aslında hiyerarşik olmalı
            # Ancak istenen sadece +-*/ ve parantez olduğu için:
            return val, i

        # Gerçek bir parser yapısı (Precedence based)
        def expression(i):
            val, i = term(i)
            while i < len(tokens) and tokens[i] in ('+', '-'):
                op = tokens[i]
                right, i = term(i + 1)
                if op == '+': val += right
                else: val -= right
            return val, i

        def term(i):
            val, i = factor(i)
            while i < len(tokens) and tokens[i] in ('*', '/'):
                op = tokens[i]
                right, i = factor(i + 1)
                if op == '*': val *= right
                else: val /= right
            return val, i

        def factor(i):
            if tokens[i] == '-':
                val, next_i = factor(i + 1)
                return -val, next_i
            elif tokens[i] == '(':
                val, next_i = expression(i + 1)
                return val, next_i + 1
            else:
                # Sayısal değer (float veya int)
                try:
                    return float(tokens[i]), i + 1
                except ValueError:
                    raise ValueError("Geçersiz token")

        return expression(0)[0]

    return parse(0)
```
