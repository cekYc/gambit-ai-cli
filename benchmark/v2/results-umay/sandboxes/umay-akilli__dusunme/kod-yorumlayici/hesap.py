# hesap.py - Küçük bir hesap dili yorumlayıcısı

from typing import List, Optional, Union


class Token:
    """Token tipleri."""
    def __init__(self, type_: str, value: str, line: int, col: int):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.col})"


class Tokenizer:
    """Basit bir tokenizer: sayıları, tanımlayıcıları, operatörleri ayırır."""
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.text):
            return None
        return self.text[self.pos]
    
    def advance(self):
        if self.pos < len(self.text):
            ch = self.text[self.pos]
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
    
    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char() in ' \t\r':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() is not None and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        digits = []
        has_dot = False
        
        while self.current_char() is not None and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # ikinci nokta - sayı biter
                has_dot = True
            digits.append(self.current_char())
            self.advance()
        
        value = ''.join(digits)
        if has_dot:
            return Token('NUMBER', value, start_line, start_col)
        return Token('NUMBER', value, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line, start_col = self.line, self.col
        chars = []
        
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            chars.append(self.current_char())
            self.advance()
        
        value = ''.join(chars)
        return Token('IDENTIFIER', value, start_line, start_col)
    
    def read_operator(self) -> Token:
        start_line, start_col = self.line, self.col
        ch = self.current_char()
        
        # İki karakterli operatörler: **
        if ch == '*' and self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '*':
            self.advance()
            self.advance()
            return Token('OPERATOR', '**', start_line, start_col)
        
        # Tek karakterli operatörler ve noktalama
        single_chars = '+-*/%=;(),'
        if ch in single_chars:
            self.advance()
            if ch == ';':
                return Token('SEMICOLON', ';', start_line, start_col)
            elif ch == '(':
                return Token('LPAREN', '(', start_line, start_col)
            elif ch == ')':
                return Token('RPAREN', ')', start_line, start_col)
            elif ch == ',':
                return Token('COMMA', ',', start_line, start_col)
            elif ch == '=':
                return Token('ASSIGN', '=', start_line, start_col)
            else:
                return Token('OPERATOR', ch, start_line, start_col)
        
        # Bilinmeyen karakter
        self.advance()
        raise SyntaxError(f"Bilinmeyen karakter: {ch!r} (satır {start_line}, sütun {start_col})")
    
    def tokenize(self) -> List[Token]:
        while self.current_char() is not None:
            self.skip_whitespace()
            self.skip_comment()
            self.skip_whitespace()  # yorumdan sonra tekrar boşluk atla
            
            ch = self.current_char()
            if ch is None:
                break
            
            # Yeni satır token'ı oluştur
            if ch == '\n':
                self.tokens.append(Token('NEWLINE', '\n', self.line, self.col))
                self.advance()
                continue
            
            if ch.isdigit() or (ch == '.' and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()):
                self.tokens.append(self.read_number())
            elif ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier())
            else:
                self.tokens.append(self.read_operator())
        
        self.tokens.append(Token('EOF', '', self.line, self.col))
        return self.tokens

    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() is not None and self.current_char() != '\n':
                self.advance()
            # newline'ı atla (tokenize loop'unda yakalanacak)
            if self.current_char() == '\n':
                self.advance()

    def skip_whitespace(self):
        while self.current_char() is not None and self.current_char() in ' \t\r':
            self.advance()


