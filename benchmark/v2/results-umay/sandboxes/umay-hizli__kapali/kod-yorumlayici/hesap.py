import math


class CalcError(Exception):
    pass


class NameError(CalcError):
    pass


class ZeroDivisionError(CalcError):
    pass


class SyntaxError(CalcError):
    pass


# ---------------------------------------------------------------------------
# 1. Lexer
# ---------------------------------------------------------------------------

class Token:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind, value, pos):
        self.kind = kind
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.kind!r}, {self.value!r}, {self.pos})"


def tokenize(text):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c == "#":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == ";":
            tokens.append(Token("SEMI", ";", i))
            i += 1
            continue
        if c == "(":
            tokens.append(Token("LPAREN", "(", i))
            i += 1
            continue
        if c == ")":
            tokens.append(Token("RPAREN", ")", i))
            i += 1
            continue
        if c == ",":
            tokens.append(Token("COMMA", ",", i))
            i += 1
            continue
        if c == "+":
            tokens.append(Token("PLUS", "+", i))
            i += 1
            continue
        if c == "-":
            tokens.append(Token("MINUS", "-", i))
            i += 1
            continue
        if c == "*":
            if i + 1 < n and text[i + 1] == "*":
                tokens.append(Token("POW", "**", i))
                i += 2
            else:
                tokens.append(Token("MUL", "*", i))
                i += 1
            continue
        if c == "/":
            tokens.append(Token("DIV", "/", i))
            i += 1
            continue
        if c == "=":
            tokens.append(Token("ASSIGN", "=", i))
            i += 1
            continue
        if c == "%":
            tokens.append(Token("MOD", "%", i))
            i += 1
            continue
        if c.isdigit() or c == ".":
            start = i
            dot_seen = False
            while i < n and (text[i].isdigit() or text[i] == "."):
                if text[i] == ".":
                    if dot_seen:
                        raise SyntaxError(f"Geçersiz sayı literal'i: {text[start:i+1]!r}")
                    dot_seen = True
                i += 1
            literal = text[start:i]
            try:
                value = float(literal) if dot_seen else int(literal)
            except ValueError:
                raise SyntaxError(f"Geçersiz sayı literal'i: {literal!r}")
            tokens.append(Token("NUMBER", value, start))
            continue
        if c.isalpha() or c == "_":
            start = i
            while i < n and (text[i].isalnum() or text[i] == "_"):
                i += 1
            word = text[start:i]
            tokens.append(Token("IDENT", word, start))
            continue
        raise SyntaxError(f"Beklenmeyen karakter: {c!r}")
    tokens.append(Token("EOF", None, n))
    return tokens


# ---------------------------------------------------------------------------
# 2. Parser / Evaluator (recursive descent)
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.vars = {}

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, kind):
        tok = self.peek()
        if tok.kind != kind:
            raise SyntaxError(
                f"'{kind}' bekleniyordu, '{tok.kind}' bulundu"
            )
        self.advance()
        return tok

    # ---------- expression / assignment ----------

    def parse_expression(self):
        tok = self.peek()
        if tok.kind == "IDENT" and self._looks_like_assignment():
            name = self.advance().value
            self.expect("ASSIGN")
            value = self.parse_expression()
            self.vars[name] = value
            return value
        return self.parse_or()

    def _looks_like_assignment(self):
        # IDENT '=' ...  (veya IDENT '=' direkt EOF/sonraki ifade baslangici)
        if self.pos + 1 >= len(self.tokens):
            return False
        return self.tokens[self.pos + 1].kind == "ASSIGN"

    def _expect_assign(self):
        tok = self.peek()
        if tok.kind != "ASSIGN":
            raise SyntaxError("Atama icin '=' bekleniyordu")
        self.advance()
        return tok

    # or: not present -> just and_expr
    def parse_or(self):
        return self.parse_add()

    def parse_add(self):
        node = self.parse_mul()
        while self.peek().kind in ("PLUS", "MINUS"):
            op = self.advance().kind
            right = self.parse_mul()
            if op == "PLUS":
                node = node + right
            else:
                node = node - right
        return node

    def parse_mul(self):
        node = self.parse_unary()
        while self.peek().kind in ("MUL", "DIV", "MOD"):
            op = self.advance().kind
            right = self.parse_unary()
            if op == "MUL":
                node = node * right
            else:
                    pass
            if op == "DIV":
                if right == 0:
                    raise ZeroDivisionError("sıfıra bölme")
                node = node / right
            elif op == "MOD":
                if right == 0:
                    raise ZeroDivisionError("sıfıra bölme (mod)")
                node = node % right
        return node

    def parse_unary(self):
        tok = self.peek()
        if tok.kind == "MINUS":
            self.advance()
            operand = self.parse_unary()
            return -operand
        if tok.kind == "PLUS":
            self.advance()
            return +self.parse_unary()
        return self.parse_pow()

    def parse_pow(self):
        base = self.parse_primary()
        if self.peek().kind == "POW":
            self.advance()
            exp = self.parse_unary()  # sag birlesim; tekli once uygulanir
            return base ** exp
        return base

    def parse_primary(self):
        tok = self.peek()
        if tok.kind == "NUMBER":
            self.advance()
            return tok.value
        if tok.kind == "IDENT":
            name = self.advance().value
            if self.peek().kind == "LPAREN":
                return self._call_builtin(name)
            if name not in self.vars:
                raise NameError(f"tanimsiz degisken: {name}")
            return self.vars[name]
        if tok.kind == "LPAREN":
            self.advance()
            val = self.parse_expression()
            self.expect("RPAREN")
            return val
        raise SyntaxError(f"ifade baslangici bekleniyordu, '{tok.kind}' bulundu")

    def _call_builtin(self, name):
        self.expect("LPAREN")
        args = []
        if self.peek().kind != "RPAREN":
            while True:
                args.append(self.parse_expression())
                if self.peek().kind == "COMMA":
                    self.advance()
                    continue
                break
        self.expect("RPAREN")
        if name == "min":
            if not args:
                raise SyntaxError("min en az bir arguman bekliyor")
            return min(args)
        if name == "max":
            if not args:
                raise SyntaxError("max en az bir arguman bekliyor")
            return max(args)
        if name == "abs":
            if len(args) != 1:
                raise SyntaxError("abs tek bir arguman bekliyor")
            return abs(args[0])
        raise NameError(f"bilinmeyen fonksiyon: {name}")


# ---------------------------------------------------------------------------
# 3. Public API
# ---------------------------------------------------------------------------

def calistir(program: str):
    """Kucuk hesap dilini yorulur ve son ifadenin degerini dondurur."""
    tokens = tokenize(program)
    parser = Parser(tokens)
    last = None
    while True:
        tok = parser.peek()
        if tok.kind == "EOF":
            break
        # Bos ifadeleri (sadece noktalı virgul) atla
        if tok.kind == "SEMI":
            parser.advance()
            continue
        last = parser.parse_expression()
        if parser.peek().kind == "SEMI":
            parser.advance()
        elif parser.peek().kind != "EOF":
            raise SyntaxError(f"Beklenmeyen jeton: {parser.peek().kind}")
    return last


if __name__ == "__main__":
    import sys
    data = sys.stdin.read()
    print(calistir(data))

