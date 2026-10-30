# kod-slug · puan 1.00

**Not:** 8/8 test; token sınırında kesildi

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
    *   Task: Write a Python function `tr_slug(text: str) -> str`.
    *   Purpose: Convert text to a URL-friendly slug (specifically Turkish).
    *   Requirements:
        1.  Turkish character mapping: ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u (and uppercase variants Ç, Ğ, I, İ, Ö, Ş, Ü).
        2.  Result must be all lowercase.
        3.  Non-alphanumeric characters should be replaced by a single '-'.
        4.  Leading and trailing '-' characters must be removed.
    *   Output Format: Only the Python code inside a single ```python block.

2.  **Drafting the Logic:**
    *   Input: `text` (string).
    *   Step 1: Define translation table for Turkish characters.
        *   Lowercase: 'ç', 'ğ', 'ı', 'ö', 'ş', 'ü' -> 'c', 'g', 'i', 'o', 's', 'u'.
        *   Uppercase: 'Ç', 'Ğ', 'I', 'İ', 'Ö', 'Ş', 'Ü' -> 'C', 'G', 'I', 'O', 'S', 'U'.
    *   Step 2: Apply translation. `text.translate(table)`.
    *   Step 3: Convert to lowercase (though the mapping handles specific chars, general lowercasing ensures consistency). Actually, since we map uppercase Turkish letters to uppercase ASCII equivalents first, then we need to make sure everything is lowercase at the end. Or just map them directly to lowercase in the translation table?
        *   Option A: Map 'Ç' -> 'c', 'Ğ' -> 'g', etc. Then convert whole string to lower.
        *   Option B: Convert to lower first, then map specific chars (ı vs I). Note that `ı` is distinct from `i`. In Python `str.lower()`, `I` becomes `i`, but `İ` becomes `i`. Wait, Turkish locale matters for `lower()`? No, standard Python `lower()` handles ASCII. For Turkish characters:
            *   'Ç'.lower() -> 'ç' (in standard Python 3).
            *   'Ğ'.lower() -> 'ğ'.
            *   'İ'.lower() -> 'ı' (Wait, no. In standard Python, `İ` is often treated as `I` or specific unicode. Actually, `str.lower()` in Python uses Unicode casing rules. `İ`.lower() is `ı`. `I`.lower() is `i`. This might be tricky if we rely solely on `.lower()`.
            *   Better approach: Explicitly define the translation table for all variants to lowercase ASCII equivalents directly.
        *   Let's check Python's behavior: `'Ç'.lower()` -> `'ç'`, `'İ'.lower()` -> `'ı'` (in some versions/locales, but standard Unicode says `I` is Latin Capital I, `İ` is Latin Capital I with dot). Actually, in Python 3, `'İ'.lower()` returns `'ı'`. So `.lower()` works for Turkish chars mostly.
        *   However, the requirement explicitly asks to map specific chars: ç→c, ğ→g, etc. This implies we want ASCII equivalents.
        *   Strategy: Create a translation dictionary mapping all Turkish letters (upper and lower) to their lowercase ASCII counterparts. Then use `str.translate`. Then convert remaining non-alphanumeric to '-'. Finally strip leading/trailing '-'.

    *   Step 4: Replace non-alphanumeric characters with '-'.
        *   Regex or simple iteration? `re.sub(r'[^a-z0-9]', '-', text)`. Note that after translation, we have ASCII letters. So `[a-z0-9]` is safe if we ensure everything is lowercase first.

    *   Step 5: Strip leading/trailing '-'.
        *   `.strip('-')`.

3.  **Refining the Translation Table:**
    *   Need to map:
        *   'ç': 'c'
        *   'Ç': 'c'
        *   'ğ': 'g'
        *   'Ğ': 'g'
        *   'ı': 'i' (Note: Turkish dotless i)
        *   'İ': 'i' (Wait, standard `lower()` makes `İ` -> `ı`. We want it to become `i` for slug purposes usually? The prompt says "ı→i". It implies the dotless i should become regular i. Let's look at the mapping: `ı→i`. What about `I`? Usually slugs treat `I` as `i`. But specifically Turkish chars are mentioned.
        *   Prompt says: `ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u`. It also mentions uppercase variants `Ç, Ğ, I, İ, Ö, Ş, Ü`. Wait, the prompt lists `I` (Latin Capital I) in the uppercase list? "büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü)".
        *   Actually, usually Turkish slug logic maps:
            *   ç -> c
            *   Ç -> c
            *   ğ -> g
            *   Ğ -> g
            *   ı -> i (dotless)
            *   İ -> i (dotted capital I becomes dotless lowercase? Or just 'i'?) Usually `İ` maps to `i`.
            *   ö -> o
            *   Ö -> o
            *   ş -> s
            *   Ş -> s
            *   ü -> u
            *   Ü -> u
        *   Let's check the prompt again: "büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü)". It explicitly lists `I` (Latin Capital I) as needing conversion? Or is it a typo in my reading? "Türkçe harfler dönüşsün... büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü)".
        *   Actually, standard Turkish slug logic: `ı` becomes `i`. `İ` becomes `i`. `I` is already ASCII. But if the prompt says "büyük halleri ... de aynı şekilde", it means map them to lowercase equivalents.
        *   Let's create a dict mapping all these specific chars to their target lowercase ASCII char.

    *   Translation Table Construction:
        ```python
        trans_table = str.maketrans({
            'ç': 'c', 'Ç': 'c',
            'ğ': 'g', 'Ğ': 'g',
            'ı': 'i', 'İ': 'i', # Note: Prompt says ı->i. Usually İ also -> i for slugs. I is already i. But prompt lists I in uppercase list? Let's assume standard Turkish slug behavior where dotless i becomes i, dotted capital I becomes i.
            'ö': 'o', 'Ö': 'o',
            'ş': 's', 'Ş': 's',
            'ü': 'u', 'Ü': 'u'
        })
        ```
    *   Wait, does `I` need mapping? The prompt lists `I` in the uppercase list of Turkish letters. It might be a slight confusion in the prompt (since I is not Turkish), but to be safe and follow "büyük halleri ... de aynı şekilde", I should ensure everything ends up lowercase ASCII.
    *   Actually, simpler approach: Translate specific chars, then `.lower()`. But `İ`.lower() is `ı` in Python 3 (Unicode). We want it to be `i`. So explicit mapping for `İ` -> `i` is crucial. Also `ı` -> `i`.
    *   Let's check the prompt requirement strictly: "ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u". And uppercase variants.
    *   So mapping should be explicit to ensure ASCII output.

4.  **Implementation Details:**
    *   Import `re` for regex replacement? Or just string methods? Regex is cleaner for "non-alphanumeric".
    *   Code structure:
        ```python
        def tr_slug(text: str) -> str:
            # Translation table
            trans = {
                'ç': 'c', 'Ç': 'c',
                'ğ': 'g', 'Ğ': 'g',
                'ı': 'i', 'İ': 'i',
                'ö': 'o', 'Ö': 'o',
                'ş': 's', 'Ş': 's',
                'ü': 'u', 'Ü': 'u'
            }
            text = text.translate(str.maketrans(trans)) # Wait, maketrans takes dict or tuples. str.maketrans(dict) works in Python 3.
            # Actually str.maketrans expects a dictionary where keys are characters and values are strings (length 1).
            
            # Apply translation
            text = text.translate(str.maketrans(trans))
            
            # Lowercase (ensure everything is lower, though mapping handles specific ones)
            text = text.lower() 
            
            # Replace non-alphanumeric with -
            import re
            text = re.sub(r'[^a-z0-9]', '-', text)
            
            # Strip leading/trailing -
            return text.strip('-')
        ```
    *   Wait, `str.maketrans` takes a dict. If I pass the dict directly to `translate`, it works in Python 3? Yes, `str.translate(table)` where table is result of `maketrans`. Or just use `dict` if keys are chars and values are strings? No, `translate` expects a translation table (integers or string mapping).
    *   Correct usage: `table = str.maketrans(trans_dict)`, then `text.translate(table)`.

5.  **Refining the Regex:**
    *   After translation and lowercasing, we have ASCII chars.
    *   We need to replace anything that is not a letter or digit with '-'.
    *   Pattern: `[^a-z0-9]`.
    *   Then strip `-` from start/end.

6.  **Edge Cases:**
    *   Empty string? Returns empty string (strip returns empty).
    *   String with only special chars? Returns empty string.
    *   Spaces? Replaced by '-'.
    *   Example: "Merhaba Dünya!" -> "merhaba-dunya".
        *   'M' -> 'm', 'e'...'a' -> same, 'D' -> 'd', 'ü' -> 'u', 'y'...'a' -> same. '!' -> '-'.
        *   Result: "merhaba-dunya-". Strip -> "merhaba-dunya". Matches example.

7.  **Final Code Structure:**
    *   Define function.
    *   Create translation table.
    *   Translate.
    *   Lowercase (redundant if mapping is to lowercase, but good for safety). Actually, `str.maketrans` with dict values as lowercase strings ensures they are lowercase. But other chars like 'A' need `.lower()`. So call `.lower()` after translate.
    *   Regex replace non-alphanumeric.
    *   Strip.

8.  **Wait, one detail:** "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character outside letter and digit should be a single '-'). This implies consecutive special chars become one '-'. `re.sub(r'[^a-z0-9]', '-', text)` does this because it replaces each char with '-', but wait. If I have "!!", regex replaces first '!' with '-', second '!' with '-', resulting in "--".
    *   Requirement: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." -> This phrasing is slightly ambiguous. Does it mean "replace the sequence of non-alphanumeric chars with a single '-'"? Or "each such character becomes a '-'"?
    *   Usually, slugs collapse multiple separators into one. Example: "Hello!!World" -> "hello-world". If I replace each '!' with '-', I get "hello--world".
    *   Let's re-read carefully: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character outside letter and digit should be a single '-'). This literally means char-by-char replacement. BUT standard slug behavior usually collapses separators. However, looking at the example: `tr_slug("Merhaba Dünya!") == "merhaba-dunya"`. There is only one '!' so it doesn't clarify collapsing.
    *   Common interpretation for slugs (e.g., WordPress): Multiple spaces or punctuation become a single hyphen.
    *   However, strict reading of the sentence: "Her karakter ... tek bir '-' olsun". This suggests 1 char -> 1 '-'.
    *   BUT, usually "slug" implies collapsing whitespace/punctuation. Let's look for standard behavior implied by "URL'de kullanılacak kısa ada (slug)". URLs don't like multiple hyphens often? Actually they do, but it looks ugly.
    *   Wait, if I have "Merhaba  Dünya", space is non-alphanumeric. If I replace each char with '-', I get "merhaba--dunya". Is that desired?
    *   Let's check the constraint again: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character outside letter and digit should be a single '-'). This sounds like 1-to-1 mapping.
    *   However, standard slug logic often uses `re.sub(r'[^a-z0-9]+', '-', text)` to collapse multiple separators into one.
    *   Let's consider the phrase "tek bir '-' olsun". It could mean "The result of replacing non-alphanumeric chars should be a single hyphen" (implying collapsing). Or it could mean "Each such character becomes a hyphen".
    *   Given "URL'de kullanılacak kısa ada", usually `hello--world` is valid but less clean. But if the instruction says "Her karakter ... tek bir '-' olsun", I should probably stick to 1-to-1 replacement unless standard slug logic implies collapsing.
    *   Wait, looking at similar tasks online (Turkish slug), often multiple spaces become one hyphen.
    *   Let's look at the phrasing again: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." -> "Every character outside letter and digit should be a single '-'. This implies `!` becomes `-`, `?` becomes `-`. It does not explicitly say consecutive ones become one.
    *   However, if I have "Merhaba  Dünya" (two spaces), result "merhaba--dunya".
    *   Let's assume standard slug behavior which collapses separators because that is the definition of a clean slug. But strict reading suggests char-by-char.
    *   Wait, there is a nuance: "Her karakter dizisi tek bir '-' olsun" might be interpreted as "The set of non-alphanumeric characters should result in a single hyphen". No, that's too strong.
    *   Let's check the example again: `Merhaba Dünya!`. One space, one exclamation. Result `merhaba-dunya`. Space becomes `-`, ! becomes nothing? Wait. "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." -> Non-alphanumeric chars become '-'.
    *   In the example: "Merhaba Dünya!". 'D' is letter, 'ü' is letter (mapped to u), 'y', 'a' are letters. Space is non-letter/non-digit. '!' is non-letter/non-digit.
    *   If space becomes '-', and '!' becomes '-', result would be `merhaba-dunya-`. But example says `merhaba-dunya`.
    *   This implies trailing '-' must be removed (Requirement 4: "Baştaki ve sondaki '-' karakterleri silinsin"). So `merhaba-dunya-` -> `merhaba-dunya`.
    *   What about internal multiple separators? e.g. "Merhaba   Dünya". If space->-, result `merhaba---dunya`. Strip doesn't help middle.
    *   Usually, slugs collapse consecutive non-alphanumeric chars into a single hyphen. This is the standard behavior for `slugify` libraries (e.g., `django.utils.text.slugify`).
    *   Given "URL'de kullanılacak", collapsing is safer and more common. I will use `re.sub(r'[^a-z0-9]+', '-', text)` to ensure consecutive separators become one hyphen, which aligns with the spirit of a slug. If I strictly follow char-by-char, it might produce ugly URLs.
    *   Wait, re-reading: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character outside letter and digit should be a single '-'). This phrasing is tricky. It literally says 1 non-alphanumeric -> 1 hyphen. But the example `Merhaba Dünya!` -> `merhaba-dunya`.
        *   Input: "Merhaba" + " " + "Dünya" + "!".
        *   Non-alpha-numeric chars: ' ', '!'.
        *   If 1-to-1: ' ' -> '-', '!' -> '-'. Result: `merhaba-dunya--`. Strip trailing: `merhaba-dunya-`. Wait, example result is `merhaba-dunya`. So the space became `-` and `!` was removed? Or both became `-` but one was stripped?
        *   If `!` becomes `-`, it's at the end. Stripped.
        *   If ` ` becomes `-`, it's in middle.
        *   Result `merhaba-dunya`. This implies space -> `-` and `!` -> (removed or converted to - then stripped).
        *   Actually, if I replace all non-alphanumeric with '-', I get `merhaba-dunya-`. Strip trailing gives `merhaba-dunya`.
        *   So the logic holds: Replace all non-alpha-num with `-`, then strip.
        *   Does it handle multiple spaces? "Merhaba  Dünya". -> `merhaba--dunya`. Is this desired? Usually slugs collapse this to `merhaba-dunya`. The instruction says "Her karakter ... tek bir '-' olsun" (Every character... should be a single '-'). This sounds like 1-to-1. But standard slug practice is collapsing.
        *   However, if I use `re.sub(r'[^a-z0-9]+', '-', text)`, it replaces the *sequence* of non-alphanumeric chars with a single `-`. This satisfies "Every character outside... becomes part of a hyphen" loosely? No.
        *   Let's check the constraint again: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character sequence outside letter and digit should be a single '-'). Wait, "karakter dizisi" means "character string/sequence". If it meant "each character", it would say "her karakter". It says "Her karakter dizisi" (Every character sequence). This is ambiguous.
        *   However, looking at the example `Merhaba Dünya!` -> `merhaba-dunya`. The space and exclamation mark are both non-alphanumeric. If they were treated individually as `-`, we would have two hyphens or one if collapsed. Since trailing is stripped, `!` becomes `-` then stripped. Space becomes `-`. So `merhaba-dunya-` -> `merhaba-dunya`.
        *   What about "Merhaba  Dünya"? If I treat space as char, I get double hyphen. If I collapse, single.
        *   Given the instruction "URL'de kullanılacak", collapsing is standard. I will use `re.sub(r'[^a-z0-9]+', '-', text)`. This ensures no consecutive hyphens. It effectively treats a sequence of non-alphanumeric chars as one separator.

    *   Wait, let's look at the instruction "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." again.
        *   Literal translation: "Every character string outside letter and digit should be a single '-'.
        *   This likely means: Replace any non-alphanumeric sequence with a single hyphen. (e.g., spaces, punctuation).
        *   So `re.sub(r'[^a-z0-9]+', '-', text)` is the correct interpretation for "slug".

    *   Wait, one more check on Turkish chars mapping.
        *   Prompt: `ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u`.
        *   Uppercase: `Ç, Ğ, I, İ, Ö, Ş, Ü`. Note the inclusion of `I` (Latin Capital I). In Turkish context, sometimes `I` is treated as a variant. But standard mapping for slugs usually maps `İ` to `i`.
        *   My translation table should include:
            *   'ç': 'c', 'Ç': 'c'
            *   'ğ': 'g', 'Ğ': 'g'
            *   'ı': 'i', 'İ': 'i' (Crucial for Turkish slugs)
            *   'ö': 'o', 'Ö': 'o'
            *   'ş': 's', 'Ş': 's'
            *   'ü': 'u', 'Ü': 'u'
        *   What about `I`? The prompt lists `I` in the uppercase list. I should probably map it to `i` just in case, or rely on `.lower()`. Since `I`.lower() is `i`, explicit mapping isn't strictly needed for ASCII `I`, but good for consistency if input contains Turkish-specific variants that look like `I`. But standard Python `str.lower()` handles `İ` -> `ı`. We want `İ` -> `i`. So explicit mapping `İ`: `i` is necessary.
        *   Wait, does the prompt imply `I` (Latin I) should be mapped? "büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü)". It lists `I` alongside Turkish uppercase letters. This suggests treating it as a character to normalize. Since `I`.lower() is already `i`, mapping `I` -> `i` is redundant but harmless.
        *   Wait, does the prompt imply `ı` (dotless i) should map to `i`? Yes ("ı→i").
        *   Does it imply `İ` (dotted capital I) should map to `i`? "büyük halleri ... de aynı şekilde". So yes.

    *   Plan:
        1. Define dict with all Turkish chars + their uppercase variants mapping to lowercase ASCII equivalents.
        2. Use `str.translate`.
        3. `.lower()` (to ensure any remaining non-mapped chars are lower).
        4. Regex replace non-alphanumeric sequence with `-`.
        5. Strip leading/trailing `-`.

    *   Wait, if I use `re.sub(r'[^a-z0-9]+', '-', text)`, does it handle the case where there is no match? Yes.
    *   Does it handle empty string? Yes.

    *   Code check:
        ```python
        def tr_slug(text: str) -> str:
            import re
            # Translation table for Turkish characters to ASCII lowercase
            trans_table = {
                'ç': 'c', 'Ç': 'c',
                'ğ': 'g', 'Ğ': 'g',
                'ı': 'i', 'İ': 'i',
                'ö': 'o', 'Ö': 'o',
                'ş': 's', 'Ş': 's',
                'ü': 'u', 'Ü': 'u'
            }
            
            # Create translation table object
            trans_map = str.maketrans(trans_table)
            
            # Apply translation and lowercase
            text = text.translate(trans_map).lower()
            
            # Replace non-alphanumeric sequences with single hyphen
            text = re.sub(r'[^a-z0-9]+', '-', text)
            
            # Strip leading/trailing hyphens
            return text.strip('-')
        ```
    *   Wait, `str.maketrans` takes a dict where keys are chars and values are strings (length 1). My dict has length 1 values. Correct.
    *   One detail: The prompt says "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character sequence outside letter and digit should be a single '-'). This supports `re.sub(r'[^a-z0-9]+', '-', text)`. If it meant char-by-char, it would likely say "her karakter" instead of "karakter dizisi". Also standard slug behavior.
    *   Wait, I need to check if `I` needs explicit mapping in the dict. The prompt lists `I` in the uppercase list. It's safer to include it or rely on `.lower()`. Since `I` is ASCII, `.lower()` handles it. But `İ` (Turkish Capital I) must be mapped explicitly because `.lower()` makes it `ı`, not `i`. So explicit mapping for `İ` -> `i` is required.
    *   Wait, does the prompt require `I` to map? "büyük halleri (Ç, Ğ, I, İ, Ö, Ş, Ü)". It lists `I`. If I don't put it in dict, `.lower()` handles it. But if I want to be explicit about following instructions:
    *   Actually, standard Turkish slug logic often treats `ı` and `İ` specially. The prompt explicitly says `ı→i`. And implies uppercase variants behave similarly. So `İ→i`.
    *   What about `I`? It's not a Turkish letter technically (it's Latin), but listed in the "uppercase variants" list of the instruction context. I will rely on `.lower()` for it, or add to dict if I want to be safe. Adding to dict doesn't hurt. But `str.maketrans` might complain if keys are not single chars? No, values must be length 1 strings.
    *   Let's stick to the specific Turkish letters mentioned: ç, ğ, ı, ö, ş, ü and their uppercase counterparts. I will add `I` -> `i` just in case, or rely on `.lower()`. Since `I` is already lowercase-able, explicit mapping isn't strictly necessary for correctness of ASCII output, but `İ` IS.
    *   Wait, one more thing: The prompt says "Türkçe harfler dönüşsün... büyük halleri ... de aynı şekilde". This implies the list provided covers all Turkish letters to be converted.
    *   I will include `I` in the mapping just to align with the instruction's explicit list of uppercase chars, even though it's redundant for ASCII lowercasing. Actually, better not to clutter if `.lower()` works. But wait, `İ`.lower() is `ı`. We want `i`. So `İ` MUST be in dict.
    *   Okay, final check on imports. Only standard library allowed? Yes. `re` is standard.

9.  **Formatting:**
    *   Single ```python block.
    *   No markdown outside the code block (except the block itself). Wait, "Sadece Python kodunu tek bir ```python bloğu içinde ver." -> Give ONLY the Python code inside a single python block. So no explanation text before or after.

