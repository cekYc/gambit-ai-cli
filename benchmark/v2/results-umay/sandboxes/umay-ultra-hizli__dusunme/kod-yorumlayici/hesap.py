import re

# Global symbol table for variables
_scope = {}

# --- Tokenizer ---
# Standard regex for tokens: numbers, identifiers, operators/parens, separators, comments
TOKEN_REGEX = re.compile(r'\s*([0-9]+\.[0-9]*|[0-9]+|\w+|[+\-*/%^()]|;|#.*|;?)\s*')

def tokenize(program: str) -> list[str]:
    """Program string to a list of meaningful tokens."""
    tokens = []
    # Use finditer to get matches and handle comments/separators
    for match in TOKEN_REGEX.finditer(program):
        token = match.group(1).strip()
        if not token: continue
        
        # Handle comments/separators separately, filtering out pure comments
        if token.startswith('#'):
            continue
        elif token == ';':
            pass
        else:
            tokens.append(token)
    return tokens

# --- Interpreter Logic ---

def apply_op(op: str, b: float, a: float) -> float:
    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': 
        if b == 0: raise ZeroDivisionError("division by zero")
        return a / b
    if op == '%': return a % b
    if op == '**': return a ** b
    raise SyntaxError(f"Bilinmeyen operatör: {op}")

def precedence(op: str) -> int:
    # Precedence: +, - (1), *, /, % (2), **(3)
    if op in ('+', '-'): return 1
    if op in ('*', '/', '%'): return 2
    if op == '**': return 3
    return 0

def is_right_associative(op: str) -> bool:
    return op == '**'

def evaluate_expression(tokens: list[str]) -> float:
    """Evaluates an expression using two stacks (values and operators)."""
    values = []
    ops = []

    def process_op():
        op = ops.pop()
        if len(values) < 2: 
             raise SyntaxError("Eksik operand")
        b = values.pop()
        a = values.pop()
        return apply_op(op, b, a)

    def handle_function(func_name: str, args: list[float]) -> float:
        if func_name == 'min': return min(args)
        if func_name == 'max': return max(args)
        if func_name == 'abs': return abs(args[0])
        raise NameError(f"Tanımsız fonksiyon: {func_name}")

    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # 1. Numbers
        try:
            values.append(float(token))
            i += 1
            continue
        except ValueError:
            pass
        
        # 2. Functions (min, max, abs)
        if token in ('min', 'max', 'abs'):
            i += 1
            if i >= len(tokens) or tokens[i] != '(': raise SyntaxError("Beklenen (")
            i += 1 # Skip '('
            
            args = []
            # Parse arguments until ')'
            start_arg_index = i
            while i < len(tokens) and tokens[i] != ')':
                try:
                    # Treat argument as a single expression to evaluate
                    arg_tokens = tokens[start_arg_index:i]
                    args.append(evaluate_expression(arg_tokens))
                except SyntaxError as e: 
                    raise SyntaxError(f"Fonksiyon argümanı söz dizimi hatası: {e}")
                i += 1
                start_arg_index = i
            
            if i >= len(tokens) or tokens[i] != ')': raise SyntaxError("Beklenen )")
            i += 1 # Skip ')'

            result = handle_function(token, args)
            values.append(result)
            continue
            
        # 3. Parentheses
        if token == '(': values.append(token)
        elif token == ')': 
            # Evaluate until matching '(' 
            while ops and ops[-1] != '(': 
                process_op()
            if not ops or ops[-1] != '(': raise SyntaxError("Eşleşmeyen parantez")
            ops.pop() # Pop '('
            continue
        
        # 4. Operators
        elif token in ('+', '-', '*', '/', '%', '**'):
            # Check for unary context
            is_unary = (i == 0) or tokens[i-1] in ('(', '+', '-', '*', '/', '%', '**')
            
            # If it's a unary minus and followed by a number or '(', we handle it implicitly by the structure
            # but we must ensure the token stream is clean.
            
            while ops and ops[-1] != '(' and (precedence(ops[-1]) > precedence(token) or 
                                                   (precedence(ops[-1]) == precedence(token) and not is_right_associative(token))):
                process_op()
            ops.append(token)
            i += 1
        
        # 5. Variables (Identifiers)
        elif token.isidentifier() and token not in ('min', 'max', 'abs'):
            if token not in _scope:
                raise NameError(f"Tanımsız değişken: {token}")
            values.append(_scope[token])
            i += 1
        
        else:
            raise SyntaxError(f"Bilinmeyen token veya sözdizimi hatası: {token}")

    # Finish remaining operators
    while ops: 
        if ops[-1] == '(': raise SyntaxError("Eşleşmeyen parantez")
        process_op()

    if len(values) != 1: 
        raise SyntaxError("İfade sonucu tek bir değer olmalı")
        
    return values[0]

# --- Main Function ---

def calistir(program: str) -> (float | None):
    """Yorumlayıcıyı çalıştırır ve son ifadenin değerini döndürür."""
    global _scope
    _scope = {}
    
    lines = program.splitlines()
    last_result = None
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Split by semicolon
        statements = [s.strip() for s in line.split(';') if s.strip()]
        
        for statement in statements:
            if '=' in statement:
                try:
                    var_name, expr_str = [s.strip() for s in statement.split('=', 1)]
                    if not var_name or not expr_str: raise SyntaxError("Geçersiz atama")
                    
                    tokens = tokenize(expr_str)
                    value = evaluate_expression(tokens)
                    _scope[var_name] = value
                    last_result = value
                except Exception as e:
                    if isinstance(e, NameError): raise e
                    if isinstance(e, ZeroDivisionError): raise e
                    # Propagate specific error messages without formatting the original error content
                    if str(e) == "İfade sonucu tek bir değer olmalı":
                        raise SyntaxError("Atama sırasında söz dizimi hatası: İfade sonucu tek bir değer olmalı")
                    raise SyntaxError(f"Atama sırasında söz dizimi hatası: {e}")
            else:
                # Expression evaluation (return value)
                try:
                    tokens = tokenize(statement)
                    value = evaluate_expression(tokens)
                    last_result = value
                except Exception as e:
                    if isinstance(e, NameError): raise e
                    if isinstance(e, ZeroDivisionError): raise e
                    # Propagate specific error messages without formatting the original error content
                    if str(e) == "İfade sonucu tek bir değer olmalı":
                        raise SyntaxError("İfade sırasında söz dizimi hatası: İfade sonucu tek bir değer olmalı")
                    raise SyntaxError(f"İfade sırasında söz dizimi hatası: {e}")

    return last_result
