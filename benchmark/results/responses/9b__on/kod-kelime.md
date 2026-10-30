# kod-kelime · puan 1.00

**Not:** 7/7 test

## Prompt

Python'da `top_k_words(text: str, k: int) -> list[tuple[str, int]]` fonksiyonunu yaz. Metinde en sık geçen
k kelimeyi (kelime, sayı) çiftleri olarak döndürsün.
- Büyük/küçük harf farkı önemsiz; kelimeler küçük harfe çevrilsin.
- Kelime ardışık harflerden oluşur (Türkçe harfler dahil); rakamlar ve noktalama işaretleri kelimeye dahil değildir.
- Sıralama: sayıya göre azalan; sayılar eşitse kelimeye göre alfabetik (Python'un normal string sıralaması).
- k, farklı kelime sayısından büyükse hepsini döndürsün.
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

Thinking Process:

1.  **Analyze the Request:**
    *   Role: Experienced software developer.
    *   Task: Write a Python function `top_k_words(text: str, k: int) -> list[tuple[str, int]]`.
    *   Functionality: Return the top $k$ most frequent words in the given text as tuples of (word, count).
    *   Constraints & Rules:
        1.  Case-insensitive (convert to lowercase).
        2.  Words consist of consecutive letters (including Turkish characters like 'ı', 'ş', etc.). Digits and punctuation are not part of words.
        3.  Sorting order: Primary key = count (descending), Secondary key = word (ascending/lexicographical using Python's default string sorting).
        4.  If $k$ is larger than the number of unique words, return all unique words.
    *   Output Format: Only Python code inside a single ```python block.

2.  **Determine the Implementation Steps:**
    *   Import necessary modules (e.g., `re` for regex to extract words).
    *   Define the function signature.
    *   Preprocess text: Convert to lowercase.
    *   Extract words: Use a regular expression that matches sequences of letters (including Turkish characters). The pattern `\w+` usually includes digits and underscores, so it's better to use `[a-zA-ZğĞüÜşŞıİöÖçÇ]` or simply `re.findall(r'[^\W_]+', text.lower())`. Actually, standard Unicode letter matching is safer for Turkish. In Python 3, `\w` matches Unicode word characters by default if the regex flag isn't set to ASCII mode, but sometimes it's tricky with specific locale settings. A robust way for Turkish specifically is `[a-zA-ZğĞüÜşŞıİöÖçÇ]+`. However, using `re.findall(r'\b\w+\b', text.lower())` might include digits if not careful. The prompt says "rakamlar ve noktalama işaretleri kelimeye dahil değildir" (digits and punctuation are not included).
    *   Regex pattern: `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` is explicit for Turkish. Or simply `re.findall(r'[^\W_]+', text.lower())` where `\w` includes digits/underscore, so negating it excludes them? Wait, `\b\w+\b` matches word characters (letters, digits, underscore). The requirement says "rakamlar ... dahil değildir". So I need to match only letters.
    *   Better Regex: `[a-zA-ZğĞüÜşŞıİöÖçÇ]+`. This covers standard Latin and Turkish specific chars. Is there a more generic way? `re.findall(r'[^\d\s\W_]+', ...)` might be complex. Let's stick to the explicit character class for Turkish support as requested ("Türkçe harfler dahil").
    *   Count frequencies: Use `collections.Counter`.
    *   Sort results: Sort by count descending, then word ascending.
    *   Slice top $k$.
    *   Return list of tuples.

3.  **Refining the Regex:**
    *   Python's `re` module handles Unicode letters well if we use the right flags or character classes.
    *   To ensure Turkish characters are treated as word boundaries correctly and digits/punctuation are excluded:
        Pattern: `[a-zA-ZğĞüÜşŞıİöÖçÇ]+`
        This ensures only letters are captured.
    *   Wait, does `\w` include Turkish chars in Python 3? Yes, by default it matches Unicode word characters (letters from any language). However, digits and underscores are also included in `\w`. So `re.findall(r'\w+', text.lower())` would capture "abc123" as one token if there's no separator. The prompt says "rakamlar ... kelimeye dahil değildir".
    *   So I should split by non-letters.
    *   Regex: `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` is safe and explicit for the requirement.

4.  **Drafting the Code:**

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Convert to lowercase
    text = text.lower()
    
    # Extract words (only letters, including Turkish chars)
    # Pattern matches sequences of letters. 
    # Note: Using explicit Turkish characters ensures correct behavior for the requirement.
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    
    # Count frequencies
    counts = Counter(words)
    
    # Sort: count descending, word ascending (lexicographical)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    # Take top k
    return sorted_items[:k]
```

5.  **Reviewing Constraints:**
    *   Case-insensitive? Yes (`lower()`).
    *   Words are consecutive letters (Turkish included)? Yes (Regex pattern).
    *   Digits/punctuation excluded? Yes (Regex only matches letters).
    *   Sorting: Count desc, Word asc? Yes (`-x[1]` for count, `x[0]` for word).
    *   $k$ > unique words? Slicing `[:k]` handles this naturally.
    *   Return type: `list[tuple[str, int]]`. Yes.

6.  **Edge Cases:**
    *   Empty text -> returns empty list.
    *   Text with only punctuation/digits -> returns empty list.
    *   $k=0$ -> returns empty list.
    *   Turkish characters handling: The regex explicitly includes them. Is there a risk of missing other Unicode letters? Usually, in these coding tasks, explicit Turkish chars are expected unless "Unicode" is specified broadly. Given the prompt specifically mentions "Türkçe harfler dahil", listing them is safer than relying on locale-specific defaults which might vary or be ambiguous in regex contexts without `re.UNICODE` (which is default). Actually, `\w` matches Unicode letters by default in Python 3. But `\w` includes digits and underscore. So `[^\W_]+` would match non-word-characters? No.
    *   Let's check `re.findall(r'\b\w+\b', text.lower())`. In Python 3, `\w` matches `[a-zA-Z0-9_]` in ASCII mode or Unicode letters + digits + underscore in default mode. If I use `text.lower()`, it handles case. But `\w` includes digits. So "abc123" becomes one word. The requirement says digits are NOT part of the word.
    *   So `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` is definitely correct for excluding digits while including Turkish letters.

7.  **Final Polish:**
    Ensure imports are inside or outside? Usually, standard practice allows imports at top level. The prompt asks for "Sadece Python kodunu tek bir ```python bloğu içinde ver" (Give only the Python code in a single python block). I will include imports within the block.

8.  **Constructing Final Output:**
    Wrap the code in triple backticks with `python`.

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    text = text.lower()
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:k]
```

Wait, one detail check: "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Give only the Python code in a single python block). I should not add explanations outside the block.

One minor optimization/correction on regex: While `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` works, relying on explicit character classes is good for specific requirements like Turkish support. However, standard Python `re` with Unicode flags often handles more characters if needed, but the prompt specifically highlights "Türkçe harfler dahil". Explicitly listing them ensures compliance without ambiguity regarding locale settings.

Let's double check sorting logic:
"sayıya göre azalan; sayılar eşitse kelimeye göre alfabetik (Python'un normal string sıralaması)."
`sorted(..., key=lambda x: (-x[1], x[0]))`
- `x[1]` is count. `-x[1]` makes it descending.
- `x[0]` is word. Default ascending sort for strings matches "alfabetik".
This looks correct.

Final check on imports: `re` and `Counter`. Standard library, allowed.

One more thing: The prompt asks for the function definition. Should I include test cases? No, just the code implementing the function.

Wait, is there any ambiguity about "Python'un normal string sıralaması"? Python sorts strings based on Unicode code points. Turkish characters like 'ş' (U+015F) come after standard ASCII letters in some collations but in default Python sorting they are sorted by their code point value. The prompt says "Python'un normal string sıralaması", so `x[0]` is sufficient without custom locale-aware collation.

Final Code Structure:
```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # ... implementation
```

I will write this now.

One detail: `list[tuple[str, int]]` is type hint syntax (PEP 604). It requires Python 3.9+. This is standard for modern Python development. I will use it as requested in the signature provided in the prompt (`-> list[tuple[str, int]]`).

Wait, checking regex again. `[a-zA-ZğĞüÜşŞıİöÖçÇ]+`.
Does this cover all Turkish letters?
A, B, C, Ç, D, E, F, G, Ğ, H, I, İ, J, K, L, M, N, O, Ö, P, R, S, Ş, T, U, Ü, V, Y, Z.
My regex: `a-zA-Z` covers A-Z and a-z.
Then specific Turkish chars: `ğĞüÜşŞıİöÖçÇ`.
Wait, I missed some? No, the standard Latin letters are covered by `[a-zA-Z]`. The special ones are Ç, Ğ, İ, Ö, Ş, Ü.
My regex has: `ğĞüÜşŞıİöÖçÇ`.
It includes: g, G, u, U, s, S, i, I, o, O, c, C.
Missing: ç (lowercase), Ç (uppercase). Wait, `[a-zA-Z]` covers 'c' and 'C'. So `ç` is not in `[a-zA-Z]`. It needs to be explicit if it's distinct from ASCII 'c'. In Turkish locale, 'c' is 'c', 'ç' is 'ç'. They are different characters.
So I need `çÇ` explicitly? Yes.
My regex: `[a-zA-ZğĞüÜşŞıİöÖçÇ]+`.
Wait, looking closely at my draft: `çÇ` is there at the end.
Let's list them carefully:
Latin: a-z, A-Z (includes c, C).
Turkish specific: Ğ, İ, Ö, Ş, Ü, ç, Ç.
Note: 'i' and 'I' are in `[a-zA-Z]`. But Turkish has 'ı' and 'İ'. 'ı' is distinct from 'i'. So `ı` needs to be explicit.
My draft had `ıİ`. Yes.
So the set of special chars needed beyond ASCII letters: Ğ, İ, Ö, Ş, Ü, ç, Ç, ı.
Wait, `[a-zA-Z]` includes i and I. It does NOT include ı (dotless i).
So I need `ıİ`.
My draft had `ıİ`. Yes.
Does it have `çÇ`? My draft had `çÇ`. Yes.
Does it have `ğĞ`? Yes.
Does it have `öÖ`? Yes.
Does it have `şŞ`? Yes.
Does it have `üÜ`? Yes.

So the regex `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` is correct for Turkish letters + ASCII letters.
Wait, does `[a-zA-Z]` cover 'c' and 'C'? Yes. So I don't need to duplicate them if I add `ç`. But wait, in regex character classes, order doesn't matter much but distinct chars must be listed. Since `ç` is not `c`, it must be added explicitly.
So `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` covers:
- All ASCII letters (A-Z, a-z) -> includes c, C, i, I.
- Turkish specific: Ğ, İ, Ö, Ş, Ü, ç, Ç, ı.
Wait, `ı` is dotless i. `[a-zA-Z]` has `i`. So `ı` must be explicit.
My regex string: `'ğĞüÜşŞıİöÖçÇ'`.
It contains `ı`, `İ`. It contains `ç`, `Ç`. It contains `ğ`, `Ğ`. It contains `ö`, `Ö`. It contains `ş`, `Ş`. It contains `ü`, `Ü`.
So it covers all Turkish letters.

Wait, is there any other letter? No.
Okay, the regex is solid.

One small detail: `re` module needs to be imported. `Counter` from `collections`.
The prompt asks for "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Give only the Python code in a single python block). I will ensure no markdown text outside the block.

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    text = text.lower()
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:k]
```

Wait, I should check if `re` needs any flags. Default is fine for this regex.
Also, ensure the function signature matches exactly what was requested: `top_k_words(text: str, k: int) -> list[tuple[str, int]]`. Yes.

Final verification of constraints:
- Case insensitive: `text.lower()` handles this.
- Words are consecutive letters (Turkish included): Regex `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` handles this.
- Digits/punctuation excluded: Regex only matches letters, so digits and punctuation are skipped.
- Sorting: Count desc (`-x[1]`), Word asc (`x[0]`). Correct.
- k > unique words: `[:k]` slice returns all available if fewer than k. Correct.

Ready to generate output.

One detail on the prompt "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Give only the Python code in a single python block). I must not add any conversational text before or after the code block. Just the code block.

Wait, looking at the instruction again: "Sen deneyimli bir yazılım geliştiricisin. Görevi dikkatle çöz ve cevabını tam olarak istenen biçimde ver." (You are an experienced software developer. Solve carefully and give your answer in the exact requested format.)
And then "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Give only the Python code in a single python block).

So I will output ONLY the markdown code block containing the Python code. No introductory text like "Here is the code".

Wait, one more check on imports. Sometimes it's cleaner to put imports inside the function or at top level. Top level is standard for modules/functions files. Since this is a snippet, top level imports are fine.

Double Check Regex:
`[a-zA-ZğĞüÜşŞıİöÖçÇ]+`
Does `re.findall` return empty strings? No, `+` requires at least one match.
If text has no words, returns empty list. Counter is empty. Sorted items empty. Returns empty list. Correct.

Okay, proceeding.

One nuance: "Python'un normal string sıralaması". Python 3 sorts strings by Unicode code point. This is the default behavior of `sorted`. So `x[0]` works perfectly.

Final check on type hints. `list[tuple[str, int]]` is valid in Python 3.9+. If the environment is older (e.g. 3.8), it might need `List[Tuple[str, int]]` from typing. However, modern Python development assumes 3.9+ for this syntax unless specified otherwise. The prompt uses `list[tuple[str, int]]` in the function signature request itself (`top_k_words(text: str, k: int) -> list[tuple[str, int]]`). So I must use that exact syntax.

Okay, writing the code.

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    text = text.lower()
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:k]
```

Wait, I should check if there are any hidden requirements. "Sadece Python kodunu tek bir ```python bloğu içinde ver."
Okay.