10. **Final Code Verification:**
    *   Input: `Merhaba Dünya!`
    *   Translate: `merhaba dunya!` (assuming D->d, ü->u). Wait, `D`.lower() is `d`. `ü` -> `u`.
    *   Lowercase: `merhaba dunya!`
    *   Regex `[^a-z0-9]+`: Space becomes `-`, `!` becomes `-`. Result `merhaba-dunya--`. Wait.
        *   "Merhaba" (letters) -> "merhaba".
        *   " " (space) -> "-".
        *   "Dünya" (letters) -> "dunya".
        *   "!" -> "-".
        *   Combined: `merhaba-dunya-`.
    *   Strip `-`: `merhaba-dunya`. Matches example.
    *   Input: `Merhaba  Dünya` (two spaces).
    *   Regex `[^a-z0-9]+`: "  " -> "-". Result `merhaba-dunya`. Correct for slug behavior.

    *   Wait, does the prompt require collapsing? "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun." (Every character sequence outside letter and digit should be a single '-').
        *   If I have "!!", that is a sequence of non-alphanumeric chars. It becomes one "-". This matches `re.sub(r'[^a-z0-9]+', '-', text)`.
        *   So yes, collapsing is the correct interpretation of "karakter dizisi" (character string/sequence).

    *   One detail: The prompt asks for `tr_slug(text: str) -> str`. I should define this function.
    *   Imports inside or outside? Usually imports at top level are fine. But to keep it clean, put import inside or assume environment has it. Standard practice is top-level import. I will put `import re` at the top of the block.

    *   Wait, one constraint: "Sadece Python kodunu tek bir ```python bloğu içinde ver." (Give ONLY the Python code inside a single python block).
    *   So no text like "Here is the code:". Just the block.

    *   Double check `str.maketrans`. In Python 3, `str.maketrans(dict)` returns a translation table. `text.translate(table)`. Correct.

    *   Wait, I should ensure `I` (Latin Capital I) is handled correctly if it appears. `.lower()` handles it to `i`. So explicit mapping not needed for `I`, but `İ` needs it.
    *   Wait, does the prompt imply `ı` (dotless i) maps to `i`? Yes ("ı→i").
    *   Does it imply `İ` (dotted capital I) maps to `i`? "büyük halleri ... de aynı şekilde". So yes.

    *   Final check on imports: Is `re` allowed? Usually yes for standard library. If not, manual loop is needed. But regex is standard Python. I'll use it.
    *   Wait, to be safest and most "Pythonic" without external deps (though re is built-in), regex is fine.

    *   One nuance: `str.maketrans` with a dict where values are strings of length 1 works.
    *   Example: `{'ç': 'c'}`.
    *   Code looks solid.

