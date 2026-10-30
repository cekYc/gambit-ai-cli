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
    """
    Dört işlem (+ - * /), parantez, tekli eksi ve ondalıklı sayıları destekleyen
    basit bir ifade değerlendirici (eval/exec/compile kullanmadan).
    
    İşlem önceliği:
      1. Parantezler
      2. Çarpma ve bölme (soldan sağa)
      3. Toplama ve çıkarma (soldan sağa)
      4. Tekli eksi (unary minus) - en düşük öncelik, ancak parantez içi işlemlerden sonra uygulanır
    
    Boşluklar önemsizdir.
    """
    
    # Önce ifadedeki boşlukları kaldır
    s = s.replace(' ', '')
    
    pos = 0
    n = len(s)
    
    def peek():
        """Güncel konumdaki karakteri döndür, sona gelinmediyse."""
        nonlocal pos
        if pos < n:
            return s[pos]
        return None
    
    def advance():
        """Bir ileri git ve o konumdaki karakteri döndür."""
        nonlocal pos
        ch = peek()
        pos += 1
        return ch
    
    def parse_expression():
        """
        Toplama/çıkarma düzeyini işler (en düşük öncelik, soldan sağa).
        expression := term (('+' | '-') term)*
        """
        nonlocal pos
        
        # İlk terimi ayrıştır
        val = parse_term()
        
        while pos < n and s[pos] in ('+', '-'):
            op = advance()
            right = parse_term()
            if op == '+':
                val += right
            else:  # '-'
                val -= right
        
        return val
    
    def parse_term():
        """
        Çarpma/bölme düzeyini işler (soldan sağa).
        term := unary (('*' | '/') unary)*
        """
        nonlocal pos
        
        # İlk tekli eksi veya sayıyı ayrıştır
        val = parse_unary()
        
        while pos < n and s[pos] in ('*', '/'):
            op = advance()
            right = parse_unary()
            if op == '*':
                val *= right
            else:  # '/'
                if right == 0:
                    raise ZeroDivisionError("Sıfıra bölme hatası")
                val /= right
        
        return val
    
    def parse_unary():
        """
        Tekli eksi ve sayıları işler.
        unary := ('-' unary) | primary
        Bu, -3, -(2+1), 2*-3 gibi durumları ele alır.
        
        Not: Unary minus'ın önceliği, çarpma/bölmeden düşük ama 
        parantez içi işlemlerden yüksek olmalı. 
        Aslında standart matematiğe göre: -a*b = (-a)*b, -(2+1) gibi.
        Biz burada unary'yi term seviyesinde parse ediyoruz, bu doğru.
        """
        nonlocal pos
        
        if pos < n and s[pos] == '-':
            # Tekli eksi
            advance()  # '-' karakterini geç
            return -parse_unary()
        
        return parse_primary()
    
    def parse_primary():
        """
        En yüksek öncelik: sayılar ve parantezler.
        primary := NUMBER | '(' expression ')'
        """
        nonlocal pos
        
        if pos >= n:
            raise ValueError("İfade beklenirken sona gelindi")
        
        ch = s[pos]
        
        # Ondalıklı veya tamsayı sayı
        if ch.isdigit() or (ch == '.' and pos + 1 < n and s[pos+1].isdigit()):
            return parse_number()
        
        # Parantez ile çevrili ifade
        elif ch == '(':
            advance()  # '(' i geç
            val = parse_expression()
            if pos >= n or s[pos] != ')':
                raise ValueError("Eşleşmeyen parantez: ')' bekleniyor")
            advance()  # ')' i geç
            return val
        
        else:
            raise ValueError(f"Beklenmedik karakter: '{ch}' (pozisyon {pos})")
    
    def parse_number():
        """
        Ondalıklı veya tamsayı sayıyı ayrıştır.
        """
        nonlocal pos
        
        start = pos
        
        # Tamsayı kısmı
        while pos < n and s[pos].isdigit():
            pos += 1
        
        # Ondalık nokta ve ondalık kısım
        if pos < n and s[pos] == '.':
            pos += 1
            while pos < n and s[pos].isdigit():
                pos += 1
        
        num_str = s[start:pos]
        
        if not num_str or num_str == '.':
            raise ValueError(f"Geçersiz sayı: '{num_str}'")
        
        return float(num_str)
    
    # Değerlendirmeye başla
    result = parse_expression()
    
    # Tüm ifade ayrıştırılmalı
    if pos != n:
        raise ValueError(f"Beklenmedik karakter pozisyon {pos} de: '{s[pos]}'")
    
    return result
