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

Thinking Process:

1.  **Analyze the Request:**
    *   Role: Experienced Software Developer.
    *   Task: Write a Python function `tr_slug(text: str) -> str`.
    *   Functionality: Convert text to URL-safe slug format.
    *   Specific Rules:
        1.  Turkish character mapping (lowercase & uppercase): ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u; Ç→C? No, rule says "Sonuç tamamen küçük harf olsun" (Result must be all lowercase). So Ç→c, etc.
        2.  Result entirely in lowercase.
        3.  Non-alphanumeric characters become single '-'.
        4.  Leading and trailing '-' must be removed.
    *   Example: `tr_slug("Merhaba Dünya!") == "merhaba-dunya"` (Wait, example says `D` to `d`, but original text has space. Space should likely become `-`. Let's check standard slug logic vs specific instruction).
        *   Instruction: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Any character sequence outside of letters and numbers becomes a single '-').
        *   Example: `Merhaba Dünya!` -> `merhaba-dunya`. Space became `-`, Exclamation mark disappeared or was part of the non-alphanumeric group? Usually, spaces become hyphens. If multiple non-alphanumerics are adjacent, they should probably collapse to one hyphen based on "tek bir '-' olsun" (become a single '-').
        *   Instruction implies normalization: replace non-alpha-numeric chars with '-', then strip leading/trailing '-'.

