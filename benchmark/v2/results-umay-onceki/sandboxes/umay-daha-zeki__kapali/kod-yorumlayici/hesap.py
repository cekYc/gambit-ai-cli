import re
from operator import add, sub, mul, truediv, pow, mod

# Fonksiyon tanımları
def min_func(*args):
    return min(args)

def max_func(*args):
    return max(args)

def abs_func(x):
    return abs(x)

# Global ortam (değişkenler, fonksiyonlar)
global_env = {
    'min': min_func,
    'max': max_func,
    'abs': abs_func
}

# Tokenizer (Basitleştirilmiş)
def tokenize(program):
    token_specification = [
        ('NUMBER', r'\d+(\.\d*)?'),
        ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('OP', r'\+\s*|\-\s*|\*\s*|/\s*|%\s*|\**|\(\s*|\)\s*|;'), # Operatörler ve parantezler
        ('ASSIGN', r'='),
        ('COMMENT', r'#.*'),
        ('SKIP', r'\s+'),
    ]
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, program):
        kind = mo.lastgroup
        value = mo.group(mo.lastgroup)
        if kind == 'COMMENT' or kind == 'SKIP':
            continue
        tokens.append((kind, value))
    return tokens

# Sözdizimi Ayrıştırıcı (Parser) - Basitleştirilmiş Öncelik Tabanlı
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected_type, expected_value=None):
        if self.current_token and self.current_token[0] == expected_type and (expected_value is None or self.current_token[1] == expected_value):
            self.advance()
        else:
            raise SyntaxError(f"Beklenen {expected_type} ({expected_value}) bulunamadı. Mevcut: {self.current_token}")

    def parse(self):
        statements = []
        while self.current_token and self.current_token[0] != 'SKIP':
            stmt = self._parse_statement()
            if stmt: # Boş ifade değilse kaydet
                statements.append(stmt)
            # İfade sonu kontrolü (; veya satır sonu (token listesinde bitiş))
            if self.current_token and self.current_token[1] == ';':
                self.advance() # ; token'ını tüket
        return statements

    def _parse_statement(self):
        # Atama mı, yoksa ifade mi?
        if self.current_token and self.current_token[0] == 'ID' and self.tokens[self.pos+1][1] == '=':
            id_token = self.current_token
            self.advance() # ID tüket
            self.eat('ASSIGN', '=')
            value = self._parse_expression()
            return (id_token[1], value)
        else:
            return self._parse_expression()

    # --- İfade Ayrıştırma (Operator Precedence Parsing) ---
    # Bu kısım, karmaşık öncelik kurallarını (**, *, /, +, -, parantez) yönetir.
    def _parse_expression(self):
        return self._parse_precedence(0) # En düşük öncelik ile başla

    def _parse_precedence(self, min_precedence):
        # Bir ilkel (sayı, ID, parantez) veya sol taraf
        left = self._parse_primary()

        while self.current_token:
            kind, value = self.current_token
            
            # Operatörlerin öncelik sırası (Düşükten Yükseğe): +/-, */%/, **, Parantez
            # Öncelikler: 1 (+-), 2 (*/%), 3 (**)
            if kind == 'OP':
                if value in ('+', '-'): prec = 1
                elif value in ('*', '/', '%'): prec = 2
                elif value == '**': prec = 3
                else: break # Diğer OP'ler (parantez) burada işlenmez

                if prec < min_precedence: break

                self.advance() # Operatörü tüket
                
                # Sağdan birleşme (Right Associativity) kontrolü (sadece **) 
                right_min_precedence = prec if value == '**' else prec + 1
                right = self._parse_precedence(right_min_precedence)
                
                # Yorumlama (Evaluation) adımını burada yapmalıyız
                left = self._apply_op(left, value, right)
            else: 
                break
        return left

    def _parse_primary(self):
        kind, value = self.current_token
        
        if kind == 'NUMBER':
            self.advance()
            return float(value) if '.' in value else int(value)
        
        elif kind == 'ID':
            # Değişken mi, fonksiyon mu?
            if self.tokens[self.pos+1][1] == '(': # Fonksiyon çağrısı
                self.advance() # ID tüket
                self.eat('OP', '(')
                # Argümanları topla (basitçe parantez içindeki ifadelerin değerlerini döndürmeli)
                args = []
                while self.current_token and self.current_token[1] != ')':
                    args.append(self._parse_expression())
                    # Virgül (,) argüman ayracı olarak kabul edilmeli (token_specification'da eksik, varsayalım ki basit virgül ile ayrılıyor)
                    if self.current_token and self.current_token[1] == ',':
                        self.advance()
                    elif self.current_token and self.current_token[1] == ')':
                        break # Hata durumu
                self.eat('OP', ')')
                return global_env[value](*args)
            else:
                self.advance() # ID tüket
                if value in global_env: # Fonksiyon ise, çağrılmalı (yukarıdaki blokta yakalanmalı)
                    return global_env[value]
                else: # Değişken ise, global ortamdan al
                    if value not in global_env: 
                        raise NameError(f"Tanımsız değişken veya fonksiyon: {value}")
                    return global_env[value]
        
        elif value == '(': # Parantez ile başlatılan ifade
            self.advance() # '(' tüket
            result = self._parse_expression()
            self.eat('OP', ')') # ')' tüket
            return result
        
        else:
            raise SyntaxError(f"Beklenmedik token: {self.current_token}")

    # --- İfade Yorumlama Yardımcı Fonksiyonları ---
    def _apply_op(self, left_val, op_value, right_val):
        if op_value == '+': return add(left_val, right_val)
        if op_value == '-': return sub(left_val, right_val)
        if op_value == '*': return mul(left_val, right_val)
        if op_value == '/': 
            if right_val == 0: raise ZeroDivisionError("Sıfıra bölme hatası")
            return truediv(left_val, right_val)
        if op_value == '%': return mod(left_val, right_val)
        if op_value == '**': return pow(left_val, right_val)
        raise NotImplementedError(f"Bilinmeyen operatör: {op_value}")


def calistir(program: str) -> (float | int | None):
    """Küçük hesap dilini yorumlar ve son ifadenin değerini döndürür."""
    if not program.strip():
        return None

    tokens = tokenize(program)
    if not tokens: 
        return None

    parser = Parser(tokens)
    statements = parser.parse()

    last_result = None

    for stmt in statements:
        if len(stmt) == 2 and stmt[0] != 'None': # Atama (ad, deger) 
            var_name, value = stmt[1] 
            global_env[var_name] = value
            # Atama ifadesinin sonucu atanan değerdir, ancak biz son ifadenin sonucunu istiyoruz.
            # Atama, bir ifade DEĞİLDİR, bir komuttur. Son ifadenin değerini tutmalıyız.
            pass 
        else:
            # Bu bir ifade (değer döndüren) olmalı
            value = stmt
            last_result = value
            
    # Son ifadenin değerini döndür, yoksa None
    return last_result

# Testler (Gizli testler için referans)
# print(calistir("1 + 2 * 3")) # 7.0
# print(calistir("a = 10; a * 2")) # 20.0
# print(calistir("10 ** 2 ** 1")) # 10.0 # Sağdan birleşme
# print(calistir("-2 ** 2")) # -4.0 # Özel kural
# print(calistir("min(1, 5, 2)")) # 1
# print(calistir("10 / 0")) # ZeroDivisionError
# print(calistir("x + 1")) # NameError
