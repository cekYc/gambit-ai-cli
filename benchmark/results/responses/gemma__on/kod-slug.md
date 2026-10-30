# kod-slug · puan 1.00

**Not:** 8/8 test

## Prompt

Python'da `tr_slug(text: str) -> str` fonksiyonunu yaz. Metni URL'de kullanılacak kısa ada (slug) çevirsin:
- Türkçe harfler dönüşsün: ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u; büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü) de aynı şekilde.
- Sonuç tamamen küçük harf olsun.
- Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun.
- Baştaki ve sondaki '-' karakterleri silinsin.
Örnek: tr_slug("Merhaba Dünya!") == "merhaba-dunya"
Sadece Python kodunu tek bir ```python bloğu içinde ver.

## Düşünme

*   Input: `text` (string).
    *   Output: `slug` (string).
    *   Requirements:
        1.  Convert Turkish characters to ASCII equivalents (ç $\to$ c, ğ $\to$ g, ı $\to$ i, ö $\to$ o, ş $\to$ s, ü $\to$ u) for both lowercase and uppercase.
        2.  Result must be entirely lowercase.
        3.  Non-alphanumeric characters (anything not a letter or digit) should be replaced by a single hyphen `-`.
        4.  Leading and trailing hyphens must be removed.

    *   `ç`, `Ç` $\to$ `c`
    *   `ğ`, `Ğ` $\to$ `g`
    *   `ı`, `İ` $\to$ `i` (Note: `İ` is tricky in Python's `.lower()` sometimes, better to handle explicitly or use a mapping).
    *   `ö`, `Ö` $\to$ `o`
    *   `ş`, `Ş` $\to$ `s`
    *   `ü`, `Ü` $\to$ `u`

    1.  Create a mapping dictionary for Turkish characters to ASCII equivalents.
    2.  Convert the input string to lowercase first? Or handle uppercase in the map? Let's do it step-by-step:
        a. Replace specific Turkish characters with their English counterparts (handling both cases).
        b. Convert everything to lowercase.
        c. Use regular expressions (`re`) to replace sequences of non-alphanumeric characters with a single hyphen.
        d. Strip hyphens from the start and end using `.strip('-')`.

    *   `text = "Merhaba Dünya!"`
    *   Step 1 (Mapping): `merhaba dunya!`
    *   Step 2 (Lowercase): `merhaba dunya!`
    *   Step 3 (Regex non-alphanumeric to `-`): `merhaba-dunya-`
    *   Step 4 (Strip `-`): `merhaba-dunya`

    Wait, let's check "İ". In Python: `"İ".lower()` is `'i'`. So standard `.lower()` works fine for most cases if we map the characters correctly.

    Mapping dictionary approach:
    ```python
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    ```

    Regex approach:
    `re.sub(r'[^a-z0-9]+', '-', text)` - This replaces any sequence of non-lowercase letters and digits with a single hyphen. Since we convert to lowercase first, this is efficient.

    *   Input: `"Merhaba Dünya!"`
    *   Replace Turkish chars: `merhaba dunya!` (Wait, I need to handle the mapping before or after lowercasing).
    *   Let's do it like this:
        1.  Map characters.
        2.  Lower case.
        3.  Regex replace non-alphanumeric with `-`.
        4.  Strip `-`.

    Wait, if I map `İ` to `i`, then `.lower()` is redundant for that char but safe. If I lowercase first, I need to handle the mapping of lowercase Turkish chars.

    Let's try:
    1. Lowercase input.
    2. Replace specific characters (`ç`, `ğ`, `ı`, `ö`, `ş`, `ü`).
    3. Regex replace non-alphanumeric with `-`.
    4. Strip `-`.

    Wait, if I lowercase first, "İ" becomes "i". If I have "I", it becomes "i". This is correct for slugs.

    ```python
    import re

    def tr_slug(text: str) -> str:
        # Mapping dictionary for Turkish characters to ASCII equivalents
        mapping = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        }

        # 1. Replace Turkish characters using the mapping
        for tr_char, ascii_char in mapping.items():
            text = text.replace(tr_char, ascii_char)

        # 2. Convert to lowercase
        text = text.lower()

        # 3. Replace non-alphanumeric sequences with a single hyphen
        # [^a-z0-9]+ matches one or more characters that are NOT a-z or 0-9
        text = re.sub(r'[^a-z0-9]+', '-', text)

        # 4. Strip leading and trailing hyphens
        return text.strip('-')
    ```

    *   `tr_slug("Merhaba Dünya!")`:
        1. Mapping: `merhaba dunya!` (Wait, 'ü' is in mapping). Result: `merhaba dunya!`
        2. Lowercase: `merhaba dunya!`
        3. Regex: `merhaba-dunya-`
        4. Strip: `merhaba-dunya`. Correct.

    *   `tr_slug("Çok Güzel Bir Şey!")`:
        1. Mapping: `cok Guzel Bir Sey!` (Wait, 'ü' is in mapping). Result: `cok Guzel Bir Sey!`
        2. Lowercase: `cok guzel bir sey!`
        3. Regex: `cok-guzel-bir-sey-`
        4. Strip: `cok-guzel-bir-sey`. Correct.

    *   `tr_slug("---test---")`:
        1. Mapping: `---test---`
        2. Lowercase: `---test---`
        3. Regex: `-test-`
        4. Strip: `test`. Correct.

    *   `tr_slug("123 abc 456")`:
        1. Result: `123-abc-456`. Correct.

    The prompt asks for "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun". This means if I have `"hello @#$ world"`, it should be `"hello-world"`. My regex `[^a-z0-9]+` handles this perfectly because it matches the sequence `@#$` and replaces it with one `-`.

    *   Function name: `tr_slug(text: str) -> str`
    *   Turkish chars handled? Yes.
    *   Lowercase result? Yes.
    *   Non-alphanumeric to single hyphen? Yes.
    *   Strip leading/trailing hyphens? Yes.
    *   Single python block? Yes.

    One detail: `İ` in Python's `.lower()` can sometimes behave unexpectedly depending on the locale, but for standard string operations it usually works fine. However, to be safe and explicit as requested by "Türkçe harfler dönüşsün", I will include them in the mapping or handle them before lowercasing.

    Let's refine the replacement logic:
    ```python
    import re

    def tr_slug(text: str) -> str:
        # Mapping for Turkish characters (both cases to be safe)
        mapping = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        }

        # Replace Turkish characters first to avoid issues with lowercase conversion
        for tr_char, ascii_char in mapping.items():
            text = text.replace(tr_char, ascii_char)

        # Convert to lowercase
        text = text.lower()

        # Replace non-alphanumeric sequences with a single hyphen
        text = re.sub(r'[^a-z0-9]+', '-', text)

        # Strip leading and trailing hyphens
        return text.strip('-')
    ```

    Wait, if I replace `İ` with `i` first, then `.lower()` is fine. If I have `I`, it becomes `i`. This covers the requirement "büyük halleri de aynı şekilde".

    One edge case: What if the input is `" "` (just a space)?
    1. Mapping: `" "`
    2. Lowercase: `" "`
    3. Regex: `"-"`
    4. Strip: `""`. Correct for an empty slug.

    What about `"A & B"`?
    1. Mapping: `"A & B"`
    2. Lowercase: `"a & b"`
    3. Regex: `"a-b"`
    4. Strip: `"a-b"`. Correct.

    Final check on the regex `[^a-z0-9]+`:
    If input is `"abc123def"`, it stays `"abc123def"`.
    If input is `"abc...def"`, it becomes `"abc-def"`.
    This matches "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun".

    ```python
    import re

    def tr_slug(text: str) -> str:
        mapping = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        }
        for tr_char, ascii_char in mapping.items():
            text = text.replace(tr_char, ascii_char)

        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')
    ```

    Wait, one small detail: `I` (capital i without dot) in Turkish is the uppercase of `ı`. In English, it's the uppercase of `i`. The prompt says "ı $\to$ i" and "I $\to$ i". This means both the Turkish 'I' and the English 'I' should become 'i'. My mapping handles this.

    Let's double check:
    `tr_slug("Merhaba Dünya!")`
    - `mapping`: `merhaba dunya!` (if we replace lowercase first) or `Merhaba Dunya!` (if uppercase).
    - Let's use the logic: Replace characters $\to$ Lowercase $\to$ Regex.

    Example trace with `"İstanbul"`:
    1. Mapping: `I` is in mapping? Yes, `I` $\to$ `i`. So `İstanbul` becomes `istanbul`.
    2. Lowercase: `istanbul`.
    3. Regex: `istanbul`.
    4. Strip: `istanbul`.

    Example trace with `"ŞEHRİN"`:
    1. Mapping: `Ş` $\to$ `s`, `İ` $\to$ `i`. Result: `sehrin`.
    2. Lowercase: `sehrin`.
    3. Regex: `sehrin`.

    Wait, if I replace `Ş` with `s` and then lowercase, it's fine. If I have `ş`, it becomes `s`.

    One more check on the regex: `[^a-z0-9]+`. This will catch everything that isn't a letter or number.
    If input is `"abc_def"`, `_` is not in `[a-z0-9]`, so it becomes `abc-def`. Correct.

    Final Code Structure:
    ```python
    import re

    def tr_slug(text: str) -> str:
        mapping = {
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        }
        for tr_char, ascii_char in mapping.items():
            text = text.replace(tr_char, ascii_char)

        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')
    ```

    Wait, there is a slight risk with `text.replace` in a loop if one replacement creates a character that is later replaced. But here we are mapping Turkish characters to ASCII ones, and the target characters (c, g, i, o, s, u) are not part of the keys being replaced (except for lowercase versions).
    Example: `Ç` $\to$ `c`. Then loop continues. No problem.

    Actually, a more robust way is using `str.translate`:
    ```python
    table = str.maketrans("çğıöşüÇĞİIÖŞÜ", "cgiosuCGIOSU") # Wait, I need to handle 'I' and 'İ' carefully.
    ```
    Actually, the loop is fine for this specific set of characters.

    Let's refine the mapping one last time:
    `ç-c, ğ-g, ı-i, ö-o, ş-s, ü-u` (lowercase)
    `Ç-c, Ğ-g, İ-i, I-i, Ö-o, Ş-s, Ü-u` (uppercase)

    Wait, `I` is the uppercase of `ı`. In English, `I` is the uppercase of `i`. The prompt says: "Türkçe harfler dönüşsün: ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u; büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü) de aynı şekilde."
    This means `I` $\to$ `i`.

    Let's check the mapping again:
    `mapping = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u', 'Ç': 'c', 'Ğ': 'g', 'I': 'i', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'}`

    This looks solid.

