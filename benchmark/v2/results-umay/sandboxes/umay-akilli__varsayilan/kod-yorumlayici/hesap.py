import re
from typing import List, Optional, Union, Tuple

Number = Union[int, float]

class Token:
    __slots__ = ('type', 'value', 'pos')
    def __init__(self, type: str, value: str, pos: int):
        self.type = type
        self.value = value
        self.pos = pos
    def __repr__(self):
        return f'Token({self.type}, {self.value!r})'

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.length = len(text)
    
    def peek(self) -> str:
        if self.pos < self.length:
            return self.text[self.pos]
        return '\0'
    
    def advance(self) -> str:
        ch = self.peek()
        self.pos += 1
        return ch
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while self.pos < self.length:
            ch = self.peek()
            if ch in ' \t\r\n':
                self.advance()
                continue
            if ch == '#':
                while self.pos < self.length and self.peek() != '\n':
                    self.advance()
                continue
            if ch == ';':
                tokens.append(Token('SEMI', ';', self.pos))
                self.advance()
                continue
            if ch.isdigit() or ch == '.':
                start = self.pos
                has_dot = False
                while self.pos < self.length:
                    c = self.peek()
                    if c.isdigit():
                        self.advance()
                    elif c == '.' and not has_dot:
                        has_dot = True
                        self.advance()
                    else:
                        break
                num_str = self.text[start:self.pos]
                if num_str == '.':
                    raise SyntaxError(f'Syntax error at position {start}')
                if has_dot:
                    value = float(num_str)
                else:
                    value = int(num_str)
                tokens.append(Token('NUMBER', value, start))
                continue
            if ch.isalpha() or ch == '_':
                start = self.pos
                while self.pos < self.length:
                    c = self.peek()
                    if c.isalnum() or c == '_':
                        self.advance()
                    else:
                        break
                name = self.text[start:self.pos]
                if name in ('min', 'max', 'abs'):
                    tokens.append(Token('FUNC', name, start))
                else:
                    tokens.append(Token('NAME', name, start))
                continue
            if ch == '+':
                self.advance()
                if self.peek() == '+':
                    raise SyntaxError(f'Syntax error at position {self.pos-1}')
                tokens.append(Token('PLUS', '+', self.pos-1))
                continue
            if ch == '-':
                self.advance()
                tokens.append(Token('MINUS', '-', self.pos-1))
                continue
            if ch == '*':
                self.advance()
                if self.peek() == '*':
                    self.advance()
                    tokens.append(Token('POWER', '**', self.pos-2))
                else:
                    tokens.append(Token('MUL', '*', self.pos-1))
                continue
            if ch == '/':
                self.advance()
                tokens.append(Token('DIV', '/', self.pos-1))
                continue
            if ch == '%':
                self.advance()
                tokens.append(Token('MOD', '%', self.pos-1))
                continue
            if ch == '=':
                self.advance()
                tokens.append(Token('ASSIGN', '=', self.pos-1))
                continue
            if ch == '(':
                self.advance()
                tokens.append(Token('LPAREN', '(', self.pos-1))
                continue
            if ch == ')':
                self.advance()
                tokens.append(Token('RPAREN', ')', self.pos-1))
                continue
            if ch == ',':
                self.advance()
                tokens.append(Token('COMMA', ',', self.pos-1))
                continue
            raise SyntaxError(f'Syntax error at position {self.pos}')
        tokens.append(Token('EOF', '', self.pos))
        return tokens

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current = tokens[0]
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
    
    def expect(self, type: str) -> Token:
        if self.current.type != type:
            raise SyntaxError(f'Syntax error at position {self.current.pos}')
        tok = self.current
        self.advance()
        return tok
    
    def parse(self):
        statements = []
        while self.current.type != 'EOF':
            if self.current.type == 'SEMI':
                self.advance()
                continue
            stmt = self.parse_statement()
            statements.append(stmt)
            while self.current.type == 'SEMI':
                self.advance()
        return statements
    
    def parse_statement(self):
        if self.current.type == 'NAME':
            name = self.current.value
            name_pos = self.current.pos
            self.advance()
            if self.current.type == 'ASSIGN':
                self.advance()
                expr = self.parse_expression()
                return ('assign', name, expr, name_pos)
            else:
                self.pos -= 1
                self.current = self.tokens[self.pos]
                expr = self.parse_expression()
                return ('expr', expr)
        else:
            expr = self.parse_expression()
            return ('expr', expr)
    
    def parse_expression(self):
        return self.parse_add_sub()
    
    def parse_add_sub(self):
        left = self.parse_mul_div_mod()
        while self.current.type in ('PLUS', 'MINUS'):
            op = self.current.type
            self.advance()
            right = self.parse_mul_div_mod()
            left = ('binop', op, left, right)
        return left
    
    def parse_mul_div_mod(self):
        left = self.parse_unary()
        while self.current.type in ('MUL', 'DIV', 'MOD'):
            op = self.current.type
            self.advance()
            right = self.parse_unary()
            left = ('binop', op, left, right)
        return left
    
    def parse_unary(self):
        if self.current.type in ('PLUS', 'MINUS'):
            op = self.current.type
            self.advance()
            operand = self.parse_unary()
            return ('unary', op, operand)
        return self.parse_power()
    
    def parse_power(self):
        left = self.parse_primary()
        if self.current.type == 'POWER':
            self.advance()
            right = self.parse_unary()
            return ('binop', 'POWER', left, right)
        return left
    
    def parse_primary(self):
        tok = self.current
        if tok.type == 'NUMBER':
            self.advance()
            return ('num', tok.value)
        if tok.type == 'NAME':
            self.advance()
            return ('var', tok.value)
        if tok.type == 'FUNC':
            func_name = tok.value
            self.advance()
            self.expect('LPAREN')
            args = []
            if self.current.type != 'RPAREN':
                args.append(self.parse_expression())
                while self.current.type == 'COMMA':
                    self.advance()
                    args.append(self.parse_expression())
            self.expect('RPAREN')
            return ('call', func_name, args)
        if tok.type == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        raise SyntaxError(f'Syntax error at position {tok.pos}')