```python
import re

def tr_slug(text: str) -> str:
    # Translation table for Turkish characters to ASCII lowercase equivalents
    trans_table = {
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        'ı': 'i', 'İ': 'i',
        'ö': 'o', 'Ö': 'o',
        'ş': 's', 'Ş': 's',
        'ü': 'u', 'Ü': 'u'
    }
    
    # Create translation table and apply it, then convert to lowercase
    text = text.translate(str.maketrans(trans_table)).lower()
    
    # Replace sequences of non-alphanumeric characters with a single hyphen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove leading and trailing hyphens
    return text.strip('-')
```

Wait, I should check if `I` needs to be in the dict. The prompt lists `I` in the uppercase list of Turkish letters. While `I`.lower() is `i`, adding it explicitly ensures compliance with "büyük halleri ... de aynı şekilde" instruction regarding that specific character listed. However, since `.lower()` handles ASCII `I` correctly to `i`, omitting it from dict but keeping `.lower()` call achieves the same result for ASCII `I`. But `İ` is critical. I will leave `I` out of dict and rely on `.lower()`, as adding redundant keys doesn't change behavior, but relying on standard casing rules is cleaner unless specific mapping overrides them (which it does for `İ`). Actually, to be strictly compliant with the instruction "büyük halleri ... de aynı şekilde", I should ensure all listed uppercase chars map. Since `I` maps to `i` via `.lower()`, and others map via dict, it's fine. But wait, if I don't put `I` in dict, does it matter? No.
However, I will add `I`: 'i' just to be explicit about the instruction list, though redundant. Actually, no, keep it clean. The critical one is `İ`.

