# hesap.py - Küçük bir hesap dili yorumlayıcısı
# eval, exec, compile, ast KULLANILMAZ

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class Token:
    type: str
    value: Union[str, float, int]
    pos: int


class Tokenizer:
    """Basit bir tokenizer: sayı, tanımlayıcı, operatör, parantez, noktalı virgül, yorum."""
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.len = len(text)
    
    def peek(self) -> str:
        if self.pos < self.len:
            return self.text[self.pos]
        return '\0'
    
    def advance(self) -> str:
        ch = self.peek()
        self.pos += 1
        return ch
    
    def skip_whitespace(self):
        while self.peek() in ' \t\r\n':
            self.advance()
    
    def read_number(self) -> Token:
        start = self.pos
        has_dot = False
        while True:
            ch = self.peek()
            if ch.isdigit():
                self.advance()
            elif ch == '.' and not has_dot:
                has_dot = True
                self.advance()
            else:
                break
        num_str = self.text[start:self.pos]
        if has_dot:
            value = float(num_str)
        else:
            value = int(num_str)
        return Token('NUMBER', value, start)
    
    def read_identifier(self) -> Token:
        start = self.pos
        ch = self.peek()
        if not (ch.isalpha() or ch == '_'):
            raise SyntaxError(f"Geçersiz tanımlayıcı başlangıcı: {ch}")
        self.advance()
        while True:
            ch = self.peek()
            if ch.isalnum() or ch == '_':
                self.advance()
            else:
                break
        name = self.text[start:self.pos]
        return Token('IDENT', name, start)
    
    def next_token(self) -> Optional[Token]:
        self.skip_whitespace()
        if self.pos >= self.len:
            return None
        
        ch = self.peek()
        
        # Yorum satırı
        if ch == '#':
            while self.peek() not in '\n\0':
                self.advance()
            return self.next_token()
        
        # Sayı
        if ch.isdigit():
            return self.read_number()
        
        # Tanımlayıcı / fonksiyon adı
        if ch.isalpha() or ch == '_':
            return self.read_identifier()
        
        # Operatörler ve noktalama
        self.advance()
        
        if ch == ';':
            return Token('SEMICOLON', ';', self.pos - 1)
        if ch == '(':
            return Token('LPAREN', '(', self.pos - 1)
        if ch == ')':
            return Token('RPAREN', ')', self.pos - 1)
        if ch == ',':
            return Token('COMMA', ',', self.pos - 1)
        if ch == '=':
            return Token('ASSIGN', '=', self.pos - 1)
        if ch == '+':
            return Token('PLUS', '+', self.pos - 1)
        if ch == '-':
            return Token('MINUS', '-', self.pos - 1)
        if ch == '*':
            if self.peek() == '*':
                self.advance()
                return Token('POWER', '**', self.pos - 2)
            return Token('MUL', '*', self.pos - 1)
        if ch == '/':
            return Token('DIV', '/', self.pos - 1)
        if ch == '%':
            return Token('MOD', '%', self.pos - 1)
        
        raise SyntaxError(f"Bilinmeyen karakter: {ch}")
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            tok = self.next_token()
            if tok is None:
                break
            tokens.append(tok)
        tokens.append(Token('EOF', None, self.pos))
        return tokens


# --- AST Düğümleri ---

class Expr:
    pass

@dataclass
class Number(Expr):
    value: Union[int, float]

@dataclass
class Variable(Expr):
    name: str

@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    expr: Expr

@dataclass
class Assign(Expr):
    name: str
    value: Expr

@dataclass
class Call(Expr):
    func: str
    args: List[Expr]


# --- Pratt Parser ---

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def peek(self) -> Token:
        return self.tokens[self.pos]
    
    def advance(self) -> Token:
        tok = self.peek()
        self.pos += 1
        return tok
    
    def expect(self, ttype: str) -> Token:
        tok = self.peek()
        if tok.type != ttype:
            raise SyntaxError(f"Beklenen {ttype}, bulundu {tok.type}")
        return self.advance()
    
    def parse(self) -> List[Expr]:
        exprs = []
        while self.peek().type != 'EOF':
            expr = self.parse_expression(0)
            exprs.append(expr)
            if self.peek().type == 'SEMICOLON':
                self.advance()
        return exprs
    
    def parse_expression(self, min_prec: int) -> Expr:
        left = self.parse_prefix()
        
        while True:
            tok = self.peek()
            prec = self.get_infix_precedence(tok.type)
            if prec < min_prec:
                break
            
            next_min_prec = prec + 1 if tok.type == 'POWER' else prec
            
            self.advance()
            right = self.parse_expression(next_min_prec)
            left = BinaryOp(left, tok.type, right)
        
        return left
    
    def get_infix_precedence(self, ttype: str) -> int:
        if ttype in ('PLUS', 'MINUS'):
            return 20
        if ttype in ('MUL', 'DIV', 'MOD'):
            return 30
        if ttype == 'POWER':
            return 50
        return -1
    
    def parse_prefix(self) -> Expr:
        tok = self.peek()
        
        if tok.type in ('PLUS', 'MINUS'):
            self.advance()
            expr = self.parse_prefix()
            return UnaryOp(tok.type, expr)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Expr:
        tok = self.peek()
        
        if tok.type == 'NUMBER':
            self.advance()
            return Number(tok.value)
        
        if tok.type == 'IDENT':
            name = tok.value
            self.advance()
            
            if self.peek().type == 'LPAREN':
                self.advance()
                args = []
                if self.peek().type != 'RPAREN':
                    while True:
                        args.append(self.parse_expression(0))
                        if self.peek().type == 'COMMA':
                            self.advance()
                        else:
                            break
                self.expect('RPAREN')
                return Call(name, args)
            
            if self.peek().type == 'ASSIGN':
                self.advance()
                value = self.parse_expression(0)
                return Assign(name, value)
            
            return Variable(name)
        
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression(0)
            self.expect('RPAREN')
            return expr
        
        raise SyntaxError(f"Beklenmeyen token: {tok.type}")


