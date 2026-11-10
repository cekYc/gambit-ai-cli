"""Basit bir hesap dilini yorumlayan Python modülü."""

_variables = {}
_last_result = None

def _parse_number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def _tokenize(expr):
    tokens = []
    i = 0
    s = expr
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] == '#':
            while i < len(s) and s[i] != chr(10):
                i += 1
            continue
        if s[i].isdigit() or (s[i] == '-' and i + 1 < len(s) and (s[i+1].isdigit() or s[i+1] == '.')):
            start = i
            if s[i] == '-':
                i += 1
            while i < len(s) and (s[i].isdigit() or s[i] == '.'):
                i += 1
            num_str = s[start:i]
            if s[start] == '-' and not num_str[1:].replace('.', '', 1).isdigit():
                i = start
                tokens.append('-')
                continue
            tokens.append(_parse_number(num_str))
            continue
        if s[i] == '(':
            tokens.append('(')
            i += 1
            continue
        if s[i] == ')':
            tokens.append(')')
            i += 1
            continue
        if s[i].isalpha() or s[i] == '_':
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                i += 1
            name = s[start:i]
            tokens.append(name)
            continue
        if s[i] == '+':
            tokens.append('+')
            i += 1
            continue
        if s[i] == '-':
            tokens.append('-')
            i += 1
            continue
        if s[i] == '*':
            tokens.append('*')
            i += 1
            continue
        if s[i] == '/':
            tokens.append('/')
            i += 1
            continue
        if s[i] == '%':
            tokens.append('%')
            i += 1
            continue
        if s[i] == '^':
            tokens.append('**')
            i += 1
            continue
        if s[i] == '=':
            tokens.append('=')
            i += 1
            continue
        raise SyntaxError(f"Bilinmeyen karakter: '{s[i]}'")
    return tokens

def _parse_primary(tokens, pos):
    if pos >= len(tokens):
        raise SyntaxError("Eksik ifade")
    token = tokens[pos]
    if isinstance(token, (int, float)):
        return token, pos + 1
    if token == '(':
        result, pos = _parse_expression(tokens, pos + 1)
        if pos >= len(tokens) or tokens[pos] != ')':
            raise SyntaxError("Eksik kapalı parantez")
        return result, pos + 1
    if isinstance(token, str):
        if pos + 1 < len(tokens) and tokens[pos + 1] == '(':
            func_name = token
            if func_name == 'abs':
                arg_result = tokens[pos + 2] if pos + 2 < len(tokens) else 0
                if arg_result < 0:
                    return -arg_result, pos + 3
                return arg_result, pos + 3
            elif func_name == 'min':
                arg_result = tokens[pos + 2] if pos + 2 < len(tokens) else 0
                return arg_result, pos + 3
            elif func_name == 'max':
                arg_result = tokens[pos + 2] if pos + 2 < len(tokens) else 0
                return arg_result, pos + 3
        if token in _variables:
            return _variables[token], pos + 1
        raise NameError(f"Tanımsız değişken: '{token}'")
    raise SyntaxError(f"Beklenmedik token: {token}")

def _parse_factor(tokens, pos):
    left, pos = _parse_primary(tokens, pos)
    while pos < len(tokens):
        token = tokens[pos]
        if token == '**':
            pos += 1
            right, pos = _parse_factor(tokens, pos)
            left = left ** right
        elif token == '-':
            pos += 1
            right, pos = _parse_primary(tokens, pos)
            left = -right
        elif token == '+':
            pos += 1
            right, pos = _parse_primary(tokens, pos)
        else:
            break
    return left, pos

def _parse_term(tokens, pos):
    left, pos = _parse_factor(tokens, pos)
    while pos < len(tokens):
        token = tokens[pos]
        if token == '*':
            pos += 1
            right, pos = _parse_factor(tokens, pos)
            left = left * right
        elif token == '/':
            pos += 1
            right, pos = _parse_factor(tokens, pos)
            if right == 0:
                raise ZeroDivisionError("Sıfıra bölme")
            left = left / right
        elif token == '%':
            pos += 1
            right, pos = _parse_factor(tokens, pos)
            left = left % right
        else:
            break
    return left, pos

def _parse_expression(tokens, pos):
    left, pos = _parse_term(tokens, pos)
    while pos < len(tokens):
        token = tokens[pos]
        if token == '+':
            pos += 1
            right, pos = _parse_term(tokens, pos)
            left = left + right
        elif token == '-':
            pos += 1
            right, pos = _parse_term(tokens, pos)
            left = left - right
        else:
            break
    return left, pos

def _parse_assignment(tokens):
    global _last_result
    if len(tokens) < 3 or tokens[1] != '=':
        result, _ = _parse_expression(tokens, 0)
        _last_result = result
        return result
    var_name = tokens[0]
    if not isinstance(var_name, str):
        raise SyntaxError("Atamada değişken adı expected")
    if not (var_name[0].isalpha() or var_name[0] == '_'):
        raise SyntaxError(f"Değişken adı harf veya _ ile başlamalı: '{var_name}'")
    result, _ = _parse_expression(tokens[2:], 0)
    _variables[var_name] = result
    _last_result = result
    return result

def calistir(program):
    global _variables, _last_result
    _variables = {}
    _last_result = None
    if chr(10) in program:
        lines = program.split(chr(10))
        last_line = None
        for line in reversed(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                last_line = stripped
                break
        if last_line is None:
            return _last_result
        program = last_line
    if '#' in program:
        program = program[:program.index('#')]
    tokens = _tokenize(program)
    result = _parse_assignment(tokens)
    return _last_result

if __name__ == "__main__":
    print("Test 1:", calistir("5 + 3"))
    print("Test 2:", calistir("10 - 4"))
    print("Test 3:", calistir("6 * 7"))
    print("Test 4:", calistir("10 / 3"))
    print("Test 5:", calistir("2 ** 3"))
    print("Test 6:", calistir("-2 ** 2"))
    print("Test 7:", calistir("2 ** -1"))
    print("Test 8:", calistir("abs(-5)"))
    print("Test 9:", calistir("min(3, 7)"))
    print("Test 10:", calistir("max(3, 7)"))
    print("Test 11:", calistir("x = 5"))
    print("Test 12:", calistir("x + 3"))
    print("Test 13:", calistir("y = x * 2"))
    print("Test 14:", calistir("y + x"))
