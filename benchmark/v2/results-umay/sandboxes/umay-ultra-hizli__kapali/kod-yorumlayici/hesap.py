import re

def calistir(program: str) -> any:
    """Küçük bir hesap dilini yorumlar ve son ifadenin değerini döndürür. eval, exec, compile, ast yasaktır."""
    lines = [line.split('#', 1)[0].strip() for line in program.splitlines() if line.strip() and not line.strip().startswith('#')]
    env = {}
    last_result = None

    # Fonksiyon tanımları
    def min(args): return min(args)
    def max(args): return max(args)
    def abs(x): return abs(x)

    token_regex = r'[a-zA-Z_][a-zA-Z0-9]*|\d+\.\d+|\d+|[+\-*/%**()]|[;,]' 
    
    def tokenize(expression):
        return re.findall(token_regex, expression)

    precedence = {
        '+': 1, '-': 1, 
        '*': 2, '/': 2, '%': 2, 
        '**': 3
    }

    def is_number(token):
        try:
            float(token)
            return True
        except ValueError: return False

    # Unary operatör kontrolü (token'dan önceki token'a bakarak)
    def is_unary(token, prev_token):
        return token in ('+', '-') and (prev_token is None or prev_token in '([{,')

    # --- Shunting-Yard Algoritması (Infix -> RPN) ---
    def shunting_yard(tokens):
        output_queue = []
        operator_stack = []
        
        for i, token in enumerate(tokens):
            prev_token = tokens[i-1] if i > 0 else None
            
            if token in env: # Değişken
                output_queue.append(token)
            elif is_number(token):
                output_queue.append(token)
            elif token in ['min', 'max', 'abs']: # Fonksiyon
                operator_stack.append(token)
            elif token == '(': 
                operator_stack.append(token)
            elif token == ')': 
                while operator_stack and operator_stack[-1] != '(': 
                    output_queue.append(operator_stack.pop())
                if not operator_stack or operator_stack[-1] != '(': raise SyntaxError("Eşleşmeyen parantez")
                operator_stack.pop() # '(' çıkar
            elif token in precedence:
                # Binary operatörler
                while (operator_stack and operator_stack[-1] != '(' and 
                       precedence.get(operator_stack[-1], 0) >= precedence[token]):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)
            elif token in ('+', '-'): # Unary/Binary ayrımı
                if is_unary(token, prev_token):
                     output_queue.append(f"UNARY_{token}")
                else:
                    # Binary operatör (öncelik kontrolü burada yapılır)
                    while (operator_stack and operator_stack[-1] != '(' and 
                           precedence.get(operator_stack[-1], 0) >= precedence[token]):
                        output_queue.append(operator_stack.pop())
                    operator_stack.append(token)
            else:
                raise SyntaxError(f"Bilinmeyen token: {token}")
        
        while operator_stack: 
            op = operator_stack.pop()
            if op == '(' or op == ')': raise SyntaxError("Eşleşmeyen parantez")
            output_queue.append(op)
        return output_queue

    # --- RPN Hesaplama ---
    def evaluate_rpn(rpn_tokens, env):
        stack = []
        for token in rpn_tokens:
            if is_number(token):
                stack.append(float(token))
            elif token in env:
                stack.append(env[token])
            elif token in ['min', 'max', 'abs']:
                if token == 'abs':
                    if len(stack) < 1: raise SyntaxError("Abs için argüman bekleniyor")
                    val = stack.pop()
                    stack.append(abs(val))
                elif token == 'min' or token == 'max':
                    args = []
                    while len(stack) > 0 and stack[-1] not in ['min', 'max']:
                        args.append(stack.pop())
                    args.reverse()
                    if len(args) < 1: raise SyntaxError(f"{token} için argüman bekleniyor")
                    if token == 'min': stack.append(min(args))
                    else: stack.append(max(args))
            elif token in precedence:
                op = token
                if op == '+': stack.append(apply_op(op, stack.pop(), stack.pop()))
                elif op == '-': stack.append(apply_op(op, stack.pop(), stack.pop()))
                elif op == '*': stack.append(apply_op(op, stack.pop(), stack.pop()))
                elif op == '/': stack.append(apply_op(op, stack.pop(), stack.pop()))
                elif op == '%': stack.append(apply_op(op, stack.pop(), stack.pop()))
                elif op == '**': stack.append(apply_op(op, stack.pop(), stack.pop()))
            elif token.startswith("UNARY_"): # Unary operatörler
                op = token.split('_')[1]
                if op == '-':
                    val = stack.pop()
                    stack.append(-val)
                elif op == '+':
                    val = stack.pop()
                    stack.append(val)
            else:
                raise SyntaxError(f"Tanımsız öğe: {token}")
        
        if len(stack) != 1: raise SyntaxError("İfade tamamlanmadı.")
        return stack[0]

    # --- Ana Çalıştırma Döngüsü ---
    for line in lines:
        line = line.strip()
        if not line: continue
        
        # Atama
        if '=' in line and line.count('=') == 1:
            var_name, expression_str = [p.strip() for p in line.split('=', 1)]
            tokens = tokenize(expression_str)
            try:
                rpn = shunting_yard(tokens)
                current_value = evaluate_rpn(rpn, env)
                env[var_name] = current_value
                last_result = current_value
            except Exception as e:
                raise e
        
        # İfade
        else:
            tokens = tokenize(line)
            if not tokens: continue
            try:
                rpn = shunting_yard(tokens)
                last_result = evaluate_rpn(rpn, env)
            except Exception as e:
                raise e

    return last_result