2.  **Determine Implementation Details:**
    *   Language: Python.
    *   Input: `str`. Output: `str`.
    *   Turkish Translation: I need to handle the specific Turkish vowel mapping. I can't rely on just `.lower()` because Turkish punctuation/letters aren't handled correctly by default English locales without manual mapping or Unicode normalization (which might not be enough for this specific strict requirement). It's safer to use a translation dictionary for Turkish characters.
    *   Steps:
        1.  Translate characters using the Turkish map.
        2.  Convert everything to lowercase (though the map can handle both upper/lower if I include mappings, explicit `.lower()` on the result is needed). Actually, better to process char by char or use `str.translate`.
        3.  Replace non-alphanumeric chars with `-`.
        4.  Strip leading/trailing `-`.

    *   Refining Step 1 (Translation):
        *   Mapping: 'ç' -> 'c', 'Ğ'/'g'? Wait, instruction says "Ç→c". So uppercase Turkish letters should also be mapped to lowercase equivalents. `str.lower()` does this for ASCII but not Turkish unless locale is set or mapping is done manually. I will create a translation table.
        *   Mapping needed:
            Lowercase: ç, ğ, ı, ö, ş, ü -> c, g, i, o, s, u
            Uppercase: Ç, Ğ, İ (wait, instruction says "I" or "İ"? Usually 'İ' is uppercase dotted I, but standard Turkish is dotless İ and dotted I. The prompt says: "büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü) de aynı şekilde."
            *Correction*: In the prompt it lists `I` instead of `İ`. This might be a typo in the prompt or referring to Latin 'I'. However, context implies Turkish letters. Usually, Turkish uppercase is Ç, Ğ, İ, O (no), Ö, Ş, Ü. Wait, Turkish Uppercase I is İ (dotless). The prompt explicitly lists `I`. Let's assume standard Turkish characters: ç, ğ, ı, ö, ş, ü and their uppercase counterparts Ç, Ğ, İ, Ö, Ş, Ü.
            *Wait*, looking closely at the prompt: `(Ç, Ğ, I, İ, Ö, Ş, Ü)`. There is a potential typo in `I` (Latin i vs dotless İ). But given the context of "Türkçe harfler", it definitely means Turkish uppercase İ. However, to be safe and follow instructions strictly while handling standard Turkish encoding:
            I should map the actual Unicode characters found in Turkish text.
            If the user passes `I` (Latin), it stays `i`. But usually slugs expect normalization of Turkish letters. The safest bet is a mapping dict that covers the specific requested mappings for all relevant Turkish chars.
            Let's use a translation table approach using `str.maketrans`.

    *   Refining Step 3 (Non-alphanumeric):
        *   Regex: `[^\w]` matches non-word characters. `\w` includes underscores and numbers in Python by default (`\w` includes letters, digits, underscore). For slug, we usually want alphanumeric + space? No, instruction says "Harf ve rakam dışındaki her karakter". This excludes `_`.
        *   So I need to replace anything that is NOT a Turkish letter AND not a digit. Wait, if I use the translation map first, then check for `[a-z0-9]`.
        *   Actually, `str.translate` can remove characters or replace them.
        *   Better approach:
            1. Translate Turkish chars to ASCII equivalents + lowercase.
            2. Replace all non-alphanumeric (not a-z, not 0-9) with `-`.
            3. Strip leading/trailing `-`.

    *   Handling the "I" vs "İ" ambiguity: I will assume standard Turkish characters (İ). If input is `I` (Latin), it goes to `i` naturally. If input is `İ`, it should go to `i` based on mapping logic `ı->i`. Wait, instruction says `ı→i` for lowercase. For uppercase, it lists `(Ç, Ğ, I, İ...)`. Usually Turkish slug conversion maps `I` (Latin) -> `i` and `İ` (Turkish Uppercase Dotted I) -> `i`. If the prompt explicitly wrote `I`, maybe they mean Latin 'I'. But since they list it alongside Turkish chars, it's likely a typo for `İ`. I will map both to be safe: `ı`/`İ` -> `i`.
    *   Wait, looking at the instruction again: "Türkçe harfler dönüşsün... büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü)". This list is mixed. Turkish 'I' is usually written as dotted ı or dotless I. Uppercase is ı -> I? No, uppercase of dotless i is İ.
    *   Okay, to ensure correctness for a "Türkçe harfler" request: I will support standard Turkish characters (ç, ğ, ı, ö, ş, ü and Ç, Ğ, İ, Ö, Ş, Ü). The `I` in the prompt is likely a typo for `İ`.

    *   Algorithm:
        ```python
        def tr_slug(text):
            # Define translation table
            # Map Turkish lowercase to ASCII lowercase
            # Map Turkish uppercase to ASCII lowercase
            # All other chars handled later
            
            # Actually, regex replacement might be cleaner than multiple replace calls.
            
            # Step 1: Replace specific Turkish characters with their ASCII equivalents
            trans_table = str.maketrans({
                'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u' # Added İ and Ö/Ş/Ü mappings for upper case
            })
            
            text = text.translate(trans_table)
            
            # Step 2: Replace non-alphanumeric characters with '-'
            # But we need to exclude underscores if possible? "Harf ve rakam dışındaki".
            # Python's isalnum() includes underscore usually, so we should be careful.
            # Instruction: Harf ve rakam (Letter and number). So '_' is not a letter/number in this context.
            
            import re
            text = re.sub(r'[^a-z0-9]', '-', text)
            
            # Step 3: Strip leading/trailing '-'
            text = text.strip('-')
            
            return text if text else "" # Handle empty string edge case? Not specified, but good practice.
        ```

    *   Wait, let's check the example `tr_slug("Merhaba Dünya!") == "merhaba-dunya"`.
        *   ' ' (space) -> '-'
        *   '!' -> removed or part of sequence? `re.sub` replaces with single `-`. If there are multiple special chars adjacent, they become multiple `-`, which is fine initially but need to collapse.
        *   Instruction: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Any character sequence outside letters/numbers becomes a SINGLE '-'). This means `!@#$%` should be one `-`.
        *   So after replacing with `-`, I must also replace multiple consecutive `-` with single `-`. Then strip.

    *   Revised Algorithm:
        1. Translate Turkish chars to ASCII lowercase.
        2. Replace non-alphanumeric (except maybe space?) with something? No, just `[^a-z0-9]` becomes `-`.
        3. Replace multiple consecutive `-` with one `-`.
        4. Strip leading/trailing `-`.

    *   Wait, looking at the instruction "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun."
        If I have `Merhaba !Dunya`, it becomes `merhaba -dunya` -> `merhaba-dunya`.
        So collapsing consecutive non-alphanumeric replacements is crucial.
        
    *   Implementation Plan:
        1. Import `re`.
        2. Create translation dictionary for Turkish letters (both cases). Note: The prompt mentions 'I' inside the tuple `(Ç, Ğ, I, İ, Ö, Ş, Ü)`. It's safer to just map standard Turkish characters. If there is a Latin 'I', it remains 'i' after `lower()`.
        3. Translate text using `str.translate`.
        4. Use regex to replace non-alphanumeric with single `-`, then collapse consecutive `-`s? Or simply replace non-alphanumerics with `-` and use `re.sub(r'-+', '-', ...)`.
        
    *   Wait, one more detail: "Sonuç tamamen küçük harf olsun". My translation maps upper Turkish to lower. But what about regular ASCII uppercase letters in the input text (e.g., "ABC")? The instruction says "Metni URL'de kullanılacak kısa ada (slug) çevirsin... Sonuç tamamen küçük harf olsun." So yes, all remaining ASCII upper must also be converted to lowercase. `str.translate` handles specific chars, so after translation, I should `.lower()` the whole string just in case there are standard English uppercase letters left over.
    
    *   Final Logic:
        1. Define mapping for Turkish chars (Lower -> Lower, Upper -> Lower).
        2. Apply `translate`.
        3. Replace non-alphanumeric (`[^a-z0-9]`) with `-`.
        4. Collapse consecutive `-` to single `-` using regex.
        5. Strip leading/trailing `-`.

    *   Edge case: Empty string or only punctuation -> return empty string? Example doesn't show, but `strip('-')` on empty string returns empty string. If string is `"---"`, it becomes `""`. This seems correct.

    *   Code Structure:
        ```python
        import re

        def tr_slug(text: str) -> str:
            # Create translation table for Turkish characters
            mapping = {
                'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
                'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
            }
            
            # Note: Prompt listed "I" as well. Since it's Turkish context, 
            # I will map İ. If input is Latin 'I', it gets lowercased by .lower() later.
            
            text = text.translate(str.maketrans(mapping))
            text = text.lower()
            
            # Replace non-alphanumeric characters with '-'
            # ^[a-z0-9] means not letter or number
            text = re.sub(r'[^a-z0-9]', '-', text)
            
            # Collapse multiple hyphens to one
            text = re.sub(r'-+', '-', text)
            
            # Strip leading/trailing hyphens
            return text.strip('-')
        ```

    *   Wait, check the prompt's instruction on "I" again. `(Ç, Ğ, I, İ, Ö, Ş, Ü)`. If I strictly follow this and map `I` -> `i`, it works same as `.lower()`. But standard Turkish slug generators usually handle `İ` (dotless i uppercase). The prompt lists both `I` and `İ`. It's safe to just ensure everything ends up lowercase.
    *   Wait, is there a constraint about performance or imports? "Sadece Python kodunu tek bir ```python bloğu içinde ver." Just code block.
    *   I should check if `str.translate` handles Turkish Unicode normalization better than mapping explicitly. Explicit map is safer and faster for this specific task without locale dependencies.

    *   One detail: The prompt says "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Any character sequence outside letters/numbers becomes a single '-').
        Example: `Merhaba!Dunya` -> `merhaba-dunya`.
        If I do `re.sub(r'[^a-z0-9]', '-', text)`, it replaces each non-alpha with `-`. So `!@#$` becomes `- - - -`? No, they are adjacent in string. It becomes `----`. Then `re.sub(r'-+', '-')` makes it one `-`. This logic holds.

    *   Let's refine the Turkish mapping to be comprehensive.
        Input: "Merhaba Dünya!"
        1. Translate: "Merhaba Dunya!" (Assuming space remains space, 'ı' becomes 'i'). Wait, `translate` doesn't affect spaces or punctuation.
           String: `Merhaba Dunya!` (Space preserved).
        2. `.lower()`: `merhaba dunya!`.
        3. Regex replace non-alphanumeric with `-`: `merhaba-dunya!` -> Wait, space becomes `-`, ! becomes `-`.
           Result: `merhaba-dunya--` (space and ! become -).
           Collapse: `merhaba-dunya-`.
           Strip: `merhaba-dunya`. Matches example.

    *   One specific check: The prompt says "Türkçe harfler dönüşsün...". Does it imply ONLY Turkish chars should be mapped? Or does it mean the text is assumed to be in a mix and we must normalize Turkish ones. Standard behavior for `tr_slug` implies normalization of all input to ASCII based on Turkish rules.
    *   Wait, does "Harf ve rakam dışındaki" refer to Unicode letters or ASCII? Given the context (Slug), it usually means standard alphanumeric characters after translation. So `[^a-z0-9]`.

    *   Final check on imports: `import re` is allowed in Python scripts.
    *   Function signature: `tr_slug(text: str) -> str`.

