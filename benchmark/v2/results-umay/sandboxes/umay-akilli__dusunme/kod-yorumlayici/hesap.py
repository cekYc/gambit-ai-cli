"""
Küçük bir hesap dilini yorumlayan `calistir` fonksiyonu.
`eval`, `exec`, `compile`, `ast` kullanmadan yazılmıştır.
"""

from typing import Optional, List, Tuple, Union


class Token:
    __slots__ = ('type', 'value', 'pos')
    
    def __init__(self, type_: str, value: str, pos: int):
        self.type = type_
        self.value = value
        self.pos = pos
    
    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, {self.pos})'


class Lexer:
    """Basit bir lexer: program string'ini token'lara böler."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.len = len(text)
    
    def peek(self) -> str:
        if self.pos < self.len:
            return self.text[self.pos]
        return ''
    
    def advance(self) -> str:
        ch = self.peek()
        self.pos += 1
        return ch
    
    def skip_whitespace(self):
        while self.pos < self.len and self.text[self.pos] in ' \t\r':
            self.pos += 1
    
    def skip_comment(self):
        if self.peek() == '#':
            while self.pos < self.len and self.text[self.pos] != '\n':
                self.pos += 1
    
    def read_number(self) -> Token:
        start = self.pos
        has_dot = False
        while self.pos < self.len:
            ch = self.text[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == '.' and not has_dot:
                has_dot = True
                self.pos += 1
            else:
                break
        value = self.text[start:self.pos]
        if has_dot:
            return Token('NUMBER', float(value), start)
        return Token('NUMBER', int(value), start)
    
    def read_identifier(self) -> Token:
        start = self.pos
        while self.pos < self.len:
            ch = self.text[self.pos]
            if ch.isalnum() or ch == '_':
                self.pos += 1
            else:
                break
        value = self.text[start:self.pos]
        if value in ('min', 'max', 'abs'):
            return Token('FUNCTION', value, start)
        return Token('IDENTIFIER', value, start)
    
    def next_token(self) -> Optional[Token]:
        self.skip_whitespace()
        self.skip_comment()
        self.skip_whitespace()
        
        if self.pos >= self.len:
            return None
        
        ch = self.peek()
        
        if ch == '\n' or ch == ';':
            self.advance()
            return Token('SEPARATOR', ch, self.pos - 1)
        
        if ch.isdigit():
            return self.read_number()
        
        if ch.isalpha() or ch == '_':
            return self.read_identifier()
        
        if ch == '=':
            self.advance()
            return Token('ASSIGN', '=', self.pos - 1)
        
        if ch == '(':
            self.advance()
            return Token('LPAREN', '(', self.pos - 1)
        
        if ch == ')':
            self.advance()
            return Token('RPAREN', ')', self.pos - 1)
        
        if ch == ',':
            self.advance()
            return Token('COMMA', ',', self.pos - 1)
        
        if ch == '*':
            self.advance()
            if self.peek() == '*':
                self.advance()
                return Token('POWER', '**', self.pos - 2)
            return Token('MUL', '*', self.pos - 1)
        
        if ch == '/':
            self.advance()
            return Token('DIV', '/', self.pos - 1)
        
        if ch == '%':
            self.advance()
            return Token('MOD', '%', self.pos - 1)
        
        if ch == '+':
            self.advance()
            return Token('PLUS', '+', self.pos - 1)
        
        if ch == '-':
            self.advance()
            return Token('MINUS', '-', self.pos - 1)
        
        self.advance()
        raise SyntaxError(f'Bilinmeyen karakter: {ch!r}')
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            tok = self.next_token()
            if tok is None:
                break
            tokens.append(tok)
        tokens.append(Token('EOF', '', self.pos))
        return tokens


class Parser:
    """Recursive descent parser with precedence climbing."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0] if tokens else None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None
    
    def expect(self, type_: str) -> Token:
        if self.current and self.current.type == type_:
            tok = self.current
            self.advance()
            return tok
        raise SyntaxError(f'Beklenen {type_}, bulundu {self.current}')
    
    def match(self, *types: str) -> bool:
        return self.current is not None and self.current.type in types
    
    def parse(self):
        statements = []
        while self.current and self.current.type != 'EOF':
            if self.current.type == 'SEPARATOR':
                self.advance()
                continue
            stmt = self.parse_statement()
            statements.append(stmt)
            while self.current and self.current.type == 'SEPARATOR':
                self.advance()
        return statements
    
    def parse_statement(self):
        if self.current and self.current.type == 'IDENTIFIER':
            saved_pos = self.pos
            name_tok = self.current
            self.advance()
            if self.current and self.current.type == 'ASSIGN':
                self.advance()
                expr = self.parse_expression()
                return ('assign', name_tok.value, expr)
            self.pos = saved_pos
            self.current = self.tokens[self.pos]
        
        expr = self.parse_expression()
        return ('expr', expr)
    
    def parse_expression(self):
        left = self.parse_term()
        while self.match('PLUS', 'MINUS'):
            op = self.current.type
            self.advance()
            right = self.parse_term()
            left = ('binop', op, left, right)
        return left
    
    def parse_term(self):
        left = self.parse_unary()
        while self.match('MUL', 'DIV', 'MOD'):
            op = self.current.type
            self.advance()
            right = self.parse_unary()
            left = ('binop', op, left, right)
        return left
    
    def parse_unary(self):
        if self.match('PLUS', 'MINUS'):
            op = self.current.type
            self.advance()
            operand = self.parse_unary()
            return ('unary', op, operand)
        return self.parse_power()
    
    def parse_power(self):
        left = self.parse_primary()
        if self.match('POWER'):
            self.advance()
            right = self.parse_unary()  # Sağ taraf unary olabilir (2 ** -1)
            left = ('binop', 'POWER', left, right)
        return left
    
    def parse_primary(self):
        if not self.current:
            raise SyntaxError('Beklenmeyen program sonu')
        
        tok = self.current
        
        if tok.type == 'NUMBER':
            self.advance()
            return ('number', tok.value)
        
        if tok.type == 'IDENTIFIER':
            self.advance()
            # Fonksiyon çağrısı mı kontrol et
            if self.current and self.current.type == 'LPAREN':
                func_name = tok.value
                self.advance()  # '('
                args = []
                if not self.match('RPAREN'):
                    args.append(self.parse_expression())
                    while self.match('COMMA'):
                        self.advance()
                        args.append(self.parse_expression())
                self.expect('RPAREN')
                return ('call', func_name, args)
            return ('var', tok.value)
        
        if tok.type == 'FUNCTION':
            func_name = tok.value
            self.advance()
            self.expect('LPAREN')
            args = []
            if not self.match('RPAREN'):
                args.append(self.parse_expression())
                while self.match('COMMA'):
                    self.advance()
                    args.append(self.parse_expression())
            self.expect('RPAREN')
            return ('call', func_name, args)
        
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        
        raise SyntaxError(f'Geçersiz sözdizimi: {tok}')


