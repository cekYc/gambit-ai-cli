import re

# --- Dil Tanımı ve Öncelikler ---
OPERATORS = { 
    '+': {'prec': 1, 'assoc': 'L'}, 
    '-': {'prec': 1, 'assoc': 'L'}, 
    '*': {'prec': 2, 'assoc': 'L'}, 
    '/': {'prec': 2, 'assoc': 'L'}, 
    '%': {'prec': 2, 'assoc': 'L'}, 
    '**': {'prec': 3, 'assoc': 'R'} 
}
FUNCTIONS = {'min': 'MIN', 'max': 'MAX', 'abs': 'ABS'}

# --- Tokenizer ---
def tokenize(program):
    # Yorumları ve boş satırları temizle
    program = re.sub(r'#.*', '', program)
    
    # Token ayırma: Sayılar (tam/ondalık, başında '-' olabilir), operatörler, parantezler, tanımlayıcılar.
    tokens = re.findall(r'\w+|[0-9.]+|[+\-*/%**()]|;', program)
    
    # Unary/Binary '-' ayrımı
    processed_tokens = []
    for i, token in enumerate(tokens):
        if token == '-':
            # Unary '-' kontrolü: if token başlangıçta veya bir operatör, açılış parantezi sonrasında geliyorsa unary'dir.
            # Ayrıca bir önceki token bir operand (sayı) değilse unary'dir.
            is_unary = (i == 0) or (tokens[i-1] in ['(', '+', '-', '*', '/', '%', '**'])
            
            if is_unary:
                # Eğer - işaretinden hemen sonra sayı varsa, negatif sayıyı tek token olarak birleştir.
                if i + 1 < len(tokens) and (tokens[i+1].replace('.', '', 1).isdigit() or (tokens[i+1].startswith('-') and tokens[i+1][1:].replace('.', '', 1).isdigit())): 
                    num_str = token + tokens[i+1]
                    i += 1
                    processed_tokens.append(num_str)
                else:
                    # Unary operatör olarak UMINUS token'ını kullan
                    processed_tokens.append("UMINUS") 
            else:
                # Binary '-' 
                processed_tokens.append(token)
        else:
            processed_tokens.append(token)
            
    return processed_tokens

