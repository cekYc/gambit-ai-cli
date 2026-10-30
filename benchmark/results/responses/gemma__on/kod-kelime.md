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

*   Function signature: `top_k_words(text: str, k: int) -> list[tuple[str, int]]`.
    *   Input: A string `text` and an integer `k`.
    *   Output: A list of tuples containing the top `k` most frequent words and their counts.

        1.  Case-insensitive (convert to lowercase).
        2.  Words consist of consecutive letters (including Turkish characters like ç, ğ, ı, ö, ş, ü).
        3.  Numbers and punctuation are not part of words.
        4.  Sorting:
            *   Primary: Frequency (descending).
            *   Secondary: Alphabetical order (ascending) if frequencies are equal.
        5.  If `k` is greater than the number of unique words, return all words.

    *   Need to extract only letters. Regular expressions (`re` module) are best for this.
    *   The pattern should match sequences of characters that are considered "letters". In Python's `re` module with Unicode support (default in Python 3), `\w` includes digits and underscores, so we need something more specific like `[a-zA-Z]` but extended to include Turkish characters.
    *   Actually, a better way is using the regex pattern for "word characters" but excluding numbers/underscores, or simply finding all sequences of letters.
    *   The requirement says: "Kelime ardışık harflerden oluşur... rakamlar ve noktalama işaretleri kelimeye dahil değildir." This implies we should extract only alphabetic sequences.
    *   In Python's `re` module, `[a-zA-Z]` is English-only. To support Turkish characters (and other Unicode letters), I can use the property that a character is a letter using `char.isalpha()`.
    *   A robust way to find words: Use `re.findall(r'[a-z\u00c7\u00e7\u011f\u011f\u0131\u0131\u00f6\u00f6\u00f6\u00f6\u015f\u015f\u017e\u017e]+', text.lower())`? No, that's messy.
    *   Better way: Use `re.findall(r'[^\W\d_]+', text.lower(), re.UNICODE)`. Wait, `\w` includes digits and underscores. `[^\W\d_]` means "not (non-word or digit or underscore)". This effectively selects only letters in Unicode.
    *   Let's test the logic:
        `text = "Merhaba dünya! 123 merhaba."`
        `text.lower() -> "merhaba dünya! 123 merhaba."`
        Regex `[^\W\d_]+` on this string will find `['merhaba', 'dünya', 'merhaba']`. This is correct.

    *   Use `collections.Counter` to count frequencies.

    *   We need to sort by:
        1.  Count (descending): `-count`
        2.  Word (ascending): `word`
    *   Python's `sort` or `sorted` is stable. We can use a key function: `key=lambda item: (-item[1], item[0])`.

    ```python
    import re
    from collections import Counter

    def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
        # 1. Lowercase and find all words (only letters)
        # [^\W\d_] matches any Unicode character that is a letter
        words = re.findall(r'[^\W\d_]+', text.lower(), re.UNICODE)

        if not words:
            return []

        # 2. Count frequencies
        counts = Counter(words)

        # 3. Sort
        # Primary key: -count (descending), Secondary key: word (ascending)
        sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

        # 4. Return top k
        return sorted_items[:k]
    ```

    *   `text="Merhaba dünya! Merhaba, dünya, güneş."`, `k=2`
    *   Words: `['merhaba', 'dünya', 'merhaba', 'dünya', 'güneş']`
    *   Counts: `{'merhaba': 2, 'dünya': 2, 'güneş': 1}`
    *   Sorted items:
        - `('merhaba', 2)` vs `('dünya', 2)` -> Alphabetical order: `dünya` comes before `merhaba`? No, `d` < `m`. Wait. Let's check alphabetical order for "dünya" and "merhaba". 'd' is before 'm'. So `[('dünya', 2), ('merhaba', 2), ('güneş', 1)]`.
    *   Wait, the requirement says: "Sıralama: sayıya göre azalan; sayılar eşitse kelimeye göre alfabetik".
    *   Example check: `counts.items()` -> `[('merhaba', 2), ('dünya', 2), ('güneş', 1)]`.
    *   `sorted(..., key=lambda x: (-x[1], x[0]))`:
        - For `('merhaba', 2)`: `(-2, 'merhaba')`
        - For `('dünya', 2)`: `(-2, 'dünya')`
        - For `('güneş', 1)`: `(-1, 'güneş')`
    *   Sorting these tuples: `(-2, 'dünya') < (-2, 'merhaba') < (-1, 'güneş')`.
    *   Result: `[('dünya', 2), ('merhaba', 2), ('güneş', 1)]`. Correct.

    *   `re.findall(r'[^\W\d_]+', text.lower())` is very efficient for finding Unicode letters.
    *   Let's double check the "Turkish characters" requirement. `[^\W\d_]` in Python 3 with `re.UNICODE` (which is default) handles all Unicode letter categories correctly.

    ```python
    import re
    from collections import Counter

    def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
        # Find all sequences of characters that are letters (Unicode aware)
        # [^\W\d_] matches any character that is a letter (not non-word, not digit, not underscore)
        words = re.findall(r'[^\W\d_]+', text.lower())

        if not words:
            return []

        counts = Counter(words)

        # Sort by frequency descending (-x[1]) and then word ascending (x[0])
        sorted_words = sorted(counts.items(), key=lambda x: (-x[1], x[0]))

        return sorted_words[:k]
    ```

    *   `top_k_words(text, k)` signature? Yes.
    *   Lowercase? Yes (`text.lower()`).
    *   Turkish characters/Letters only? Yes (`re.findall(r'[^\W\d_]+', ...)`).
    *   No numbers/punctuation? Yes.
    *   Sort: Count desc, Word asc? Yes (`key=lambda x: (-x[1], x[0])`).
    *   k > unique words returns all? Yes (slicing `[:k]` handles this automatically in Python).

    One edge case: If the input string is empty or contains no letters. `re.findall` will return an empty list, `Counter` will be empty, `sorted_words` will be empty, and it returns `[]`. This is correct.

    Wait, let's verify `[^\W\d_]` behavior with Turkish characters like 'ı'.
    In Python:
    ```python
    import re
    re.findall(r'[^\W\d_]+', "Işığı gördüm!") # ['ı', 'şı', 'ğı', 'gördüm'] -> wait, no.
    # Actually \w includes letters, digits, and underscore.
    # [^\W] is equivalent to \w.
    # So [^\W\d_] means: (is a word character) AND (is not a digit) AND (is not an underscore).
    # This effectively leaves only characters in the 'Letter' category of Unicode.
    ```
    Let's test `re.findall(r'[^\W\d_]+', "Merhaba dünya! 123 merhaba.")`:
    `text.lower()` -> `"merhaba dünya! 123 merhaba."`
    `re.findall` -> `['merhaba', 'dünya', 'merhaba']`. Correct.

    Final check on sorting: "sayılar eşitse kelimeye göre alfabetik".
    If counts are equal, the word is used for comparison. Since we want ascending alphabetical order (a, b, c...), and Python's `sorted` sorts tuples element by element, using `( -count, word )` will sort count descending and then word ascending. This matches perfectly.

    ```python
    import re
    from collections import Counter

    def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
        # Find all words consisting only of letters (Unicode-aware)
        words = re.findall(r'[^\W\d_]+', text.lower())
        counts = Counter(words)
        # Sort by count descending (-x[1]) and then word ascending (x[0])
        return sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:k]
    ```

    Wait, one detail: `re.findall` with `[^\W\d_]+` might be slightly slower than a direct regex for letters if the text is massive, but it's the most robust way to handle all Unicode letters (including Turkish) without listing them manually. The prompt says "Kelime ardışık harflerden oluşur", which implies we want sequences of characters that are letters.

    One more check: `re.findall(r'[^\W\d_]+', text.lower())`
    If input is `"123-abc_def"`, it should return `['abc', 'def']`.
    `[^\W\d_]` on `_`: `_` is a word character (`\w`), so `\W` (non-word) doesn't match it. But the regex says "not digit and not underscore". So `_` is excluded. Correct.

    Final code structure:
    ```python
    import re
    from collections import Counter

    def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
        # Find all sequences of Unicode letters
        words = re.findall(r'[^\W\d_]+', text.lower())
        counts = Counter(words)
        # Sort by frequency (descending) and then alphabetically (ascending)
        return sorted(counts.items(), key=lambda x: (-x[1], x[0]))[:k]
    ```

    Wait, I should ensure `re` is imported inside the block if it's a single block requirement. The prompt asks for "Sadece Python kodunu tek bir ```python bloğu içinde ver". This usually implies everything needed to run the function.

    One small detail: In some environments, `\w` might behave differently depending on flags, but in Python 3, `re` is Unicode-aware by default. `[^\W\d_]` is a standard way to get "only letters".

    Let's double check the sorting requirement one last time.
    "Sıralama: sayıya göre azalan; sayılar eşitse kelimeye göre alfabetik (Python'un normal string sıralaması)."
    Example: `('apple', 5), ('banana', 5), ('cherry', 3)`
    `(-5, 'apple') < (-5, 'banana') < (-3, 'cherry')`. Correct.

    Final check on Turkish characters:
    `text = "Çiçekler çok güzeldir."`
    `words = ['çiçekler', 'çok', 'güzeldir']`
    This works perfectly with `[^\W\d_]+`.