class Interpreter:
    def __init__(self):
        self.variables = {}
    
    def eval(self, node) -> Number:
        ntype = node[0]
        if ntype == 'num':
            return node[1]
        if ntype == 'var':
            name = node[1]
            if name not in self.variables:
                raise NameError(f"name '{name}' is not defined")
            return self.variables[name]
        if ntype == 'assign':
            _, name, expr, _ = node
            value = self.eval(expr)
            self.variables[name] = value
            return value
        if ntype == 'unary':
            _, op, operand = node
            val = self.eval(operand)
            if op == 'PLUS':
                return +val
            return -val
        if ntype == 'binop':
            _, op, left, right = node
            lval = self.eval(left)
            rval = self.eval(right)
            if op == 'PLUS':
                return lval + rval
            if op == 'MINUS':
                return lval - rval
            if op == 'MUL':
                return lval * rval
            if op == 'DIV':
                if rval == 0:
                    raise ZeroDivisionError('division by zero')
                return lval / rval
            if op == 'MOD':
                if rval == 0:
                    raise ZeroDivisionError('modulo by zero')
                return lval % rval
            if op == 'POWER':
                return lval ** rval
        if ntype == 'call':
            _, func_name, args = node
            arg_vals = [self.eval(arg) for arg in args]
            if func_name == 'abs':
                if len(arg_vals) != 1:
                    raise TypeError(f'abs() takes exactly one argument ({len(arg_vals)} given)')
                return abs(arg_vals[0])
            if func_name == 'min':
                if not arg_vals:
                    raise TypeError('min() requires at least one argument')
                return min(arg_vals)
            if func_name == 'max':
                if not arg_vals:
                    raise TypeError('max() requires at least one argument')
                return max(arg_vals)
            raise NameError(f"name '{func_name}' is not defined")
        raise ValueError(f'Unknown node type: {ntype}')
    
    def run(self, statements) -> Optional[Number]:
        result = None
        for stmt in statements:
            if stmt[0] == 'expr':
                result = self.eval(stmt[1])
            elif stmt[0] == 'assign':
                result = self.eval(stmt)
        return result

def calistir(program: str) -> Optional[Number]:
    lexer = Lexer(program)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    statements = parser.parse()
    interpreter = Interpreter()
    return interpreter.run(statements)
