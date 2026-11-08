def calistir(program: str):
    """
    Küçük bir hesap dilini yorumlar ve son ifadenin değerini döndürür.
    """
    
    class Tokenizer:
        def __init__(self, text: str):
            self.text = text
            self.pos = 0
            self.tokens = []
            self.tokenize()
        
        def tokenize(self):
            while self.pos < len(self.text):
                ch = self.text[self.pos]
                
                # Boşlukları atla
                if ch in ' \t\r':
                    self.pos += 1
                    continue
                
                # Satır sonu veya ; -> ayrıştırıcı bunu ifade ayracı olarak kullanacak
                if ch == '\n' or ch == ';':
                    self.tokens.append(('SEP', ch))
                    self.pos += 1
                    continue
                
                # Yorum satırı
                if ch == '#':
                    while self.pos < len(self.text) and self.text[self.pos] != '\n':
                        self.pos += 1
                    continue
                
                # Sayı
                if ch.isdigit() or ch == '.':
                    start = self.pos
                    has_dot = False
                    while self.pos < len(self.text):
                        c = self.text[self.pos]
                        if c.isdigit():
                            self.pos += 1
                        elif c == '.' and not has_dot:
                            has_dot = True
                            self.pos += 1
                        else:
                            break
                    num_str = self.text[start:self.pos]
                    if num_str == '.':
                        raise SyntaxError("Geçersiz sayı")
                    if has_dot:
                        self.tokens.append(('NUMBER', float(num_str)))
                    else:
                        self.tokens.append(('NUMBER', int(num_str)))
                    continue
                
                # Tanımlayıcı / anahtar kelime
                if ch.isalpha() or ch == '_':
                    start = self.pos
                    while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                        self.pos += 1
                    ident = self.text[start:self.pos]
                    if ident in ('min', 'max', 'abs'):
                        self.tokens.append(('FUNC', ident))
                    else:
                        self.tokens.append(('IDENT', ident))
                    continue
                
                # İşleçler ve parantezler
                if ch == '+':
                    self.tokens.append(('PLUS', '+'))
                    self.pos += 1
                    continue
                if ch == '-':
                    self.tokens.append(('MINUS', '-'))
                    self.pos += 1
                    continue
                if ch == '*':
                    if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '*':
                        self.tokens.append(('POWER', '**'))
                        self.pos += 2
                    else:
                        self.tokens.append(('MUL', '*'))
                        self.pos += 1
                    continue
                if ch == '/':
                    self.tokens.append(('DIV', '/'))
                    self.pos += 1
                    continue
                if ch == '%':
                    self.tokens.append(('MOD', '%'))
                    self.pos += 1
                    continue
                if ch == '=':
                    self.tokens.append(('ASSIGN', '='))
                    self.pos += 1
                    continue
                if ch == '(':
                    self.tokens.append(('LPAREN', '('))
                    self.pos += 1
                    continue
                if ch == ')':
                    self.tokens.append(('RPAREN', ')'))
                    self.pos += 1
                    continue
                if ch == ',':
                    self.tokens.append(('COMMA', ','))
                    self.pos += 1
                    continue
                
                # Bilinmeyen karakter
                raise SyntaxError(f"Bilinmeyen karakter: {ch}")
            
            self.tokens.append(('EOF', None))
        
        def get_tokens(self):
            return self.tokens
    
    class Parser:
        def __init__(self, tokens):
            self.tokens = tokens
            self.pos = 0
        
        def peek(self):
            return self.tokens[self.pos][0]
        
        def current(self):
            return self.tokens[self.pos]
        
        def advance(self):
            self.pos += 1
        
        def match(self, token_type):
            if self.peek() == token_type:
                self.advance()
                return True
            return False
        
        def expect(self, token_type):
            if self.peek() == token_type:
                self.advance()
                return True
            raise SyntaxError(f"Beklenen {token_type}, bulundu {self.peek()}")
        
        def parse(self):
            """Programı ayrıştır ve ifadeler listesi döndür."""
            expressions = []
            while self.peek() != 'EOF':
                # Boş ifadeleri atla (ardışık SEP'ler)
                while self.peek() == 'SEP':
                    self.advance()
                if self.peek() == 'EOF':
                    break
                expr = self.parse_expression()
                expressions.append(expr)
                # İfade sonrası SEP'leri atla
                while self.peek() == 'SEP':
                    self.advance()
            return expressions
        
        def parse_expression(self):
            return self.parse_assignment()
        
        def parse_assignment(self):
            # Atama: ident = expression
            if self.peek() == 'IDENT':
                ident_token = self.current()
                self.advance()
                if self.peek() == 'ASSIGN':
                    self.advance()
                    value = self.parse_expression()
                    return ('assign', ident_token[1], value)
                else:
                    # Atama değil, geriye sar ve expression olarak parse et
                    self.pos -= 1
            return self.parse_add_sub()
        
        def parse_add_sub(self):
            left = self.parse_mul_div_mod()
            while self.peek() in ('PLUS', 'MINUS'):
                op = self.current()[0]
                self.advance()
                right = self.parse_mul_div_mod()
                left = ('binop', op, left, right)
            return left
        
        def parse_mul_div_mod(self):
            left = self.parse_power()
            while self.peek() in ('MUL', 'DIV', 'MOD'):
                op = self.current()[0]
                self.advance()
                right = self.parse_power()
                left = ('binop', op, left, right)
            return left
        
        def parse_power(self):
            left = self.parse_unary()
            if self.peek() == 'POWER':
                self.advance()
                right = self.parse_power()  # Sağdan birleşim
                left = ('binop', 'POWER', left, right)
            return left
        
        def parse_unary(self):
            if self.peek() in ('PLUS', 'MINUS'):
                op = self.current()[0]
                self.advance()
                operand = self.parse_unary()
                return ('unary', op, operand)
            return self.parse_primary()
        
        def parse_primary(self):
            if self.peek() == 'NUMBER':
                val = self.current()[1]
                self.advance()
                return ('number', val)
            if self.peek() == 'IDENT':
                name = self.current()[1]
                self.advance()
                return ('var', name)
            if self.peek() == 'FUNC':
                func_name = self.current()[1]
                self.advance()
                self.expect('LPAREN')
                args = []
                if self.peek() != 'RPAREN':
                    args.append(self.parse_expression())
                    while self.peek() == 'COMMA':
                        self.advance()
                        args.append(self.parse_expression())
                self.expect('RPAREN')
                return ('call', func_name, args)
            if self.peek() == 'LPAREN':
                self.advance()
                expr = self.parse_expression()
                self.expect('RPAREN')
                return expr
            raise SyntaxError(f"Beklenmeyen token: {self.peek()}")
    
    class Interpreter:
        def __init__(self):
            self.variables = {}
        
        def eval(self, node):
            node_type = node[0]
            
            if node_type == 'number':
                return node[1]
            
            if node_type == 'var':
                name = node[1]
                if name not in self.variables:
                    raise NameError(f"Tanımsız değişken: {name}")
                return self.variables[name]
            
            if node_type == 'assign':
                name = node[1]
                value = self.eval(node[2])
                self.variables[name] = value
                return value
            
            if node_type == 'binop':
                op = node[1]
                left = self.eval(node[2])
                right = self.eval(node[3])
                
                if op == 'PLUS':
                    return left + right
                if op == 'MINUS':
                    return left - right
                if op == 'MUL':
                    return left * right
                if op == 'DIV':
                    if right == 0:
                        raise ZeroDivisionError("Sıfıra bölme")
                    return left / right
                if op == 'MOD':
                    if right == 0:
                        raise ZeroDivisionError("Sıfıra bölme")
                    return left % right
                if op == 'POWER':
                    return left ** right
                
                raise SyntaxError(f"Bilinmeyen işleç: {op}")
            
            if node_type == 'unary':
                op = node[1]
                operand = self.eval(node[2])
                if op == 'PLUS':
                    return +operand
                if op == 'MINUS':
                    return -operand
                raise SyntaxError(f"Bilinmeyen tekli işleç: {op}")
            
            if node_type == 'call':
                func_name = node[1]
                args = [self.eval(arg) for arg in node[2]]
                
                if func_name == 'min':
                    if not args:
                        raise SyntaxError("min en az 1 argüman gerektirir")
                    return min(args)
                if func_name == 'max':
                    if not args:
                        raise SyntaxError("max en az 1 argüman gerektirir")
                    return max(args)
                if func_name == 'abs':
                    if len(args) != 1:
                        raise SyntaxError("abs tam 1 argüman gerektirir")
                    return abs(args[0])
                
                raise NameError(f"Bilinmeyen fonksiyon: {func_name}")
            
            raise SyntaxError(f"Bilinmeyen düğüm türü: {node_type}")
        
        def run(self, expressions):
            result = None
            for expr in expressions:
                result = self.eval(expr)
            return result
    
    # Tokenize
    tokenizer = Tokenizer(program)
    tokens = tokenizer.get_tokens()
    
    # Parse
    parser = Parser(tokens)
    expressions = parser.parse()
    
    # Eğer hiç ifade yoksa None döndür
    if not expressions:
        return None
    
    # Interpret
    interpreter = Interpreter()
    return interpreter.run(expressions)
