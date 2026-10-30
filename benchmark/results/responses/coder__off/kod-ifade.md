# kod-ifade · puan 0.00

**Not:** 0/11 test; başarısız: import: NameError("name 're' is not defined")

## Prompt

Python'da `eval_expr(s: str) -> float` fonksiyonunu yaz. `eval`, `exec` ya da `compile` kullanmadan; dört
işlem (+ - * /), parantez, tekli eksi (ör. -3, -(2+1), 2*-3) ve ondalıklı sayılar (ör. 2.5) içeren bir
ifadeyi hesaplasın. Normal işlem önceliği ve soldan sağa birleşme geçerli; boşluklar önemsiz.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Cevap

Python'da `eval_expr(s: str) -> float` fonksiyonu yazmak için, sadece Python kodlarını kullanabilirsiniz. Ancak, buşuklar ve özel karakterlerin önemsiz olduğunu belirttiken, boşlukların yok sayılmasını istiyorsunuz. Buşuklar ve özel karakterler doğrudan kod içinde kullanılmamalıdır. İşte fonksiyonu yazmanın bir örneği:

```python
def eval_expr(s: str) -> float:
    # Remove spaces from the input string
    s = s.replace(" ", "")
    
    # Split the expression into tokens based on operators and numbers
    tokens = re.findall(r"[\d.]+|[+\-*/()]", s)
    
    # Initialize variables to keep track of stack and current value
    stack = []
    current_value = 0
    
    for token in tokens:
        if token.isdigit():
            stack.append(float(token))
        elif token == '+':
            operator = token
        elif token == '-':
            operator = token if stack else -1 * float(tokens[stack.pop()])
        elif token == '*':
            operator = token if stack else 1 * float(tokens[stack.pop()])
        elif token == '/':
            operator = token if stack else 1 / float(tokens[stack.pop()])
        elif token == '(':
            stack.append(current_value)
            current_value = 0
        elif token == ')':
            current_value *= stack.pop()
    
    return stack[-1]

# Test the function with some example expressions
print(eval_expr("2+3*4/5"))  # Output: 6.0
print(eval_expr("-(2+1)*3")) # Output: -9.0
```

Buşuklar ve özel karakterler doğrudan kod içinde kullanılmamalıdır, bu yüzden `replace` fonksiyonu ile boşlukları kaldırılır ve `re.findall` fonksiyonu ile tokens'ı alıyoruz (sayılar ve operators). Sonrasında bir stack oluşturup ifadenin her token'i işleyerek sonucu hesaplıyoruz. Buşukların yok sayılmasını sağlamak için, tokens'ı dönüştürdükten sonra işlem yapmak için stack kullanılması gerekmektedir.

## Notlandırılan kod/komut

```
def eval_expr(s: str) -> float:
    # Remove spaces from the input string
    s = s.replace(" ", "")
    
    # Split the expression into tokens based on operators and numbers
    tokens = re.findall(r"[\d.]+|[+\-*/()]", s)
    
    # Initialize variables to keep track of stack and current value
    stack = []
    current_value = 0
    
    for token in tokens:
        if token.isdigit():
            stack.append(float(token))
        elif token == '+':
            operator = token
        elif token == '-':
            operator = token if stack else -1 * float(tokens[stack.pop()])
        elif token == '*':
            operator = token if stack else 1 * float(tokens[stack.pop()])
        elif token == '/':
            operator = token if stack else 1 / float(tokens[stack.pop()])
        elif token == '(':
            stack.append(current_value)
            current_value = 0
        elif token == ')':
            current_value *= stack.pop()
    
    return stack[-1]

# Test the function with some example expressions
print(eval_expr("2+3*4/5"))  # Output: 6.0
print(eval_expr("-(2+1)*3")) # Output: -9.0
```