## Cevap

```python
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Metni küçük harfe çevir ve sadece Unicode harflerden oluşan kelimeleri bul
    # [^\W\d_] ifadesi; kelime karakteri olup ( \w ), rakam olmayan (\d) 
    # ve alt çizgi olmayan (_) tüm karakterleri (yani sadece harfleri) seçer.
    words = re.findall(r'[^\W\d_]+', text.lower())
    
    if not words:
        return []
    
    # Kelimelerin frekanslarını hesapla
    counts = Counter(words)
    
    # Sıralama kriterleri:
    # 1. Sayıya göre azalan (-x[1])
    # 2. Kelimeye göre alfabetik (x[0])
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    # İlk k elemanı döndür (k, toplam kelimeden büyükse tamamını döner)
    return sorted_items[:k]
```

## Notlandırılan kod/komut

```
import re
from collections import Counter

def top_k_words(text: str, k: int) -> list[tuple[str, int]]:
    # Metni küçük harfe çevir ve sadece Unicode harflerden oluşan kelimeleri bul
    # [^\W\d_] ifadesi; kelime karakteri olup ( \w ), rakam olmayan (\d) 
    # ve alt çizgi olmayan (_) tüm karakterleri (yani sadece harfleri) seçer.
    words = re.findall(r'[^\W\d_]+', text.lower())
    
    if not words:
        return []
    
    # Kelimelerin frekanslarını hesapla
    counts = Counter(words)
    
    # Sıralama kriterleri:
    # 1. Sayıya göre azalan (-x[1])
    # 2. Kelimeye göre alfabetik (x[0])
    sorted_items = sorted(counts.items(), key=lambda x: (-x[1], x[0]))
    
    # İlk k elemanı döndür (k, toplam kelimeden büyükse tamamını döner)
    return sorted_items[:k]
```