class Interpreter:
    """AST'yi yorumlar ve değerlendirir."""
    
    def __init__(self):
        self.variables = {}
    
    def eval(self, node):
        if node is None:
            return None
        
        ntype = node[0]
        
        if ntype == 'number':
            return node[1]
        
        if ntype == 'var':
            name = node[1]
            if name not in self.variables:
                raise NameError(f"Tanımsız değişken: '{name}'")
            return self.variables[name]
        
        if ntype == 'unary':
            op = node[1]
            val = self.eval(node[2])
            if op == 'PLUS':
                return +val
            elif op == 'MINUS':
                return -val
        
        if ntype == 'binop':
            op = node[1]
            left = self.eval(node[2])
            right = self.eval(node[3])
            
            if op == 'PLUS':
                return left + right
            elif op == 'MINUS':
                return left - right
            elif op == 'MUL':
                return left * right
            elif op == 'DIV':
                if right == 0:
                    raise ZeroDivisionError('Sıfıra bölme')
                return left / right
            elif op == 'MOD':
                if right == 0:
                    raise ZeroDivisionError('Sıfıra bölme')
                return left % right
            elif op == 'POWER':
                return left ** right
        
        if ntype == 'call':
            func_name = node[1]
            args = [self.eval(arg) for arg in node[2]]
            
            if func_name == 'abs':
                if len(args) != 1:
                    raise TypeError(f'abs() 1 argüman bekler, {len(args)} verildi')
                return abs(args[0])
            elif func_name == 'min':
                if len(args) < 1:
                    raise TypeError('min() en az 1 argüman bekler')
                return min(args)
            elif func_name == 'max':
                if len(args) < 1:
                    raise TypeError('max() en az 1 argüman bekler')
                return max(args)
            else:
                raise NameError(f"Bilinmeyen fonksiyon: '{func_name}'")
        
        raise ValueError(f'Bilinmeyen node tipi: {ntype}')
    
    def execute(self, statements):
        last_value = None
        for stmt in statements:
            if stmt[0] == 'assign':
                _, name, expr = stmt
                value = self.eval(expr)
                self.variables[name] = value
                last_value = value
            elif stmt[0] == 'expr':
                _, expr = stmt
                last_value = self.eval(expr)
        return last_value


def calistir(program: str):
    """
    Hesap dilinde yazılmış programı çalıştırır ve son ifadenin değerini döndürür.
    
    Args:
        program: Hesap dili kaynak kodu (string)
    
    Returns:
        Son ifadenin değeri (int, float) veya None (hiç ifade yoksa)
    
    Raises:
        SyntaxError: Sözdizimi hatası durumunda
        NameError: Tanımsız değişken/fonksiyon durumunda
        ZeroDivisionError: Sıfıra bölme durumunda
    """
    if not program or not program.strip():
        return None
    
    lexer = Lexer(program)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    statements = parser.parse()
    
    if not statements:
        return None
    
    interpreter = Interpreter()
    return interpreter.execute(statements)


if __name__ == '__main__':
    test_cases = [
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
        ("x = 5; x * 2", 10),
        ("-2 ** 2", -4),
        ("2 ** -1", 0.5),
        ("2 ** 3 ** 2", 512),
        ("min(5, 3, 8)", 3),
        ("max(5, 3, 8)", 8),
        ("abs(-10)", 10),
        ("10 / 3", 10/3),
        ("10 % 3", 1),
        ("# yorum\n42", 42),
        ("", None),
        ("   ", None),
    ]
    
    for code, expected in test_cases:
        try:
            result = calistir(code)
            status = "OK" if result == expected else "FAIL"
            print(f'{status}: {code!r} => {result} (beklenen: {expected})')
        except Exception as e:
            print(f'ERROR: {code!r} => {type(e).__name__}: {e}')
    
    error_cases = [
        ("x + 1", NameError),
        ("1 / 0", ZeroDivisionError),
        ("2 +", SyntaxError),
        ("(1", SyntaxError),
        ("3 4", SyntaxError),
        ("2 $ 3", SyntaxError),
        ("foo()", NameError),
    ]
    
    for code, expected_error in error_cases:
        try:
            result = calistir(code)
            print(f'FAIL (beklenen hata): {code!r} => {result}')
        except Exception as e:
            status = "OK" if isinstance(e, expected_error) else "FAIL"
            print(f'{status}: {code!r} => {type(e).__name__}: {e}')
