
class Tokenizer:
    """Basit bir tokenizer: sayıları, isimleri, işleçleri ve parantezleri token'lere ayırır."""
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)
        self.tokens = []
    
    def current_char(self):
        if self.pos < self.length:
            return self.text[self.pos]
        return None
    
    def peek_char(self):
        if self.pos + 1 < self.length:
            return self.text[self.pos + 1]
        return None
    
    def advance(self):
        self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self):
        start = self.pos
        has_dot = False
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break
                has_dot = True
            self.advance()
        num_str = self.text[start:self.pos]
        if has_dot:
            return ('NUMBER', float(num_str))
        return ('NUMBER', int(num_str))
    
    def read_identifier(self):
        start = self.pos
        while self.current_char() and (self.current_char().isalnum() or self.current_char() == '_'):
            self.advance()
        return ('IDENTIFIER', self.text[start:self.pos])
    
    def tokenize(self):
        while self.pos < self.length:
            self.skip_whitespace()
            self.skip_comment()
            
            ch = self.current_char()
            if ch is None:
                break
            
            # Satır sonu veya noktalı virgül
            if ch == '\n' or ch == ';':
                self.tokens.append(('SEP', ch))
                self.advance()
                continue
            
            # Parantezler
            if ch == '(':
                self.tokens.append(('LPAREN', ch))
                self.advance()
                continue
            if ch == ')':
                self.tokens.append(('RPAREN', ch))
                self.advance()
                continue
            
            # Virgül
            if ch == ',':
                self.tokens.append(('COMMA', ch))
                self.advance()
                continue
            
            # Atama
            if ch == '=':
                self.tokens.append(('ASSIGN', ch))
                self.advance()
                continue
            
            # İşleçler: ** kontrolü önce
            if ch == '*' and self.peek_char() == '*':
                self.tokens.append(('POWER', '**'))
                self.advance()
                self.advance()
                continue
            
            # Tek karakterli işleçler
            if ch in '+-*/%':
                self.tokens.append(('OP', ch))
                self.advance()
                continue
            
            # Sayı
            if ch.isdigit() or (ch == '.' and self.peek_char() and self.peek_char().isdigit()):
                self.tokens.append(self.read_number())
                continue
            
            # İsim (değişken/fonksiyon)
            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # Bilinmeyen karakter
            raise SyntaxError(f'Geçersiz karakter: {ch}')
        
        self.tokens.append(('EOF', None))
        return self.tokens


class Parser:
    """Recursive descent parser for the expression language."""
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else ('EOF', None)
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = ('EOF', None)
    
    def expect(self, token_type, value=None):
        if self.current[0] != token_type or (value is not None and self.current[1] != value):
            raise SyntaxError(f'Beklenen {token_type} {value}, ama {self.current} bulundu')
        self.advance()
    
    def parse(self):
        """Programı parse et: ifade listesi döndürür."""
        expressions = []
        while self.current[0] != 'EOF':
            if self.current[0] == 'SEP':
                self.advance()
                continue
            expr = self.parse_expression()
            expressions.append(expr)
            # İfade sonrası separator bekle (ama zorunlu değil, EOF da olabilir)
            while self.current[0] == 'SEP':
                self.advance()
        return expressions
    
    def parse_expression(self):
        """Atama veya ifade parse et."""
        # Atama kontrolü: identifier = expression
        if self.current[0] == 'IDENTIFIER':
            # Peek ahead for '='
            save_pos = self.pos
            name = self.current[1]
            self.advance()
            if self.current[0] == 'ASSIGN':
                self.advance()
                value = self.parse_expression()
                return ('ASSIGN', name, value)
            # Atama değil, geri sar ve normal ifade parse et
            self.pos = save_pos
            self.current = self.tokens[self.pos]
        
        return self.parse_add_sub()
    
    def parse_add_sub(self):
        """+ ve - işleçleri (en düşük öncelik)."""
        left = self.parse_mul_div_mod()
        while self.current[0] == 'OP' and self.current[1] in ('+', '-'):
            op = self.current[1]
            self.advance()
            right = self.parse_mul_div_mod()
            left = ('BINOP', op, left, right)
        return left
    
    def parse_mul_div_mod(self):
        """*, /, % işleçleri."""
        left = self.parse_power()
        while self.current[0] == 'OP' and self.current[1] in ('*', '/', '%'):
            op = self.current[1]
            self.advance()
            right = self.parse_power()
            left = ('BINOP', op, left, right)
        return left
    
    def parse_power(self):
        """** işleci (sağdan birleşir, unary'den önce)."""
        # Sol taraf: unary expression
        left = self.parse_unary()
        if self.current[0] == 'POWER':
            self.advance()
            right = self.parse_power()  # Sağdan birleşim için recursive çağrı
            left = ('BINOP', '**', left, right)
        return left
    
    def parse_unary(self):
        """Tekli + ve - işleçleri."""
        if self.current[0] == 'OP' and self.current[1] in ('+', '-'):
            op = self.current[1]
            self.advance()
            operand = self.parse_unary()
            return ('UNOP', op, operand)
        return self.parse_primary()
    
    def parse_primary(self):
        """Temel ifadeler: sayı, isim, fonksiyon çağrısı, parantezli ifade."""
        if self.current[0] == 'NUMBER':
            val = self.current[1]
            self.advance()
            return ('NUMBER', val)
        
        if self.current[0] == 'IDENTIFIER':
            name = self.current[1]
            self.advance()
            
            # Fonksiyon çağrısı kontrolü
            if self.current[0] == 'LPAREN':
                self.advance()
                args = []
                if self.current[0] != 'RPAREN':
                    while True:
                        args.append(self.parse_expression())
                        if self.current[0] == 'COMMA':
                            self.advance()
                            continue
                        break
                if self.current[0] != 'RPAREN':
                    raise SyntaxError('Kapanmamış parantez')
                self.advance()
                return ('CALL', name, args)
            
            return ('VAR', name)
        
        if self.current[0] == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            if self.current[0] != 'RPAREN':
                raise SyntaxError('Kapanmamış parantez')
            self.advance()
            return expr
        
        raise SyntaxError(f'Beklenmeyen token: {self.current}')


