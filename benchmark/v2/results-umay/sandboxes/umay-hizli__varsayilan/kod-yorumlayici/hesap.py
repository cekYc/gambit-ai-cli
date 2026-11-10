"""Kucuk bir hesap dilini yorumlayan calistir fonksiyonu."""


class _Token:
    __slots__ = ("kind", "value", "line", "col")

    def __init__(self, kind, value, line, col):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col


class _Tokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    def _error(self, msg):
        raise SyntaxError(f"{msg} (satir {self.line}, sutun {self.col})")

    def _peek(self):
        if self.pos < len(self.text):
            return self.text[self.pos]
        return ""

    def _advance(self):
        ch = self._peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokenize(self):
        tokens = []
        while self.pos < len(self.text):
            ch = self._peek()

            if ch in " \t\r\n":
                self._advance()
                continue

            if ch == "#":
                while self.pos < len(self.text) and self.text[self.pos] != "\n":
                    self._advance()
                continue

            if ch.isdigit() or ch == ".":
                tokens.append(self._scan_number())
                continue

            if ch.isalpha() or ch == "_":
                tokens.append(self._scan_ident())
                continue

            if ch in "+-*/%();=,":
                start_line, start_col = self.line, self.col
                self._advance()
                tokens.append(_Token(ch, ch, start_line, start_col))
                continue

            self._error(f"Gecersiz karakter: {ch!r}")

        return tokens

    def _scan_number(self):
        start_line, start_col = self.line, self.col
        num_chars = []
        dot_seen = False

        while self.pos < len(self.text):
            ch = self._peek()
            if ch.isdigit():
                num_chars.append(ch)
                self._advance()
            elif ch == "." and not dot_seen:
                dot_seen = True
                num_chars.append(ch)
                self._advance()
            else:
                break

        literal = "".join(num_chars)
        if literal == "." or literal.count(".") > 1:
            self._error("Gecersiz sayi literali")

        try:
            if dot_seen:
                value = float(literal)
            else:
                value = int(literal)
        except ValueError:
            self._error("Gecersiz sayi literali")

        return _Token("NUMBER", value, start_line, start_col)

    def _scan_ident(self):
        start_line, start_col = self.line, self.col
        chars = []
        while self.pos < len(self.text):
            ch = self._peek()
            if ch.isalnum() or ch == "_":
                chars.append(ch)
                self._advance()
            else:
                break
        return _Token("IDENT", "".join(chars), start_line, start_col)


class _Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _advance(self):
        tok = self._peek()
        self.pos += 1
        return tok

    def _expect(self, kind):
        tok = self._advance()
        if tok is None or tok.kind != kind:
            found = tok.kind if tok else "son"
            raise SyntaxError(
                f"Beklenmeyen simge: {found!r}, beklenilen: {kind!r} "
                f"(satir {tok.line if tok else '?'}, sutun {tok.col if tok else '?'})"
            )
        return tok

    def parse(self):
        stmts = []
        while self._peek() is not None:
            tok = self._peek()
            if tok.kind == ";":
                self._advance()
                continue
            stmts.append(self._parse_statement())
            if self._peek() is not None and self._peek().kind == ";":
                self._advance()
        return stmts

    def _parse_statement(self):
        tok = self._peek()
        if tok is None:
            raise SyntaxError("Beklenmeyen ifade sonu")

        if tok.kind == "IDENT":
            name_tok = self._advance()
            nxt = self._peek()
            if nxt is not None and nxt.kind == "=":
                self._advance()
                value = self._parse_expression()
                return ("assign", name_tok.value, value, name_tok.line, name_tok.col)
            if nxt is not None and nxt.kind == "IDENT":
                raise SyntaxError("Iki ifade arasinda islec eksik")
            self.pos -= 1
            return ("expr", self._parse_expression())

        return ("expr", self._parse_expression())

    def _parse_expression(self):
        return self._parse_sum()

    def _parse_sum(self):
        node = self._parse_term()
        while True:
            tok = self._peek()
            if tok is not None and tok.kind in ("+", "-"):
                op_tok = self._advance()
                right = self._parse_term()
                node = ("binop", op_tok.kind, node, right, op_tok.line, op_tok.col)
            else:
                break
        return node

    def _parse_term(self):
        node = self._parse_factor()
        while True:
            tok = self._peek()
            if tok is not None and tok.kind in ("*", "/", "%"):
                op_tok = self._advance()
                right = self._parse_factor()
                node = ("binop", op_tok.kind, node, right, op_tok.line, op_tok.col)
            else:
                break
        return node

    def _parse_factor(self):
        tok = self._peek()
        if tok is not None and tok.kind in ("+", "-"):
            op_tok = self._advance()
            operand = self._parse_factor()
            return ("unary", op_tok.kind, operand, op_tok.line, op_tok.col)
        return self._parse_power()

    def _parse_power(self):
        base = self._parse_primary()
        tok = self._peek()
        if tok is not None and tok.kind == "*" and self._peek_next_is_star():
            self._advance()
            self._advance()
            exp = self._parse_factor()
            return ("binop", "**", base, exp, tok.line, tok.col)
        return base

    def _peek_next_is_star(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1].kind == "*"
        return False

    def _parse_primary(self):
        tok = self._peek()
        if tok is None:
            raise SyntaxError("Beklenmeyen ifade sonu")

        if tok.kind == "NUMBER":
            self._advance()
            return ("number", tok.value, tok.line, tok.col)

        if tok.kind == "IDENT":
            name = tok.value
            line, col = tok.line, tok.col
            self._advance()
            nxt = self._peek()
            if nxt is not None and nxt.kind == "(":
                return self._parse_call(name, line, col)
            return ("var", name, line, col)

        if tok.kind == "(":
            self._advance()
            node = self._parse_expression()
            self._expect(")")
            return node

        found = tok.kind if tok.kind else "son"
        raise SyntaxError(
            f"Beklenmeyen simge: {found!r} "
            f"(satir {tok.line}, sutun {tok.col})"
        )

    def _parse_call(self, name, line, col):
        self._expect("(")
        args = []
        if self._peek() is not None and self._peek().kind != ")":
            while True:
                args.append(self._parse_expression())
                if self._peek() is not None and self._peek().kind == ",":
                    self._advance()
                    continue
                break
        self._expect(")")
        return ("call", name, args, line, col)