## Cevap

```python
import re

def tr_slug(text: str) -> str:
    # Türkçe karakterlerin ASCII karşılıkları (küçük ve büyük harf)
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    # 1. Türkçe karakterleri dönüştür
    for tr_char, ascii_char in mapping.items():
        text = text.replace(tr_char, ascii_char)
    
    # 2. Metni tamamen küçük harfe çevir
    text = text.lower()
    
    # 3. Harf ve rakam dışındaki her karakter dizisini tek bir '-' ile değiştir
    # [^a-z0-9]+ ifadesi a'dan z'ye harfler ve 0-9 arası rakamlar dışındakileri yakalar
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # 4. Baştaki ve sondaki '-' karakterlerini temizle
    return text.strip('-')
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Türkçe karakterlerin ASCII karşılıkları (küçük ve büyük harf)
    mapping = {
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'I': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    }
    
    # 1. Türkçe karakterleri dönüştür
    for tr_char, ascii_char in mapping.items():
        text = text.replace(tr_char, ascii_char)
    
    # 2. Metni tamamen küçük harfe çevir
    text = text.lower()
    
    # 3. Harf ve rakam dışındaki her karakter dizisini tek bir '-' ile değiştir
    # [^a-z0-9]+ ifadesi a'dan z'ye harfler ve 0-9 arası rakamlar dışındakileri yakalar
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # 4. Baştaki ve sondaki '-' karakterlerini temizle
    return text.strip('-')
```
