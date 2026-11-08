"""
küçük bir hesap dilini yorumlayan calistir(program: str) fonksiyonu.

Kurallar:
- İfadeler satır sonu veya ';' ile ayrılır.
- '#' ile yorumlar.
- Atama: ad = ifade (ad harf ya da _ ile başlar). Atamanın değeri atanan değerdir.
- Sayılar: int veya float; / her zaman float.
- İşçiler (+ önceliği düşükten yükseğe):
    + -  (binary, sola doğru)
    * / % (sola doğru)
    - +  (tekli, sağa doğru)
    **   (sağa doğru, tekli eksiden önce uygulanır: -2 ** 2 == -4)
- Fonksiyonlar: min(...), max(...), abs(x)
- Dönüş değeri: son çalıştırılan ifadenin (ya da atamanın) değeri; yoksa None.
- Hatalar: NameError, ZeroDivisionError, SyntaxError.
"""


class _SyntaxError(Exception):
    pass


class _Tokenizer:
    """Küçük karakter tabanlı tokenizer."""

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.n = len(text)

    def _skip_ws(self):
        while self.pos < self.n and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def peek(self) -> str:
        self._skip_ws()
        if self.pos < self.n:
            return self.text[self.pos]
        return ""

    def next(self) -> str:
        ch = self.peek()
        if self.pos < self.n:
            self.pos += 1
        return ch

    def number(self):
        start = self.pos
        has_dot = False
        while self.pos < self.n:
            ch = self.text[self.pos]
            if ch.isdigit():
                self.pos += 1
            elif ch == ".":
                if has_dot:
                    break
                has_dot = True
                self.pos += 1
            else:
                break
        return self.text[start:self.pos]

    def ident(self):
        start = self.pos
        while self.pos < self.n:
            ch = self.text[self.pos]
            if ch.isalpha() or ch == "_" or ch.isdigit():
                self.pos += 1
            else:
                break
        return self.text[start:self.pos]


class _Parser:
    """Öncelikli geçişli bir ifade ayrıştırıcı."""

    BIN_PREC = {
        "+": 1,
        "-": 1,
        "*": 2,
        "/": 2,
        "%": 2,
        "**": 3,
    }

    def __init__(self, tokenizer: _Tokenizer, env: dict):
        self.t = tokenizer
        self.env = env
        self.text = tokenizer.text
        self.n = len(self.text)

    def parse(self):
        self.t._skip_ws()
        if self.t.pos >= self.t.n:
            return None
        node = self.parse_expression(0)
        self.t._skip_ws()
        if self.t.pos < self.t.n:
            raise _SyntaxError("beklenmeyen karakter")
        return node

    def parse_expression(self, min_prec: int):
        # tekli + / - (sağa doğru)
        ch = self.t.peek()
        if ch in "+-":
            op = self.t.next()
            operand = self.parse_expression(self.BIN_PREC["**"] + 1)
            return ("unary", op, operand)

        # parantezli ifade veya sayı veya isim
        ch = self.t.peek()
        if ch == "(":
            self.t.next()
            node = self.parse_expression(0)
            if self.t.peek() != ")":
                raise _SyntaxError("eksik kapanan parantez")
            self.t.next()
        elif ch.isdigit():
            num = self.t.number()
            if not num:
                raise _SyntaxError("geçersiz sayı")
            node = ("num", num)
        elif ch.isalpha() or ch == "_":
            name = self.t.ident()
            if self.t.peek() == "(":
                node = self.parse_call(name)
            else:
                node = ("var", name)
        else:
            raise _SyntaxError("geçersiz ifade başlangıcı")

        # binary işçiler (solda doğru, ** hariç)
        while True:
            self.t._skip_ws()
            if self.t.pos + 1 < self.t.n and self.text[self.t.pos:self.t.pos+2] == "**":
                op = "**"
                self.t.pos += 2
            elif self.t.pos < self.n and self.text[self.t.pos] in "+-*/%":
                op = self.text[self.t.pos]
                self.t.pos += 1
            else:
                break

            prec = self.BIN_PREC[op]
            if prec < min_prec:
                self.t.pos -= len(op)
                break

            next_min = prec if op == "**" else prec + 1
            right = self.parse_expression(next_min)
            node = ("bin", op, node, right)

        return node

    def parse_call(self, name: str):
        self.t.next()  # '('
        args = []
        self.t._skip_ws()
        if self.t.peek() != ")":
            while True:
                args.append(self.parse_expression(0))
                self.t._skip_ws()
                if self.t.peek() == ",":
                    self.t.next()
                    continue
                break
        if self.t.peek() != ")":
            raise _SyntaxError("eksik kapanan parantez")
        self.t.next()  # ')'
        return ("call", name, args)