Wait, one more check: "Harf ve rakam dışındaki her karakter dizisi tek bir '-' olsun."
Does this mean if I have "Merhaba", result should not change? Yes.
If I have "Merhaba 123", result "merhaba-123".
My regex `[^a-z0-9]+` keeps letters and digits, replaces others with `-`. Correct.

One final check on imports: The prompt asks for the function code. Usually, imports should be included if used. I will include `import re`.

Wait, one detail in the instruction: "Sadece Python kodunu tek bir ```python bloğu içinde ver."
This means I shouldn't output any text outside the block.

Let's refine the translation table to ensure it covers all requirements precisely.
The prompt lists specific mappings. I will include them exactly.
`ç→c, ğ→g, ı→i, ö→o, ş→s, ü→u`.
Uppercase: `Ç, Ğ, I, İ, Ö, Ş, Ü`.
So mapping for uppercase should be to lowercase ASCII equivalents.
My dict has `Ç`: 'c', etc. It does not have `I` -> 'i'. But `I`.lower() is 'i'. So it's fine.
Wait, if the input contains `İ`, `.lower()` makes it `ı`. My dict maps `İ` to `i`. This overrides `.lower()` behavior for that char? No, `translate` happens first. Then `.lower()`.
If I translate `İ` -> `i`, then `.lower()` keeps it as `i`. Correct.
If I don't translate `İ`, `.lower()` makes it `ı`. Incorrect (we want `i`). So explicit mapping for `İ` is mandatory.
What about `I`? If input has `I`, translate does nothing, `.lower()` makes it `i`. Correct.
So dict needs `İ`: 'i'.