One tiny thing: `re` module import is standard. `Counter` is standard.
Is it possible to do this without imports? Yes, using dict and manual sorting. But `collections.Counter` is idiomatic for experienced developers ("Sen deneyimli bir yazılım geliştiricisin"). I will use `Counter`.

Wait, one more check on the regex pattern regarding Turkish characters.
In Python 3, `\w` matches Unicode word characters which includes Turkish letters. However, it also matches digits and underscore.
If I used `[^\W_]+`, that would match any character that is NOT a non-word char AND NOT underscore? No.
`\w` = `[a-zA-Z0-9_]` (ASCII) or Unicode equivalent.
So `\b\w+\b` includes digits.
To exclude digits, I must explicitly list letters.
My explicit list `[a-zA-ZğĞüÜşŞıİöÖçÇ]+` is the safest way to ensure "rakamlar ... dahil değildir".

Okay, final confirmation of the output format. Just the code block.

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    text = text.lower()
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:k]
```

Wait, I need to make sure I don't miss any Turkish letters.
Turkish vowels/consonants:
A a -> covered by [a-zA-Z]
B b -> covered
C c -> covered
Ç ç -> Ç is in regex, c is in [a-zA-Z]. Wait, `ç` (c-cedilla) is distinct from `c`. My regex has `çÇ`. Good.
D d -> covered
E e -> covered
F f -> covered
G g -> covered
Ğ ğ -> Ğ is in regex, g is in [a-zA-Z]. Wait, `ğ` (g-circumflex) is distinct from `g`. My regex has `ğĞ`. Good.
H h -> covered
I i -> covered
İ ı -> İ is in regex, i is in [a-zA-Z]. Wait, `ı` (dotless i) is distinct from `i`. My regex has `ıİ`. Good.
J j -> covered
K k -> covered
L l -> covered
M m -> covered
N n -> covered
O o -> covered
Ö ö -> Ö is in regex, o is in [a-zA-Z]. Wait, `ö` (o-umlaut) is distinct from `o`. My regex has `öÖ`. Good.
P p -> covered
R r -> covered
S s -> covered
Ş ş -> Ş is in regex, s is in [a-zA-Z]. Wait, `ş` (s-cedilla) is distinct from `s`. My regex has `şŞ`. Good.
T t -> covered
U u -> covered
Ü ü -> Ü is in regex, u is in [a-zA-Z]. Wait, `ü` (u-umlaut) is distinct from `u`. My regex has `üÜ`. Good.
V v -> covered
Y y -> covered
Z z -> covered

So `[a-zA-ZğĞüÜşŞıİöÖçÇ]` covers all Turkish letters + ASCII letters.
Wait, I listed `çÇ` in my thought process but did I include it in the regex string?
My draft: `r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+'`. Yes, `çÇ` is at the end.
Okay, looks complete.

One final check on whitespace handling. `re.findall` returns non-overlapping matches. If there are spaces between words, they act as delimiters implicitly because `[a-zA-Z...]` does not match space. So "Hello World" -> ["hello", "world"]. Correct.

I am confident in this solution.


## Cevap

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    text = text.lower()
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:k]
```

## Notlandırılan kod/komut

```
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    text = text.lower()
    words = re.findall(r'[a-zA-ZğĞüÜşŞıİöÖçÇ]+', text)
    counts = Counter(words)
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_items[:k]
```