# --- Parser (Shunting-Yard) ---
def shunting_yard(tokens):
    output_queue = []
    operator_stack = []

    for token in tokens:
        if token.replace('.', '', 1).isdigit() or (token.startswith('-') and token[1:].replace('.', '', 1).isdigit()):
            # Sayı
            output_queue.append(token)
        elif token in FUNCTIONS:
            # Fonksiyon
            operator_stack.append(token)
        elif token in OPERATORS:
            # Operatör
            op1 = token
            while operator_stack and operator_stack[-1] in OPERATORS:
                op2 = operator_stack[-1]
                op1_prec = OPERATORS[op1]['prec']
                op2_prec = OPERATORS[op2]['prec']
                op1_assoc = OPERATORS[op1]['assoc']

                # Soldan ilişkilendirme (L) veya öncelik düşükse, op2'yi çıkar.
                if (op1_prec < op2_prec) or (op1_prec == op2_prec and op1_assoc == 'L'):
                    output_queue.append(operator_stack.pop())
                else:
                    break
            operator_stack.append(op1)
        elif token == '(': 
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(': 
                output_queue.append(operator_stack.pop())
            if not operator_stack or operator_stack[-1] != '(': 
                raise SyntaxError("Uyumsuz parantez.")
            operator_stack.pop() # '(')
        elif token == ';':
            pass
        elif token.isalpha() or token.startswith('_'):
            # Tanımlayıcı (değişken veya fonksiyon)
            output_queue.append(token)
        else:
            raise SyntaxError(f"Bilinmeyen token: {token}")

    while operator_stack:
        op = operator_stack.pop()
        if op in ('(', ')'): 
            raise SyntaxError("Uyumsuz parantez.")
        output_queue.append(op)

    return output_queue

# --- RPN Değerlendirici ---
def evaluate_rpn(rpn_tokens, scope):
    stack = []

    for token in rpn_tokens:
        # Sayı kontrolü 
        if token.replace('.', '', 1).isdigit() or (token.startswith('-') and token[1:].replace('.', '', 1).isdigit()):
            stack.append(float(token))
        elif token == 'UMINUS':
            # Unary '-' operatörünü değerlendir
            if not stack: raise SyntaxError("UMINUS için operand gerekli.")
            x = stack.pop()
            stack.append(-x)
        elif token in OPERATORS:
            # Operatör (İkili)
            if len(stack) < 2: raise SyntaxError("Operatör için yeterli operand yok.")
            right = stack.pop()
            left = stack.pop()
            
            if token == '+': stack.append(left + right)
            elif token == '-': stack.append(left - right)
            elif token == '*': stack.append(left * right)
            elif token == '/': 
                if right == 0: raise ZeroDivisionError("Sıfıra bölme hatası.")
                stack.append(left / right)
            elif token == '%': stack.append(left % right)
            elif token == '**': stack.append(left ** right)
        elif token in FUNCTIONS:
            func_name = FUNCTIONS[token]
            if func_name == 'ABS':
                if len(stack) < 1: raise SyntaxError("abs için argüman gerekli.")
                x = stack.pop()
                stack.append(abs(x))
            elif func_name in ('MIN', 'MAX'):
                args = []
                while stack and isinstance(stack[-1], (int, float)):
                    args.append(stack.pop())
                if not args: raise SyntaxError("MIN/MAX için argüman gerekli.")
                if func_name == 'MIN': stack.append(min(args))
                else: stack.append(max(args))
        elif token in scope:
            # Değişken
            stack.append(scope[token])
        else:
            # Tanımlanmamış değişken veya fonksiyon
            raise NameError(f"Tanımsız: {token}")
            
    if len(stack) != 1: 
        raise SyntaxError("İfade tamamlanmadı veya fazla operand kaldı.")
    return stack[0]

# --- Ana Yürütme Fonksiyonu ---
def calistir(program: str) -> (float | int | None):
    # Scope, değişkenleri tutar
    scope = {}
    # Yorumları ve boş satırları filtrele
    lines = [line for line in program.split('\n') if line.strip() and not line.strip().startswith('#')]
    last_value = None
    
    for line in lines:
        line = line.strip().rstrip(';')
        if not line: continue
        
        if '=' in line:
            # --- ATAMA İŞLEMİ ---
            try:
                var_name, rhs_expr = line.split('=', 1)
                var_name = var_name.strip()
                rhs_expr = rhs_expr.strip()
                
                if not (var_name.isalpha() or var_name.startswith('_')): 
                    raise SyntaxError("Geçersiz değişken adı.")

                # Sağ Tarafı RPN'ye çevir ve değerlendir
                tokens = tokenize(rhs_expr)
                rpn = shunting_yard(tokens)
                result = evaluate_rpn(rpn, scope)
                
                # Değişkene ata ve son değeri güncelle
                scope[var_name] = result
                last_value = result
            except Exception as e:
                # Hata türlerini kontrol et ve fırlat
                if isinstance(e, ZeroDivisionError): raise ZeroDivisionError(str(e))
                if isinstance(e, NameError): raise NameError(str(e))
                if isinstance(e, SyntaxError): raise SyntaxError(str(e))
                raise SyntaxError(f"Atama sırasında beklenmedik hata: {e}")
        else:
            # --- SAF İFADE İŞLEMİ ---
            try:
                tokens = tokenize(line)
                rpn = shunting_yard(tokens)
                result = evaluate_rpn(rpn, scope)
                last_value = result
            except Exception as e:
                if isinstance(e, ZeroDivisionError): raise ZeroDivisionError(str(e))
                if isinstance(e, NameError): raise NameError(str(e))
                if isinstance(e, SyntaxError): raise SyntaxError(str(e))
                raise SyntaxError(f"İfade değerlendirme sırasında beklenmedik hata: {e}")

    return last_value