# --- Evaluator ---

class Evaluator:
    def __init__(self):
        self.vars: dict[str, Union[int, float]] = {}
    
    def eval(self, expr: Expr) -> Union[int, float]:
        if isinstance(expr, Number):
            return expr.value
        
        if isinstance(expr, Variable):
            if expr.name not in self.vars:
                raise NameError(f"Tanımsız değişken: {expr.name}")
            return self.vars[expr.name]
        
        if isinstance(expr, Assign):
            value = self.eval(expr.value)
            self.vars[expr.name] = value
            return value
        
        if isinstance(expr, UnaryOp):
            val = self.eval(expr.expr)
            if expr.op == 'PLUS':
                return +val
            if expr.op == 'MINUS':
                return -val
        
        if isinstance(expr, BinaryOp):
            left = self.eval(expr.left)
            right = self.eval(expr.right)
            
            if expr.op == 'PLUS':
                return left + right
            if expr.op == 'MINUS':
                return left - right
            if expr.op == 'MUL':
                return left * right
            if expr.op == 'DIV':
                if right == 0:
                    raise ZeroDivisionError("Sıfıra bölme")
                return left / right
            if expr.op == 'MOD':
                if right == 0:
                    raise ZeroDivisionError("Sıfıra bölme")
                return left % right
            if expr.op == 'POWER':
                return left ** right
        
        if isinstance(expr, Call):
            args = [self.eval(arg) for arg in expr.args]
            if expr.func == 'abs':
                if len(args) != 1:
                    raise TypeError(f"abs() 1 argüman bekler, {len(args)} verildi")
                return abs(args[0])
            if expr.func == 'min':
                if len(args) < 1:
                    raise TypeError("min() en az 1 argüman bekler")
                return min(args)
            if expr.func == 'max':
                if len(args) < 1:
                    raise TypeError("max() en az 1 argüman bekler")
                return max(args)
            raise NameError(f"Bilinmeyen fonksiyon: {expr.func}")
        
        raise RuntimeError(f"Bilinmeyen AST düğümü: {type(expr)}")
    
    def eval_program(self, exprs: List[Expr]) -> Optional[Union[int, float]]:
        result = None
        for expr in exprs:
            result = self.eval(expr)
        return result


def calistir(program: str) -> Optional[Union[int, float]]:
    """
    Küçük hesap dilini yorumlar ve son ifadenin değerini döndürür.
    
    Args:
        program: Hesap dili kaynak kodu
    
    Returns:
        Son ifadenin değeri (int, float) veya None (hiç ifade yoksa)
    
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
    exprs = parser.parse()
    
    if not exprs:
        return None
    
    evaluator = Evaluator()
    return evaluator.eval_program(exprs)


# --- Test / Demo ---
if __name__ == "__main__":
    test_cases = [
        ("2 + 3 * 4", 14),
        ("(2 + 3) * 4", 20),
        ("x = 5; x * 2", 10),
        ("-2 ** 2", -4),
        ("2 ** -1", 0.5),
        ("2 ** 3 ** 2", 512),
        ("min(3, 1, 4)", 1),
        ("max(3, 1, 4)", 4),
        ("abs(-5)", 5),
        ("10 / 3", 10/3),
        ("10 % 3", 1),
        ("# yorum\n42", 42),
        ("a = 1; b = 2; a + b", 3),
        ("", None),
        ("   ", None),
    ]
    
    for code, expected in test_cases:
        try:
            result = calistir(code)
            status = "✓" if result == expected else "✗"
            print(f"{status} calistir({code!r}) = {result} (beklenen: {expected})")
        except Exception as e:
            print(f"✗ calistir({code!r}) -> {type(e).__name__}: {e}")
    
    error_cases = [
        ("x + 1", NameError),
        ("1 / 0", ZeroDivisionError),
        ("2 +", SyntaxError),
        ("(1", SyntaxError),
        ("3 4", SyntaxError),
        ("2 $ 3", SyntaxError),
        ("foo()", NameError),
    ]
    print("\n--- Hata testleri ---")
    for code, exc_type in error_cases:
        try:
            calistir(code)
            print(f"✗ calistir({code!r}) -> hata bekleniyordu")
        except exc_type:
            print(f"✓ calistir({code!r}) -> {exc_type.__name__}")
        except Exception as e:
            print(f"✗ calistir({code!r}) -> {type(e).__name__}: {e} (beklenen: {exc_type.__name__})")