```

## Notlandırılan kod/komut

```
def eval_expr(s: str) -> float:
    """
    Dört işlem (+ - * /), parantez, tekli eksi ve ondalıklı sayıları destekleyen
    basit bir ifade değerlendirici (eval/exec/compile kullanmadan).
    
    İşlem önceliği:
      1. Parantezler
      2. Çarpma ve bölme (soldan sağa)
      3. Toplama ve çıkarma (soldan sağa)
      4. Tekli eksi (unary minus) - en düşük öncelik, ancak parantez içi işlemlerden sonra uygulanır
    
    Boşluklar önemsizdir.
    """
    
    # Önce ifadedeki boşlukları kaldır
    s = s.replace(' ', '')
    
    pos = 0
    n = len(s)
    
    def peek():
        """Güncel konumdaki karakteri döndür, sona gelinmediyse."""
        nonlocal pos
        if pos < n:
            return s[pos]
        return None
    
    def advance():
        """Bir ileri git ve o konumdaki karakteri döndür."""
        nonlocal pos
        ch = peek()
        pos += 1
        return ch
    
    def parse_expression():
        """
        Toplama/çıkarma düzeyini işler (en düşük öncelik, soldan sağa).
        expression := term (('+' | '-') term)*
        """
        nonlocal pos
        
        # İlk terimi ayrıştır
        val = parse_term()
        
        while pos < n and s[pos] in ('+', '-'):
            op = advance()
            right = parse_term()
            if op == '+':
                val += right
            else:  # '-'
                val -= right
        
        return val
    
    def parse_term():
        """
        Çarpma/bölme düzeyini işler (soldan sağa).
        term := unary (('*' | '/') unary)*
        """
        nonlocal pos
        
        # İlk tekli eksi veya sayıyı ayrıştır
        val = parse_unary()
        
        while pos < n and s[pos] in ('*', '/'):
            op = advance()
            right = parse_unary()
            if op == '*':
                val *= right
            else:  # '/'
                if right == 0:
                    raise ZeroDivisionError("Sıfıra bölme hatası")
                val /= right
        
        return val
    
    def parse_unary():
        """
        Tekli eksi ve sayıları işler.
        unary := ('-' unary) | primary
        Bu, -3, -(2+1), 2*-3 gibi durumları ele alır.
        
        Not: Unary minus'ın önceliği, çarpma/bölmeden düşük ama 
        parantez içi işlemlerden yüksek olmalı. 
        Aslında standart matematiğe göre: -a*b = (-a)*b, -(2+1) gibi.
        Biz burada unary'yi term seviyesinde parse ediyoruz, bu doğru.
        """
        nonlocal pos
        
        if pos < n and s[pos] == '-':
            # Tekli eksi
            advance()  # '-' karakterini geç
            return -parse_unary()
        
        return parse_primary()
    
    def parse_primary():
        """
        En yüksek öncelik: sayılar ve parantezler.
        primary := NUMBER | '(' expression ')'
        """
        nonlocal pos
        
        if pos >= n:
            raise ValueError("İfade beklenirken sona gelindi")
        
        ch = s[pos]
        
        # Ondalıklı veya tamsayı sayı
        if ch.isdigit() or (ch == '.' and pos + 1 < n and s[pos+1].isdigit()):
            return parse_number()
        
        # Parantez ile çevrili ifade
        elif ch == '(':
            advance()  # '(' i geç
            val = parse_expression()
            if pos >= n or s[pos] != ')':
                raise ValueError("Eşleşmeyen parantez: ')' bekleniyor")
            advance()  # ')' i geç
            return val
        
        else:
            raise ValueError(f"Beklenmedik karakter: '{ch}' (pozisyon {pos})")
    
    def parse_number():
        """
        Ondalıklı veya tamsayı sayıyı ayrıştır.
        """
        nonlocal pos
        
        start = pos
        
        # Tamsayı kısmı
        while pos < n and s[pos].isdigit():
            pos += 1
        
        # Ondalık nokta ve ondalık kısım
        if pos < n and s[pos] == '.':
            pos += 1
            while pos < n and s[pos].isdigit():
                pos += 1
        
        num_str = s[start:pos]
        
        if not num_str or num_str == '.':
            raise ValueError(f"Geçersiz sayı: '{num_str}'")
        
        return float(num_str)
    
    # Değerlendirmeye başla
    result = parse_expression()
    
    # Tüm ifade ayrıştırılmalı
    if pos != n:
        raise ValueError(f"Beklenmedik karakter pozisyon {pos} de: '{s[pos]}'")
    
    return result
```