3.  **Constructing the Code:**
    ```python
    import re

    def tr_slug(text: str) -> str:
        # Map Turkish characters to their ASCII equivalents (lowercase)
        trans_table = str.maketrans({
            'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
            'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
        })
        
        # Translate Turkish characters to ASCII and convert all to lowercase
        text = text.translate(trans_table).lower()
        
        # Replace any non-alphanumeric character with a hyphen
        text = re.sub(r'[^a-z0-9]', '-', text)
        
        # Collapse multiple consecutive hyphens into one
        text = re.sub(r'-+', '-', text)
        
        # Remove leading and trailing hyphens
        return text.strip('-')
    ```

4.  **Verification against Example:**
    Input: `tr_slug("Merhaba Dünya!")`
    - Translate: `Merhaba Dunya!` (Space stays, exclamation stays). Turkish chars remain as they are in this string but `.lower()` handles them if any uppercase Turkish existed. If "DunYa" had 'ı', it would map to 'i'.
    - Lowercase: `merhaba dunya!`
    - Regex replace `[^a-z0-9]`: Space becomes `-`, ! becomes `-`. Result: `merhaba-dunya--` (Space is one char, ! is another). Wait.
      String: "merhaba dunya!"
      Indices: m...a[space]d...y[!].
      Replace space with - -> ...-...
      Replace ! with - -> ...---
      Result string: `merhaba-dunya--`? No, space is one char, ! is another. So between 'a' and 'd', there was a space (-> -). Between 'y' and end, there was ! (-> -).
      So `merhaba-dunya-`. Wait, example output: `"merhaba-dunya"`.
      My logic gives `merhaba-dunya-` then strip `-` -> `merhaba-dunya`. Correct.

    *   Wait, what if input is "Merhaba!Dunya"?
        Space not present. Exclamation between 'b' and 'D'.
        After replace: `merhaba-dunya`. Matches example logic (space acts as separator in example, but exclamation also creates separator).
    
    *   What about "İstanbul"? (Assuming Uppercase İ is handled by mapping to i).
        Input: `İstanbul`
        Translate: `istanbul` (if I map İ->i) or stays if only lower mapped and .lower() handles it? If input has `I` (Latin), `.lower()` -> `i`. If input has `İ` (Turkish), mapping maps to `i`. Then `.lower()` is redundant but harmless.
        Wait, my code does `translate(...)` then `.lower()`. Since `translate` for Turkish upper cases outputs lowercase ('C' etc), the second `.lower()` ensures any standard ASCII uppercase remains lowercase.

    *   Is it possible to do this without regex? String replace loop is slower and messy for "any character". Regex is best.
    
    *   One small optimization: `str.strip('-')` works on both ends.
    *   The prompt asks for specific Turkish mappings. I should ensure my mapping dict covers them explicitly as requested.