class Evaluator:
    """AST'yi değerlendirir."""
    def __init__(self):
        self.variables = {}
        self.functions = {
            'min': min,
            'max': max,
            'abs': abs,
        }
    
    def evaluate(self, node):
        if node[0] == 'NUMBER':
            return node[1]
        
        if node[0] == 'VAR':
            name = node[1]
            if name not in self.variables:
                raise NameError(f'Tanımsız değişken: {name}')
            return self.variables[name]
        
        if node[0] == 'ASSIGN':
            name = node[1]
            value = self.evaluate(node[2])
            self.variables[name] = value
            return value
        
        if node[0] == 'BINOP':
            op = node[1]
            left = self.evaluate(node[2])
            right = self.evaluate(node[3])
            
            if op == '+':
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                if right == 0:
                    raise ZeroDivisionError('Sıfıra bölme')
                return left / right
            elif op == '%':
                if right == 0:
                    raise ZeroDivisionError('Sıfıra bölme')
                return left % right
            elif op == '**':
                return left ** right
            
        if node[0] == 'UNOP':
            op = node[1]
            operand = self.evaluate(node[2])
            if op == '+':
                return +operand
            elif op == '-':
                return -operand
        
        if node[0] == 'CALL':
            name = node[1]
            args = [self.evaluate(arg) for arg in node[2]]
            if name not in self.functions:
                raise NameError(f'Bilinmeyen fonksiyon: {name}')
            func = self.functions[name]
            try:
                return func(*args)
            except TypeError as e:
                raise TypeError(f'Fonksiyon çağrı hatası: {e}')
        
        raise ValueError(f'Bilinmeyen AST düğümü: {node[0]}')


def calistir(program: str):
    """
    Küçük bir hesap dilini yorumlar ve son ifadenin değerini döndürür.
    
    Args:
        program: Yorumlanacak program metni
    
    Returns:
        Son ifadenin değeri (ya da None eğer hiç ifade yoksa)
    
    Raises:
        NameError: Tanımsız değişken veya bilinmeyen fonksiyon
        ZeroDivisionError: Sıfıra bölme
        SyntaxError: Söz dizimi hatası
    """
    if not program or not program.strip():
        return None
    
    tokenizer = Tokenizer(program)
    tokens = tokenizer.tokenize()
    
    parser = Parser(tokens)
    expressions = parser.parse()
    
    if not expressions:
        return None
    
    evaluator = Evaluator()
    result = None
    for expr in expressions:
        result = evaluator.evaluate(expr)
    
    return result