class _Evaluator:
    BUILTINS = {
        "min": min,
        "max": max,
        "abs": abs,
    }

    def __init__(self):
        self.env = {}
        self.last_value = None

    def eval(self, stmts):
        self.last_value = None
        for stmt in stmts:
            self.last_value = self._eval_stmt(stmt)
        return self.last_value

    def _eval_stmt(self, stmt):
        kind = stmt[0]
        if kind == "assign":
            _, name, value_node, _, _ = stmt
            self.env[name] = self._eval_node(value_node)
            return self.env[name]
        if kind == "expr":
            return self._eval_node(stmt[1])
        raise RuntimeError(f"Bilinmeyen ifade turu: {kind}")

    def _eval_node(self, node):
        kind = node[0]
        if kind == "number":
            return node[1]
        if kind == "var":
            name = node[1]
            if name not in self.env:
                raise NameError(f"Tanimlanmamis degisken: {name}")
            return self.env[name]
        if kind == "binop":
            _, op, left, right, _, _ = node
            l = self._eval_node(left)
            r = self._eval_node(right)
            if op == "+":
                return l + r
            if op == "-":
                return l - r
            if op == "*":
                return l * r
            if op == "/":
                if r == 0:
                    raise ZeroDivisionError("Sifira bolme")
                return l / r
            if op == "%":
                if r == 0:
                    raise ZeroDivisionError("Sifira bolme")
                return l % r
            if op == "**":
                return l ** r
            raise RuntimeError(f"Bilinmeyen islec: {op}")
        if kind == "unary":
            _, op, operand, _, _ = node
            val = self._eval_node(operand)
            if op == "+":
                return +val
            if op == "-":
                return -val
            raise RuntimeError(f"Bilinmeyen tekli islec: {op}")
        if kind == "call":
            _, name, args, _, _ = node
            if name not in self.BUILTINS:
                raise NameError(f"Bilinmeyen fonksiyon: {name}")
            fn = self.BUILTINS[name]
            evaluated = [self._eval_node(a) for a in args]
            if not evaluated:
                raise TypeError(f"{name} en az bir arguman bekliyor")
            return fn(*evaluated)
        raise RuntimeError(f"Bilinmeyen dugum turu: {kind}")


def calistir(program: str):
    """Kucuk hesap dilini yorumlayip son ifadenin degerini dondurur."""
    tokenizer = _Tokenizer(program)
    tokens = tokenizer.tokenize()
    parser = _Parser(tokens)
    stmts = parser.parse()
    evaluator = _Evaluator()
    return evaluator.eval(stmts)