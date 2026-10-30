# kod-ifade · puan 0.00

**Not:** zaman aşımı

## Prompt

Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

```python
import re
from typing import List, Tuple, Union, Any

def tokenize(expr: str) -> List[Any]:
    """Girdiyi token'lara ayırır (+, -, *, /, sayılar, parantez)."""
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        
        # Boşlukları atla
        if c.isspace():
            i += 1
            continue
        
        # Parantezler
        if c in '()':
            tokens.append(c)
            i += 1
            continue
            
        # Operatörler (+ - * /)
        if c in '+-*/':
            tokens.append(c)
            i += 1
            continue
            
        # Sayı (integer veya float)
        if c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            start = i
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.' and i > 0 and expr[i-1] == '.':
                    break # Tek nokta kuralı
                i += 1
            num_str = expr[start:i]
            tokens.append(float(num_str))
            continue

        # Beklenmeyen karakter
        raise ValueError(f"Geçersiz karakter: {c}")
    return tokens

def ast(node):
    """Node'ları AST formatına dönüştürür (özel yapı)."""
    if isinstance(node, int) or isinstance(node, float):
        return node
    elif isinstance(node, str):
        if node == '+': return 'PLUS'
        elif node == '-': return 'MINUS'
        elif node == '*': return 'MULT'
        elif node == '/': return 'DIV'
        elif node == '(': pass # Parantezleri tekrar yapma, işlem önceliğiyle yönetilecek
    elif isinstance(node, list):
        if len(node) == 1:
            return ast(node[0])
        return ASTNode(node)

class ASTNode:
    def __init__(self, value: Any, children: List[Any] = None):
        self.value = value
        self.children = children or []

def parse(tokens: List[Any], pos: int = 0) -> Tuple[ASTNode, int]:
    """Token listesini AST'ye dönüştürür."""
    
    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def consume(expected_type=None):
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if expected_type and not isinstance(token, expected_type):
            raise ValueError(f"Beğenilen tür beklenmedi: {token}")
        return token

    # Üst seviye: Çarpım/Bölme (+) ve Parantezleri yönetir.
    # ( + - ) yapısını tek bir bloğa sığdırır.
    
    def parse_primary():
        if peek() == '(':
            consume('(', int) # Açılı parantez, içerik gelecek
            node, _ = parse()
            consume(')')
            return ASTNode(0, [node]) # 0 ile işaretleyelim ki sonra işlemci bunu ele alsın
        
        token = peek()
        
        if isinstance(token, int):
            consume(int)
            return ASTNode(token)
            
        elif isinstance(token, float):
            consume(float)
            return ASTNode(token)

        # İşaretli sayı veya ifade (-3, -2+1 gibi)
        if token == '-':
            consume('-')
            node, _ = parse_primary()
            return ASTNode(0, [-node]) 

        raise ValueError(f"İlk token beklenmedi: {token}")

    def parse_additive():
        # (+ -) kuralını yönetmek için önce parantezleri ve işaretli ifadeleri çözüp, 
        # sonra (+) ve (-) operatörlerini ekleyeceğiz.
        left_node = None
        
        while pos < len(tokens):
            token = tokens[pos]
            
            if isinstance(token, int) or isinstance(token, float):
                break
            
            if token == '-':
                consume('-')
                node, _ = parse_additive() # Geriye dönüşümlü çağrı (YGR)
                left_node.value = -left_node.children[0] if left_node else None
                
            elif isinstance(token, ASTNode):
                # Eğer bir ASTNode ise ve içinde negatiflik varsa, 
                # o negatifliği yakalayalım.
                pass

        return parse_unary() if left_node is not None else parse_primary()

    def parse_multiplicative():
        node = parse_additive()
        
        while pos < len(tokens) and tokens[pos] in '+-':
            op = consume(str)
            right_node, _ = parse_additive() # Toplama seviyesine geri düş
        
        return ASTNode(0, [node])

    def parse_unary():
        if peek() == '-':
            consume('-')
            node, _ = parse_multiplicative()
            # Eğer çocuklar listeyse (parantez içi), ilk elemanı negatifleştir
            if isinstance(node.value, int) and len(node.children) > 0:
                return ASTNode(0, [-node.children[0]])
            
        node, _ = parse_primary()
        return parse_multiplicative()

    def parse_expressions():
        # Tüm ifadeleri (+ - * /) mantığında birleştirir.
        left_node = None
        
        while pos < len(tokens):
            token = tokens[pos]
            
            if isinstance(token, int) or isinstance(token, float):
                pass
            
            if token == '(':
                consume('(', ASTNode) # Açılı parantez
                node, _ = parse()
                consume(')')
                
            elif isinstance(token, ASTNode):
                pass
                
        return parse_additive()

    # Parantezleri ve işlemleri tek bir blokta toplarız.
    # Bu fonksiyonun görevi: (2+3), 2-3, -2 gibi yapıları düzgün ele almaktır.
    
    if pos < len(tokens):
        # İlk token kontrolü
        first = tokens[pos]
        
        if isinstance(first, int) or isinstance(first, float):
            left_node, _ = parse_multiplicative()
        elif first == '-':
            left_node, _ = parse_unary()
        else:
            raise ValueError("İlk token beklenmedi")
            
    return ASTNode(0, [left_node])

def ast_eval(node: ASTNode) -> float:
    """AST'i değerlere dönüştürür."""
    
    def evaluate(child):
        if isinstance(child, int) or isinstance(child, float):
            return child
        
        # Eğer çocuklar varsa ve value 0 ise (işlemci işareti), içine gir
        if node.value == 0 and len(node.children) > 0:
            inner = evaluate(node.children[0])
            
            # Negatif işaret kontrolü
            if isinstance(inner, float):
                return -inner
            
            raise ValueError(f"İçerik yok veya hata: {node.children}")

        # Operatör işlemleri
        if node.value == 'PLUS':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            return l + r
            
        elif node.value == 'MINUS':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            # Eğer sadece tek bir operand varsa (örn: -3), bu yapıyı yakalamamız gerekir.
            # Ancak parse fonksiyonu bunu -3 şeklinde ASTNode(-3) olarak döndürüyor mu?
            # Hayır, parse_unary içinde şöyle yapıyoruz: ASTNode(0, [-node.children[0]])
            # O zaman node.value 0 olacak ve children[0] negatif olacak.
            return l - r

        elif node.value == 'MULT':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            return l * r

        elif node.value == 'DIV':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            if r == 0:
                raise ZeroDivisionError("Bölünecek sayı sıfır")
            return l / r
        
        else:
            # Eğer value 0 ise ve sadece bir çocuk varsa, o çocuğun negatifini al
            if node.value == 0 and len(node.children) > 0:
                child = evaluate(node.children[0])
                return -child

    if not isinstance(node.children, list):
        raise ValueError("AST yapısı hatalı")
        
    # Eğer en dış katmanda value 0 ve sadece bir çocuk varsa (örn: (-2+3))
    if node.value == 0 and len(node.children) > 0:
        return -evaluate(node.children[0])
    
    return evaluate(node)

def eval_expr(s: str) -> float:
    """
    Verilen ifadeyi hesaplar ve float döner.
    -4, 2+3, (2-1)*5 gibi ifadeleri destekler.
    """
    # Girdiyi temizle
    s = s.replace(' ', '')
    
    if not s:
        raise ValueError("Boş ifade")
        
    tokens = tokenize(s)
    tree, _ = parse(tokens)
    return ast_eval(tree)

# Test etme için basit kullanım örnekleri (kod bloğunda çalışmaz ama mantık burada)
# print(eval_expr("-3"))      # -3.0
# print(eval_expr("2+3"))     # 5.0
# print(eval_expr("(2-1)*5")) # 5.0
# print(eval_expr("-(2+1)"))  # -3.0
```