5.  **Final Code Review:**
    - Function name: `tr_slug`. Correct.
    - Type hints: Included.
    - Logic: Follows all constraints (Turkish map, lowercase, hyphens for non-alnum, strip leading/trailing).
    - Format: Single ```python block.

    *Self-Correction on Prompt's `(Ç, Ğ, I, İ...)`*:
    If the user specifically typed `I`, they might mean Latin 'I'. But context is Turkish chars. Standard practice in this domain (Slugify) handles `İ`. The code I wrote handles both implicitly because `translate` maps `İ` to `i`, and `.lower()` maps `I` to `i`. So it covers all bases.

    *Wait, one more check on "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun."*
    Does this mean consecutive non-alphanumeric chars should be treated as ONE group? Yes, "dizisi" (sequence). My logic `re.sub(r'-+', '-')` handles the resulting sequence of hyphens. This is functionally equivalent to treating adjacent special characters as a single separator.

    Let's write the code.

```python
import re

def tr_slug(text: str) -> str:
    # Map Turkish letters to their ASCII equivalents (lowercase)
    trans_table = str.maketrans({
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    })

    # Translate and convert to lowercase
    text = text.translate(trans_table).lower()

    # Replace any non-alphanumeric character with a single hyphen
    text = re.sub(r'[^a-z0-9]', '-', text)

    # Collapse multiple consecutive hyphens into one
    text = re.sub(r'-+', '-', text)

    # Strip leading and trailing hyphens
    return text.strip('-')