Wait, I should check if `str.maketrans` works with a dictionary directly in Python 3. Yes.
Code looks good.

One detail: `text.strip('-')` removes leading and trailing hyphens. It does not remove internal ones (handled by regex). Correct.

Final check on the example: `tr_slug("Merhaba Dünya!") == "merhaba-dunya"`.
My logic:
1. Translate: 'ü' -> 'u'. 'D' is ASCII, no change in dict but lowercased later.
2. Lowercase: 'M'->'m', 'D'->'d', '!' stays '!'.
3. Regex `[^a-z0-9]+`: Space becomes '-', '!' becomes '-'. String: "merhaba-dunya--". Wait.
   Input: "Merhaba Dünya!"
   Chars: M e r h a b a [space] D ü n y a !
   Lowered: m e r h a b a [space] d u n y a !
   Regex replace non-alpha-num with '-':
   'm'...'a' -> kept.
   ' ' -> replaced by '-' (sequence of 1 char).
   'd'...'a' -> kept.
   '!' -> replaced by '-'.
   Result: "merhaba-dunya-".
4. Strip '-': "merhaba-dunya".
Matches example.

Wait, what if input is "Merhaba Dünya!!"?
Regex replaces "!" and "!" with "-" each? No, `[^a-z0-9]+` matches one or more non-alphanumeric chars as a

## Cevap

(boş)

## Notlandırılan kod/komut

```
import re

def tr_slug(text: str) -> str:
    # Translation table for Turkish characters to ASCII lowercase equivalents
    trans_table = {
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        'ı': 'i', 'İ': 'i',
        'ö': 'o', 'Ö': 'o',
        'ş': 's', 'Ş': 's',
        'ü': 'u', 'Ü': 'u'
    }
    
    # Create translation table and apply it, then convert to lowercase
    text = text.translate(str.maketrans(trans_table)).lower()
    
    # Replace sequences of non-alphanumeric characters with a single hyphen
    text = re.sub(r'[^a-z0-9]+', '-', text)
    
    # Remove leading and trailing hyphens
    return text.strip('-')
```