def _eval(node, env: dict):
    kind = node[0]

    if kind == "num":
        text = node[1]
        if "." in text:
            return float(text)
        return int(text)

    if kind == "var":
        name = node[1]
        if name not in env:
            raise NameError(f"ad tanımlı değil: {name}")
        return env[name]

    if kind == "unary":
        _, op, operand = node
        val = _eval(operand, env)
        if op == "-":
            return -val
        return +val

    if kind == "bin":
        _, op, left, right = node
        lv = _eval(left, env)
        rv = _eval(right, env)

        if op == "+":
            return lv + rv
        if op == "-":
            return lv - rv
        if op == "*":
            return lv * rv
        if op == "/":
            if rv == 0:
                raise ZeroDivisionError("sıfıra bölme")
            return lv / rv
        if op == "%":
            if rv == 0:
                raise ZeroDivisionError("sıfıra bölme")
            return lv % rv
        if op == "**":
            try:
                return lv ** rv
            except ZeroDivisionError:
                raise ZeroDivisionError("sıfıra bölme")
        raise _SyntaxError(f"bilinmeyen işleç: {op}")

    if kind == "call":
        _, name, args = node
        values = [_eval(a, env) for a in args]
        if name == "min":
            if not values:
                raise TypeError("min() en az bir argüman bekliyor")
            return min(values)
        if name == "max":
            if not values:
                raise TypeError("max() en az bir argüman bekliyor")
            return max(values)
        if name == "abs":
            if len(values) != 1:
                raise TypeError("abs() tek bir argüman bekliyor")
            return abs(values[0])
        raise NameError(f"bilinmeyen fonksiyon: {name}")

    raise _SyntaxError("geçersiz düğüm")


def calistir(program: str):
    """Küçük hesap dilini çalıştırır ve son ifadenin değerini döndürür."""
    env: dict = {}
    last = None

    # '#' ile yorumları satır bazlı temizle
    lines = program.split("\n")
    cleaned = []
    for line in lines:
        idx = line.find("#")
        if idx != -1:
            line = line[:idx]
        cleaned.append(line)
    source = "\n".join(cleaned)

    # ';' ve satır sonu ile böl; boş parçaları atla
    parts = source.replace(";", "\n").split("\n")
    for part in parts:
        expr_text = part.strip()
        if not expr_text:
            continue

        # Atama: ad = ifade
        if "=" in expr_text:
            eq = expr_text.find("=")
            name = expr_text[:eq].strip()
            value_text = expr_text[eq+1:].strip()
            if not name or not (name[0].isalpha() or name[0] == "_"):
                raise SyntaxError("geçersiz atama")
            for ch in name:
                if not (ch.isalpha() or ch == "_" or ch.isdigit()):
                    raise SyntaxError("geçersiz atama ismi")
            if not value_text:
                raise SyntaxError("eksik ifade")
            tokenizer = _Tokenizer(value_text)
            parser = _Parser(tokenizer, env)
            try:
                tree = parser.parse()
            except _SyntaxError as e:
                raise SyntaxError(str(e)) from None
            if tree is None:
                raise SyntaxError("eksik ifade")
            tokenizer._skip_ws()
            if tokenizer.pos < tokenizer.n:
                raise SyntaxError("beklenmeyen karakter")
            val = _eval(tree, env)
            env[name] = val
            last = val
            continue

        tokenizer = _Tokenizer(expr_text)
        parser = _Parser(tokenizer, env)
        try:
            tree = parser.parse()
        except _SyntaxError as e:
            raise SyntaxError(str(e)) from None
        if tree is None:
            continue
        last = _eval(tree, env)

    return last
