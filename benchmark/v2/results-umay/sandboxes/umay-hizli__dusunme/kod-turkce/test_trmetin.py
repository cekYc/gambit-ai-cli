# -*- coding: utf-8 -*-
from trmetin import tr_lower, tr_upper, tr_sorted

# Test 1: I/İ dönüşümleri
assert tr_lower('ISTANBUL') == 'ıstanbul'
assert tr_upper('istanbul') == 'İSTANBUL'
assert tr_upper('çiğ köfte') == 'ÇİĞ KÖFTE'

# Test 2: Ascii normal
assert tr_lower('ABC') == 'abc'
assert tr_upper('abc') == 'ABC'

# Test 3: Sıralama
words = ['ankara','Elma','ördek','ayşe','1a','ığdır','İstanbul','çilek','A','a','üç','ab']
result = tr_sorted(words)
print('Sonuç:', result)
print('Orijinal:', words)
assert words == ['ankara','Elma','ördek','ayşe','1a','ığdır','İstanbul','çilek','A','a','üç','ab']

expected = ['1a','A','a','ab','ankara','ayşe','çilek','Elma','ördek','üç','ığdır','İstanbul']
assert result == expected, result

# Test 4: Önek kuralı
assert tr_sorted(['istan','istanbul']) == ['istan','istanbul']

# Test 5: Listede olmayan karakterler önce, Unicode sırası
assert tr_sorted(['!','a','#']) == ['!','#','a']

# Test 6: Boş liste
assert tr_sorted([]) == []

print('Tüm testler geçti')