## Notlandırılan kod/komut

```
import re
from typing import List, Tuple, Union, Any

def tokenize(expr: str) -> List[Any]:
    """Girdiyi token'lara ayırır (+, -, *, /, sayılar, parantez)."""
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        
        # Boşlukları atla
        if c.isspace():
            i += 1
            continue
        
        # Parantezler
        if c in '()':
            tokens.append(c)
            i += 1
            continue
            
        # Operatörler (+ - * /)
        if c in '+-*/':
            tokens.append(c)
            i += 1
            continue
            
        # Sayı (integer veya float)
        if c.isdigit() or (c == '.' and i + 1 < len(expr) and expr[i+1].isdigit()):
            start = i
            while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                if expr[i] == '.' and i > 0 and expr[i-1] == '.':
                    break # Tek nokta kuralı
                i += 1
            num_str = expr[start:i]
            tokens.append(float(num_str))
            continue

        # Beklenmeyen karakter
        raise ValueError(f"Geçersiz karakter: {c}")
    return tokens

def ast(node):
    """Node'ları AST formatına dönüştürür (özel yapı)."""
    if isinstance(node, int) or isinstance(node, float):
        return node
    elif isinstance(node, str):
        if node == '+': return 'PLUS'
        elif node == '-': return 'MINUS'
        elif node == '*': return 'MULT'
        elif node == '/': return 'DIV'
        elif node == '(': pass # Parantezleri tekrar yapma, işlem önceliğiyle yönetilecek
    elif isinstance(node, list):
        if len(node) == 1:
            return ast(node[0])
        return ASTNode(node)

class ASTNode:
    def __init__(self, value: Any, children: List[Any] = None):
        self.value = value
        self.children = children or []

def parse(tokens: List[Any], pos: int = 0) -> Tuple[ASTNode, int]:
    """Token listesini AST'ye dönüştürür."""
    
    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def consume(expected_type=None):
        nonlocal pos
        token = tokens[pos]
        pos += 1
        if expected_type and not isinstance(token, expected_type):
            raise ValueError(f"Beğenilen tür beklenmedi: {token}")
        return token

    # Üst seviye: Çarpım/Bölme (+) ve Parantezleri yönetir.
    # ( + - ) yapısını tek bir bloğa sığdırır.
    
    def parse_primary():
        if peek() == '(':
            consume('(', int) # Açılı parantez, içerik gelecek
            node, _ = parse()
            consume(')')
            return ASTNode(0, [node]) # 0 ile işaretleyelim ki sonra işlemci bunu ele alsın
        
        token = peek()
        
        if isinstance(token, int):
            consume(int)
            return ASTNode(token)
            
        elif isinstance(token, float):
            consume(float)
            return ASTNode(token)

        # İşaretli sayı veya ifade (-3, -2+1 gibi)
        if token == '-':
            consume('-')
            node, _ = parse_primary()
            return ASTNode(0, [-node]) 

        raise ValueError(f"İlk token beklenmedi: {token}")

    def parse_additive():
        # (+ -) kuralını yönetmek için önce parantezleri ve işaretli ifadeleri çözüp, 
        # sonra (+) ve (-) operatörlerini ekleyeceğiz.
        left_node = None
        
        while pos < len(tokens):
            token = tokens[pos]
            
            if isinstance(token, int) or isinstance(token, float):
                break
            
            if token == '-':
                consume('-')
                node, _ = parse_additive() # Geriye dönüşümlü çağrı (YGR)
                left_node.value = -left_node.children[0] if left_node else None
                
            elif isinstance(token, ASTNode):
                # Eğer bir ASTNode ise ve içinde negatiflik varsa, 
                # o negatifliği yakalayalım.
                pass

        return parse_unary() if left_node is not None else parse_primary()

    def parse_multiplicative():
        node = parse_additive()
        
        while pos < len(tokens) and tokens[pos] in '+-':
            op = consume(str)
            right_node, _ = parse_additive() # Toplama seviyesine geri düş
        
        return ASTNode(0, [node])

    def parse_unary():
        if peek() == '-':
            consume('-')
            node, _ = parse_multiplicative()
            # Eğer çocuklar listeyse (parantez içi), ilk elemanı negatifleştir
            if isinstance(node.value, int) and len(node.children) > 0:
                return ASTNode(0, [-node.children[0]])
            
        node, _ = parse_primary()
        return parse_multiplicative()

    def parse_expressions():
        # Tüm ifadeleri (+ - * /) mantığında birleştirir.
        left_node = None
        
        while pos < len(tokens):
            token = tokens[pos]
            
            if isinstance(token, int) or isinstance(token, float):
                pass
            
            if token == '(':
                consume('(', ASTNode) # Açılı parantez
                node, _ = parse()
                consume(')')
                
            elif isinstance(token, ASTNode):
                pass
                
        return parse_additive()

    # Parantezleri ve işlemleri tek bir blokta toplarız.
    # Bu fonksiyonun görevi: (2+3), 2-3, -2 gibi yapıları düzgün ele almaktır.
    
    if pos < len(tokens):
        # İlk token kontrolü
        first = tokens[pos]
        
        if isinstance(first, int) or isinstance(first, float):
            left_node, _ = parse_multiplicative()
        elif first == '-':
            left_node, _ = parse_unary()
        else:
            raise ValueError("İlk token beklenmedi")
            
    return ASTNode(0, [left_node])

def ast_eval(node: ASTNode) -> float:
    """AST'i değerlere dönüştürür."""
    
    def evaluate(child):
        if isinstance(child, int) or isinstance(child, float):
            return child
        
        # Eğer çocuklar varsa ve value 0 ise (işlemci işareti), içine gir
        if node.value == 0 and len(node.children) > 0:
            inner = evaluate(node.children[0])
            
            # Negatif işaret kontrolü
            if isinstance(inner, float):
                return -inner
            
            raise ValueError(f"İçerik yok veya hata: {node.children}")

        # Operatör işlemleri
        if node.value == 'PLUS':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            return l + r
            
        elif node.value == 'MINUS':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            # Eğer sadece tek bir operand varsa (örn: -3), bu yapıyı yakalamamız gerekir.
            # Ancak parse fonksiyonu bunu -3 şeklinde ASTNode(-3) olarak döndürüyor mu?
            # Hayır, parse_unary içinde şöyle yapıyoruz: ASTNode(0, [-node.children[0]])
            # O zaman node.value 0 olacak ve children[0] negatif olacak.
            return l - r

        elif node.value == 'MULT':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            return l * r

        elif node.value == 'DIV':
            l = evaluate(node.children[0])
            r = evaluate(node.children[1])
            if r == 0:
                raise ZeroDivisionError("Bölünecek sayı sıfır")
            return l / r
        
        else:
            # Eğer value 0 ise ve sadece bir çocuk varsa, o çocuğun negatifini al
            if node.value == 0 and len(node.children) > 0:
                child = evaluate(node.children[0])
                return -child

    if not isinstance(node.children, list):
        raise ValueError("AST yapısı hatalı")
        
    # Eğer en dış katmanda value 0 ve sadece bir çocuk varsa (örn: (-2+3))
    if node.value == 0 and len(node.children) > 0:
        return -evaluate(node.children[0])
    
    return evaluate(node)

def eval_expr(s: str) -> float:
    """
    Verilen ifadeyi hesaplar ve float döner.
    -4, 2+3, (2-1)*5 gibi ifadeleri destekler.
    """
    # Girdiyi temizle
    s = s.replace(' ', '')
    
    if not s:
        raise ValueError("Boş ifade")
        
    tokens = tokenize(s)
    tree, _ = parse(tokens)
    return ast_eval(tree)

# Test etme için basit kullanım örnekleri (kod bloğunda çalışmaz ama mantık burada)
# print(eval_expr("-3"))      # -3.0
# print(eval_expr("2+3"))     # 5.0
# print(eval_expr("(2-1)*5")) # 5.0
# print(eval_expr("-(2+1)"))  # -3.0
```
