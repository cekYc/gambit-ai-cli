import time
from onbellek import onbellekle

# 1. TTL
calls = []
@onbellekle(ttl=0.1, saat=time.monotonic)
def f(x):
    calls.append(x)
    return x * 2
assert f(1) == 2
assert calls == [1]
assert f(1) == 2
assert calls == [1]
time.sleep(0.11)
assert f(1) == 2
assert calls == [1, 1]
print('TTL OK')

# 2. Isimli arguman sirasi onemsiz
@onbellekle()
def g(a, b):
    return a + b
assert g(1, 2) == 3
assert g(b=2, a=1) == 3
print('KW order OK')

# 3. Hashlenemeyen argumanlar onbellenmez
@onbellekle()
def h(lst):
    return sum(lst)
assert h([1, 2, 3]) == 6
assert h([1, 2, 3]) == 6
print('Unhashable OK')

# 4. Her fonksiyonun onbellegi ayri
@onbellekle()
def p(x):
    return x
@onbellekle()
def q(x):
    return x * 10
assert p(5) == 5 and q(5) == 50
assert p.bilgi()['iska'] == 1
assert q.bilgi()['iska'] == 1
print('Per-function isolation OK')

# 5. temizle() kendi onbellegini bosaltilir
p(5)
assert p.bilgi()['isabet'] == 1
p.temizle()
assert p.bilgi()['isabet'] == 1  # temizle sadece cache'i temizler, sayaci sifirlamaz
assert p(5) == 5
assert p.bilgi()['isabet'] == 1  # temizlendigi icin tekrar isabet sayilmaz (iska artar)
assert p.bilgi()['iska'] == 2
print('temizle isolation OK')

# 6. __name__ ve docstring korunur
@onbellekle()
def fonk(x):
    '''Belgeleme.'''
    return x
assert fonk.__name__ == 'fonk'
assert fonk.__doc__ == 'Belgeleme.'
print('wraps OK')

print('TUM DOGRULAMALAR GECTI')