class Parser:
    """Recursive descent parser with precedence climbing."""
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current(self) -> Token:
        return self.tokens[self.pos]
    
    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok
    
    def expect(self, type_: str, value: str = None) -> Token:
        tok = self.current()
        if tok.type != type_ or (value is not None and tok.value != value):
            expected = f"{type_}({value!r})" if value else type_
            raise SyntaxError(f"Beklenen {expected}, ama {tok.type}({tok.value!r}) bulundu (satır {tok.line}, sütun {tok.col})")
        return self.advance()
    
    def match(self, type_: str, value: str = None) -> bool:
        tok = self.current()
        if tok.type == type_ and (value is None or tok.value == value):
            self.advance()
            return True
        return False
    
    def parse(self) -> List['Expr']:
        """Programı bir ifade listesi olarak parse et."""
        exprs = []
        while self.current().type != 'EOF':
            # Boş satırları atla
            while self.match('NEWLINE'):
                pass
            
            if self.current().type == 'EOF':
                break
            
            expr = self.parse_assignment()
            exprs.append(expr)
            
            # Statement separator: ; veya NEWLINE
            if self.match('SEMICOLON'):
                continue
            if self.match('NEWLINE'):
                continue
            
            # Eğer EOF değilse ve separator da yoksa, hata
            if self.current().type != 'EOF':
                next_tok = self.current()
                if next_tok.type in ('NUMBER', 'IDENTIFIER') or \
                   (next_tok.type == 'OPERATOR' and next_tok.value in ('+', '-')) or \
                   (next_tok.type == 'LPAREN'):
                    raise SyntaxError(f"İfadeler arasına ';' veya yeni satır konulmalı (satır {next_tok.line}, sütun {next_tok.col})")
        return exprs
    
    def parse_assignment(self) -> 'Expr':
        """Assignment: identifier '=' assignment | additive"""
        # Lookahead: eğer identifier varsa ve sonrası '=' ise assignment
        tok = self.current()
        if tok.type == 'IDENTIFIER':
            # Peek next token
            if self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'ASSIGN':
                name_tok = self.advance()  # identifier
                self.expect('ASSIGN')
                value_expr = self.parse_assignment()  # sağdan birleşimli
                return AssignExpr(name_tok.value, value_expr, name_tok.line, name_tok.col)
        
        return self.parse_additive()
    
    def parse_additive(self) -> 'Expr':
        """additive: multiplicative (('+' | '-') multiplicative)*"""
        left = self.parse_multiplicative()
        
        while self.match('OPERATOR', '+') or self.match('OPERATOR', '-'):
            op = self.tokens[self.pos - 1].value
            right = self.parse_multiplicative()
            left = BinaryExpr(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> 'Expr':
        """multiplicative: unary (('*' | '/' | '%') unary)*"""
        left = self.parse_unary()
        
        while self.match('OPERATOR', '*') or self.match('OPERATOR', '/') or self.match('OPERATOR', '%'):
            op = self.tokens[self.pos - 1].value
            right = self.parse_unary()
            left = BinaryExpr(left, op, right)
        
        return left
    
    def parse_unary(self) -> 'Expr':
        """unary: ('+' | '-') unary | power"""
        if self.match('OPERATOR', '+') or self.match('OPERATOR', '-'):
            op = self.tokens[self.pos - 1].value
            operand = self.parse_unary()
            return UnaryExpr(op, operand)
        
        return self.parse_power()
    
    def parse_power(self) -> 'Expr':
        """power: primary ('**' power)?  (sağdan birleşimli)"""
        left = self.parse_primary()
        
        if self.match('OPERATOR', '**'):
            right = self.parse_unary()  # ** sonrası unary parse et (sağdan birleşimli için)
            left = BinaryExpr(left, '**', right)
        
        return left
    
    def parse_primary(self) -> 'Expr':
        """primary: NUMBER | IDENTIFIER | '(' expression ')' | function_call"""
        tok = self.current()
        
        if tok.type == 'NUMBER':
            self.advance()
            # Sayıyı int veya float olarak parse et
            if '.' in tok.value:
                return NumberExpr(float(tok.value), tok.line, tok.col)
            else:
                return NumberExpr(int(tok.value), tok.line, tok.col)
        
        if tok.type == 'IDENTIFIER':
            name = tok.value
            self.advance()
            
            # Fonksiyon çağrısı mı?
            if self.match('LPAREN'):
                args = []
                if not self.match('RPAREN'):
                    args.append(self.parse_assignment())  # argumanlar assignment da olabilir? Hayır, expression olmalı.
                    # Düzeltme: argumanlar expression (assignment değil)
                    # Ama parse_assignment da additive'e düşer, bu da expression'dır.
                    while self.match('COMMA'):
                        args.append(self.parse_assignment())
                    self.expect('RPAREN')
                return CallExpr(name, args, tok.line, tok.col)
            else:
                return VariableExpr(name, tok.line, tok.col)
        
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_assignment()
            self.expect('RPAREN')
            return expr
        
        raise SyntaxError(f"Beklenmeyen token: {tok.type}({tok.value!r}) (satır {tok.line}, sütun {tok.col})")


# AST Düğümleri
class Expr:
    pass

class NumberExpr(Expr):
    def __init__(self, value: Union[int, float], line: int, col: int):
        self.value = value
        self.line = line
        self.col = col

class VariableExpr(Expr):
    def __init__(self, name: str, line: int, col: int):
        self.name = name
        self.line = line
        self.col = col

class AssignExpr(Expr):
    def __init__(self, name: str, value: Expr, line: int, col: int):
        self.name = name
        self.value = value
        self.line = line
        self.col = col

class BinaryExpr(Expr):
    def __init__(self, left: Expr, op: str, right: Expr):
        self.left = left
        self.op = op
        self.right = right

class UnaryExpr(Expr):
    def __init__(self, op: str, operand: Expr):
        self.op = op
        self.operand = operand

class CallExpr(Expr):
    def __init__(self, name: str, args: List[Expr], line: int, col: int):
        self.name = name
        self.args = args
        self.line = line
        self.col = col


class Interpreter:
    """AST'yi değerlendirir."""
    def __init__(self):
        self.variables: dict = {}
    
    def evaluate(self, expr: Expr) -> Union[int, float, None]:
        if isinstance(expr, NumberExpr):
            return expr.value
        
        if isinstance(expr, VariableExpr):
            if expr.name not in self.variables:
                raise NameError(f"Tanımsız değişken: {expr.name}")
            return self.variables[expr.name]
        
        if isinstance(expr, AssignExpr):
            value = self.evaluate(expr.value)
            self.variables[expr.name] = value
            return value
        
        if isinstance(expr, BinaryExpr):
            left_val = self.evaluate(expr.left)
            right_val = self.evaluate(expr.right)
            return self.eval_binary(expr.op, left_val, right_val)
        
        if isinstance(expr, UnaryExpr):
            operand_val = self.evaluate(expr.operand)
            return self.eval_unary(expr.op, operand_val)
        
        if isinstance(expr, CallExpr):
            return self.eval_call(expr.name, [self.evaluate(arg) for arg in expr.args])
        
        raise RuntimeError(f"Bilinmeyen expression türü: {type(expr)}")
    
    def eval_binary(self, op: str, left: Union[int, float], right: Union[int, float]) -> Union[int, float]:
        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise ZeroDivisionError("Sıfıra bölme hatası")
            return left / right  # Python'da her zaman float
        if op == '%':
            if right == 0:
                raise ZeroDivisionError("Sıfıra bölme hatası (modulo)")
            return left % right
        if op == '**':
            return left ** right
        raise RuntimeError(f"Bilinmeyen binary operatör: {op}")
    
    def eval_unary(self, op: str, operand: Union[int, float]) -> Union[int, float]:
        if op == '+':
            return +operand
        if op == '-':
            return -operand
        raise RuntimeError(f"Bilinmeyen unary operatör: {op}")
    
    def eval_call(self, name: str, args: List[Union[int, float]]) -> Union[int, float]:
        if name == 'min':
            if not args:
                raise TypeError("min() en az 1 argüman bekler")
            return min(args)
        if name == 'max':
            if not args:
                raise TypeError("max() en az 1 argüman bekler")
            return max(args)
        if name == 'abs':
            if len(args) != 1:
                raise TypeError(f"abs() tam 1 argüman bekler, {len(args)} verildi")
            return abs(args[0])
        
        raise NameError(f"Bilinmeyen fonksiyon: {name}")


def calistir(program: str) -> Union[int, float, None]:
    """
    Hesap dili programını çalıştırır ve son ifadenin değerini döndürür.
    
    Args:
        program: Hesap dili kaynak kodu
    
    Returns:
        Son ifadenin değeri (int, float) veya hiç ifade yoksa None
    
    Raises:
        NameError: Tanımsız değişken veya fonksiyon
        ZeroDivisionError: Sıfıra bölme
        SyntaxError: Söz dizimi hatası
    """
    if not program or not program.strip():
        return None
    
    tokenizer = Tokenizer(program)
    tokens = tokenizer.tokenize()
    
    parser = Parser(tokens)
    exprs = parser.parse()
    
    if not exprs:
        return None
    
    interpreter = Interpreter()
    result = None
    for expr in exprs:
        result = interpreter.evaluate(expr)
    
    return result


# Test için main bloğu
if __name__ == "__main__":
    test_cases = [
        ("2 + 3", 5),
        ("2 * 3 + 4", 10),
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
        ("2 ** 3 ** 2", 512),  # sağdan birleşimli: 2 ** (3 ** 2) = 2 ** 9 = 512
        ("-2 ** 2", -4),  # -(2 ** 2) = -4
        ("2 ** -1", 0.5),
        ("x = 5", 5),
        ("x = 5; x + 3", 8),
        ("x = 2; y = 3; x * y", 6),
        ("min(3, 1, 4)", 1),
        ("max(3, 1, 4)", 4),
        ("abs(-5)", 5),
        ("3.5 + 2.1", 5.6),
        ("10 / 3", 10/3),
        ("10 % 3", 1),
        ("# yorum\n42", 42),
        ("", None),
        ("   ", None),
        ("x = 1; y = 2; x + y", 3),
        ("a = b = 3", 3),  # zincirli atama
        ("min(5, max(2, 3))", 3),
    ]
    
    print("Testler başlıyor...")
    for i, (code, expected) in enumerate(test_cases):
        try:
            result = calistir(code)
            if result == expected:
                print(f"✓ Test {i+1}: {code!r} => {result}")
            else:
                print(f"✗ Test {i+1}: {code!r} => {result} (beklenen: {expected})")
        except Exception as e:
            print(f"✗ Test {i+1}: {code!r} => HATA: {type(e).__name__}: {e}")
    
    # Hata testleri
    print("\nHata testleri:")
    error_cases = [
        ("x + 1", NameError),  # tanımsız değişken
        ("foo()", NameError),  # bilinmeyen fonksiyon
        ("1 / 0", ZeroDivisionError),
        ("1 % 0", ZeroDivisionError),
        ("2 +", SyntaxError),
        ("(1", SyntaxError),
        ("3 4", SyntaxError),
        ("2 $ 3", SyntaxError),
    ]
    
    for code, expected_error in error_cases:
        try:
            calistir(code)
            print(f"✗ Hata testi: {code!r} => Hata bekleniyordu ({expected_error.__name__})")
        except expected_error:
            print(f"✓ Hata testi: {code!r} => {expected_error.__name__} (beklendiği gibi)")
        except Exception as e:
            print(f"✗ Hata testi: {code!r} => Yanlış hata: {type(e).__name__}: {e}")