```
Wait, I should check if `import re` is allowed. Usually yes. The prompt says "Sadece Python kodunu... ver". Imports are part of the code block.

One minor thing: `I` vs `İ`. In standard Turkish keyboard, `I` is often `i`. `İ` is uppercase dotted I. My mapping uses `İ`. If input contains Latin `I`, `.lower()` handles it. So this is robust.

Final check on constraints:
- Türkçe harfler dönüşsün (ç→c...) -> Done via map.
- Sonuç tamamen küçük harf olsun -> Done via .lower().
- Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun -> Done via re.sub and collapse.
- Baştaki ve sondaki '-' karakterleri silinsin -> Done via strip('-').

Looks good.

One edge case: Input `""` (empty string).
1. Translate/Lower -> ""
2. ReSub -> ""
3. Collapse -> ""
4. Strip -> ""
Returns "". Correct.

Input `"---"`.
1. ... -> "---"
2. Replace -> "..."? No, regex `[^\w]` replaces non-alpha. Wait, my regex is `[^a-z0-9]`. Dashes are not a-z or 0-9. So `---` matches the pattern and becomes `---`.
Wait! If input IS `---`, it has no letters/numbers.
1. Translate -> `---` (no change).
2. Lower -> `---`.
3. Regex `[^a-z0-9]` matches `-`. Replaces with `-`. So it stays `---`.
4. Collapse -> `---`.
5. Strip -> `""`.
Correct.

Wait, if input is `"Test ---"`.
1. Translate/Downer -> "test ---".
2. Regex replaces space and dashes? No. Dashes are non-alphanumeric chars. Space is non-alphanumeric char.
So `[^a-z0-9]` matches space AND dashes.
Wait, my previous logic: "Replace any non-alphanumeric character with a single hyphen".
If input is `"Test ---"`, the regex replaces space with `-`, and each `-` with `-`. Result: `test-- --`. Then collapse to `test -`. Strip -> `test`.
Does this match the requirement? "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun."
If input has consecutive non-alphanumeric characters, they become one '-'. My regex replaces every single char with '-', creating a sequence of hyphens. The subsequent collapse regex handles that. So `"Test ---"` -> `test` (space + dashes all collapsed to single `-`, stripped). This seems correct behavior for a slug function usually, but strictly following "Harf ve rakam dışındaki... tek bir '-' olsun" implies if you have non-alphanumeric sequence, it becomes one `-`.
If I have `"A!B"`, `!` is non-alnum. Becomes `-`. Result `A-B`.
If I have `"A ! B"`, Space and ! are non-alnum. Sequence: " ! ". Becomes "-". Result `A-B`.
My code does exactly this (replace each non-alnum with -, then collapse).

Wait, one potential issue: If the input is purely non-alphanumeric like `"!!!",` becomes `-` after replace, then strip gives empty string?
Input `!!!`: Replace -> `---` (each ! replaced by -). Collapse -> `-`. Strip -> ``. Correct.

Okay, ready to generate output.

One detail on imports: Since I am a "Senior Developer", importing inside the function is okay but top-level import is standard for modules used globally in script. The prompt asks for code block. I will put `import re` at the top of the file (inside the block).

Wait, checking one more thing regarding "I" in prompt: `(Ç, Ğ, I, İ...)`.
If the user input has `I`, my `.lower()` makes it `i`. If they have `İ`, my map makes it `i`. Both work. No conflict.
But wait, if I map `ı` -> `i` (dotless i). And input is `I` (capital Latin I). My code does not explicitly map `I` in the table, but `.lower()` handles it. This is fine.

Final check on the generated code block content. Only Python code.


## Cevap

```python
import re

def tr_slug(text: str) -> str:
    # Türkçe harfleri ASCII karşılıklarına dönüştür (küçük ve büyük halleri için)
    trans_table = str.maketrans({
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    })

    # Metni çevir ve sonucunu tamamen küçük harfe dönüştür
    text = text.translate(trans_table).lower()

    # Harf ve rakam dışındaki karakterleri tek bir '-' ile değiştir (dizisi olarak)
    text = re.sub(r'[^a-z0-9]', '-', text)

    # Tekrarlayan '-' işareti tek bir '-' haline getir
    text = re.sub(r'-+', '-', text)

    # Baştaki ve sondaki '-' karakterlerini sil
    return text.strip('-')
```

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Türkçe harfleri ASCII karşılıklarına dönüştür (küçük ve büyük halleri için)
    trans_table = str.maketrans({
        'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
        'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'
    })

    # Metni çevir ve sonucunu tamamen küçük harfe dönüştür
    text = text.translate(trans_table).lower()

    # Harf ve rakam dışındaki karakterleri tek bir '-' ile değiştir (dizisi olarak)
    text = re.sub(r'[^a-z0-9]', '-', text)

    # Tekrarlayan '-' işareti tek bir '-' haline getir
    text = re.sub(r'-+', '-', text)

    # Baştaki ve sondaki '-' karakterlerini sil
    return text.strip('-')
```
