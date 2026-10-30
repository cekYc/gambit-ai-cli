# kod-sure-js · puan 1.00

**Not:** 11/11 test

## Prompt

JavaScript'te (Node.js) `parseDuration(str)` fonksiyonunu yaz. "1h 30m 15s", "45m", "2h", "90s", "1h15s" gibi
metinleri toplam saniyeye çevirsin. Birimler: h (saat), m (dakika), s (saniye). Her birim en fazla bir kez ve
bu sırayla gelir; aralarında boşluk olabilir de olmayabilir de. Geçersiz girdide (boş metin, bilinmeyen birim,
sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın.
Fonksiyonu `module.exports = { parseDuration };` ile dışa aktar.
Sadece JavaScript kodunu tek bir ```javascript bloğu içinde ver.

## Düşünme

*   Goal: Write a Node.js function `parseDuration(str)` that converts duration strings into total seconds.
    *   Input formats: "1h 30m 15s", "45m", "2h", "90s", "1h15s".
    *   Units: `h` (hours), `m` (minutes), `s` (seconds).
    *   Rules:
        *   Each unit appears at most once.
        *   Order must be h -> m -> s.
        *   Spaces are optional between units.
        *   Error conditions: Empty string, unknown units, non-numeric values before units, wrong order, duplicate units.
    *   Output format: Total seconds (integer).
    *   Export format: `module.exports = { parseDuration };`.
    *   Constraint: Only one ```javascript block containing the code.

    *   Input string needs to be parsed into components of number + unit.
    *   Regex approach seems best for splitting/matching.
    *   Pattern: A sequence of (number)(unit).
    *   Example "1h 30m 15s" -> `[{val: 1, unit: 'h'}, {val: 30, unit: 'm'}, {val: 15, unit: 's'}]`.

    *   `str.trim()` to handle leading/trailing whitespace.
    *   If empty string -> Error.
    *   Regex for a single component: `(\d+)([hms])`.
    *   Wait, the requirement says "wrong order" and "duplicate units". A simple regex match might not catch everything if I just use `matchAll`.

    Let's refine the parsing logic:
    1.  Check if string is empty or whitespace only -> Error.
    2.  Use a regular expression to find all matches of (number)(unit).
        *   Regex pattern for a single unit-value pair: `/(\d+)([hms])/g`.
    3.  However, the user says "wrong order" and "duplicate units". This implies we need to validate the *entire* string structure.

    Let's try this approach:
    1.  Split the input by spaces (or just treat it as a continuous stream). Actually, since spaces are optional, let's use a regex that captures all valid pairs and then check if the reconstructed string matches the original (ignoring whitespace) to detect invalid characters or wrong order/duplicates.

    *Wait*, "wrong order" means `1m 1h` is invalid.
    "Duplicate units" means `1h 1h` is invalid.
    "Unknown unit" means `1x` is invalid.
    "Non-numeric value" means `h` or `abc h` is invalid.

    *Better approach:*
    Use a regex to find all occurrences of `(\d+)([hms])`.
    Then, check if the sum of lengths of these matches (plus spaces) equals the original string length? No, that's too complex because of optional spaces.

    Let's use a more robust parsing:
    1.  Check for empty/whitespace -> Error.
    2.  Use `matchAll` with `/(\d+)([hms])/g`.
    3.  Store results in an array of objects `{ value, unit }`.
    4.  Validation steps:
        a. Check if the input string contains any characters that aren't digits, 'h', 'm', 's', or whitespace. If yes -> Error (unknown units/invalid chars).
        b. Check for duplicates in the extracted units.
        c. Check order of units (h < m < s).
        d. Ensure no "missing" numbers between units (e.g., `1h m` is invalid, but regex might just skip it).

    *Actually*, a very clean way to handle this:
    Use a single Regex that describes the *entire* valid pattern.
    Pattern for one unit: `(\d+[hms])`.
    Since spaces are optional and order is fixed (h then m then s):
    The string must match exactly: `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$`

    Let's test this pattern against inputs:
    - "1h 30m 15s" -> Matches.
    - "45m" -> Matches.
    - "2h" -> Matches.
    - "90s" -> Matches.
    - "1h15s" -> Matches (Wait, the regex `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` allows skipping 'm').
    - "1h 30m 15s" matches? Yes.
    - "1h 15s" matches? Yes (the middle group is optional).

    Wait, what about invalid inputs like:
    - "1h 1h" -> Regex `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` will NOT match "1h 1h". It expects only one 'h' group. This is perfect!
    - "1m 1h" -> Will not match because the order in regex is h, then m, then s. Perfect!
    - "1x" -> Will not match. Perfect!
    - "" (empty) -> Need to check explicitly.

    Let's refine the Regex: `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$`
    Wait, if I use this regex on "1h 30m 15s":
    Group 1: 1h
    Group 2: 30m
    Group 3: 15s
    Total seconds = $1*3600 + 30*60 + 15$.

    What if the input is " "? The regex `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` will match an empty string (all groups optional).
    So:
    1. Trim input.
    2. If trimmed string is empty -> Error.
    3. Test against `/^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/`.
    4. If it doesn't match, throw error (covers unknown units, wrong order, duplicates, non-numeric).
    5. If it matches, extract the numbers using `match` or by parsing groups.

    Wait, there is one edge case: "1h 30m 15s" vs "1h  30m". The regex handles multiple spaces if I use `\s*`.
    What about "1h m"? The regex `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` will not match "1h m" because the 'm' part expects a digit before it. This is correct.

    Let's double check:
    - "1h 30m 15s": Match.
    - "45m": Match.
    - "2h": Match.
    - "90s": Match.
    - "1h15s": Match.
    - "": Error (empty).
    - "1x": No match -> Error.
    - "1h 1h": No match -> Error.
    - "1m 1h": No match -> Error.
    - "1h 30": No match (missing unit) -> Error.

    Wait, one detail: `(\d+h)?` matches "1h". If the input is "1h ", it matches.
    If the input is "1h 2m 3s", it works.
    What if the user provides "1h  30m"? The regex `\s*` handles multiple spaces.

    One potential issue: `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` matches an empty string. I must check for empty input first.
    Also, if the user provides " ", it's technically a match of the optional groups but we should treat it as invalid/empty.

    Let's refine the regex to ensure at least one unit is provided:
    `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` and then check if `match[0]` is empty or just whitespace. Actually, a better way is to use a lookahead or simply check the result of the match.

    Wait, there's a flaw in my regex logic for "1h 30m 15s".
    If I use `.match(/^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/)`, and input is "1h 30m 15s":
    `matches[1]` = "1h"
    `matches[2]` = "30m"
    `matches[3]` = "15s"

    Let's write the code.

    ```javascript
    function parseDuration(str) {
      if (typeof str !== 'string' || str.trim() === '') {
        throw new Error("Invalid input: String must not be empty.");
      }

      // Regex to match valid patterns: h, then m, then s (all optional)
      // This regex ensures order and prevents duplicates/unknown units
      const regex = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
      const match = str.trim().match(regex);

      if (!match || (match[1] === undefined && match[2] === undefined && match[3] === undefined)) {
        // The regex might match an empty string if all groups are optional, 
        // but we already checked for empty input.
        // However, "1h 1h" won't match the pattern because of the structure.
        throw new Error("Invalid duration format.");
      }

      let totalSeconds = 0;

      if (match[1]) {
        totalSeconds += parseInt(match[1], 10) * 3600; // Note: regex group includes 'h'
        // Wait, match[1] is "1h". I need to extract the number.
      }
      // ...
    }
    ```

    Wait, `parseInt("1h")` in JS actually returns `1`. This is a very handy feature of `parseInt`. It parses until it hits a non-numeric character. So `parseInt("1h", 10)` is `1`.

    Let's re-verify:
    Input "1h 30m":
    `match[1]` = "1h" -> `parseInt("1h")` = 1.
    `match[2]` = "30m" -> `parseInt("30m")` = 30.
    `match[3]` = undefined.

    Input "1h 15s":
    `match[1]` = "1h"
    `match[2]` = undefined
    `match[3]` = "15s"

    Wait, what if the input is "1h  "? The regex `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` will match it. But we need to ensure that there's actually content.
    Actually, if the string is `"1h "`, `match[1]` is `"1h"`.

    Let's refine the regex and logic:
    ```javascript
    function parseDuration(str) {
      if (typeof str !== 'string' || str.trim() === '') {
        throw new Error("Invalid input");
      }

      const trimmed = str.trim();
      // This pattern ensures order h -> m -> s and allows optional spaces
      const regex = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
      const match = trimmed.match(regex);

      // If it doesn't match the structure, or if it matched but resulted in nothing (empty string)
      if (!match || !trimmed.replace(/\s/g, '')) {
         throw new Error("Invalid duration format");
      }

      let seconds = 0;
      if (match[1]) seconds += parseInt(match[1], 10) * 3600;
      if (match[2]) seconds += parseInt(match[2], 10) * 60;
      if (match[3]) seconds += parseInt(match[3], 10);

      return seconds;
    }
    ```

    Wait, one edge case: `parseInt("1h")` works, but what if the input is `"1 h"`? The regex `(\d+h)` does NOT allow a space between digit and unit. The prompt says "1h 30m", not "1 h 30 m". So my regex is correct for the requirement.

    Let's test "1h 30m 15s" with the logic:
    `match[1]` = "1h" -> `parseInt("1h")` = 1. $1 * 3600 = 3600$.
    `match[2]` = "30m" -> `parseInt("30m")` = 30. $30 * 60 = 1800$.
    `match[3]` = "15s" -> `parseInt("15s")` = 15. $15 * 1 = 15$.
    Total: 5415. Correct.

    Test "1h15s":
    `match[1]` = "1h"
    `match[2]` = undefined
    `match[3]` = "15s"
    Total: $3600 + 15 = 3615$. Correct.

    Test "45m":
    `match[1]` = undefined
    `match[2]` = "45m"
    `match[3]` = undefined
    Total: $45 * 60 = 2700$. Correct.

    Test "90s":
    `match[1]` = undefined
    `match[2]` = undefined
    `match[3]` = "90s"
    Total: 90. Correct.

    Test "1h 1h":
    Regex `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$` will NOT match `"1h 1h"` because after the first `1h`, it expects either a space then `m` or `s`. It won't find another `h`.
    Wait, let me double check that.
    Regex: `^(\d+h)?\s*(\d+m)?\s*(\d+s)?$`
    String: `"1h 1h"`
    `match[1]` matches `"1h"`.
    Then it looks for `\s*` (matches space).
    Then it looks for `(\d+m)?`. It sees "1", but the next char is "h". So group 2 doesn't match.
    Then it looks for `(\d+s)?`. Group 3 doesn't match.
    The regex reaches end of string `$`, but we are at index 3 (the second '1'). The regex fails to reach the end of the string because there is more text left that wasn't consumed by the optional groups.
    So `match` will be `null`. Correct!

    Test "1m 1h":
    `match[1]` tries to match `(\d+h)?`. It sees "1m". No match for group 1.
    It moves to `\s*`. Matches nothing.
    It moves to `(\d+m)?`. Matches "1m".
    It moves to `\s*`. Matches nothing.
    It moves to `(\d+s)?`. Doesn't match "1h".
    Regex fails because it didn't reach `$`. Correct!

    Test "1h 30": (Missing unit)
    `match[1]` matches "1h".
    `\s*` matches space.
    `(\d+m)?` doesn't match "30" because there is no 'm'.
    `(\d+s)?` doesn't match "30" because there is no 's'.
    Regex fails to reach `$`. Correct!

    Test "1h 20x": (Unknown unit)
    Fails. Correct.

    One final check: The prompt says `Error fırlatsın` (throw an error). I should use `throw new Error(...)`.

    Wait, what if the input is `"1h30m"`? My regex handles it because of `\s*`.
    What about `" 1h "`? `.trim()` handles it.

    One detail: The prompt says "Her birim en fazla bir kez ve bu sırayla gelir". This is exactly what the regex structure `^...?...?...?$` enforces.

    Let's refine the error messages to be generic or specific as needed.
    The requirement: "Geçersiz girdide (boş metin, bilinmeyen birim, sayısı olmayan birim, yanlış sıra, tekrar eden birim) Error fırlatsın."

    Code structure:
    ```javascript
    function parseDuration(str) {
      if (typeof str !== 'string' || str.trim() === '') {
        throw new Error("Invalid input");
      }

      const trimmed = str.trim();
      // Regex explanation:
      // ^ : Start of string
      // (\d+h)? : Optional group for hours
      // \s* : Optional whitespace
      // (\d+m)? : Optional group for minutes
      // \s* : Optional whitespace
      // (\d+s)? : Optional group for seconds
      // $ : End of string
      const regex = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
      const match = trimmed.match(regex);

      // If no match, or if the input was just whitespace (though trim() handles that)
      // Or if it matched but didn't actually contain any time units (e.g., " ")
      if (!match || !trimmed.replace(/\s/g, '')) {
        throw new Error("Invalid duration format");
      }

      let totalSeconds = 0;
      if (match[1]) totalSeconds += parseInt(match[1], 10) * 3600;
      if (match[2]) totalSeconds += parseInt(match[2], 10) * 60;
      if (match[3]) totalSeconds += parseInt(match[3], 10);

      return totalSeconds;
    }

    module.exports = { parseDuration };
    ```

    Wait, there's one tiny edge case: `parseInt("1h")` is fine, but what if the input was `"1.5h"`? The regex `\d+` only matches integers. The prompt says "sayısı olmayan birim" (unit without number) should throw error. My regex handles this because `\d+` requires at least one digit. If someone enters `.5h`, it won't match the pattern.

    Wait, what if input is `"1h 30m 15s "`? The `.trim()` will handle trailing space.
    What about `"1h  30m"` (double space)? `\s*` handles it.

    One more check: "sayısı olmayan birim" -> e.g., "h m s".
    Regex `(\d+h)` requires digits before 'h'. So "h" will not match. Correct.

    Final code structure looks solid.

    ```javascript
    function parseDuration(str) {
      if (typeof str !== 'string' || str.trim() === '') {
        throw new Error("Invalid input: String must not be empty.");
      }

      const trimmed = str.trim();
      // Regex ensures order (h, m, s), single occurrence of each, and valid units.
      const regex = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
      const match = trimmed.match(regex);

      // If it doesn't match the pattern or is just whitespace/empty after matching
      if (!match || !trimmed.replace(/\s/g, '')) {
        throw new Error("Invalid duration format.");
      }

      let totalSeconds = 0;
      if (match[1]) totalSeconds += parseInt(match[1], 10) * 3600;
      if (match[2]) totalSeconds += parseInt(match[2], 10) * 60;
      if (match[3]) totalSeconds += parseInt(match[3], 10);

      return totalSeconds;
    }

    module.exports = { parseDuration };
    ```

    Wait, I should check if `parseInt` is safe here. Since the regex only allows digits followed by 'h', 'm', or 's', `parseInt` will definitely work as intended.

    One last thing: "1h 30m 15s" -> $3600 + 1800 + 15 = 5415$.
    "90s" -> $90$.
    Everything seems correct.

## Cevap

```javascript
function parseDuration(str) {
  if (typeof str !== 'string' || str.trim() === '') {
    throw new Error("Invalid input: String must not be empty.");
  }

  const trimmed = str.trim();

  /**
   * Regex Açıklaması:
   * ^ : Metnin başlangıcı
   * (\d+h)? : Opsiyonel; bir veya daha fazla rakam ve 'h' (saat)
   * \s* : Opsiyonel boşluklar
   * (\d+m)? : Opsiyonel; bir veya daha fazla rakam ve 'm' (dakika)
   * \s* : Opsiyonel boşluklar
   * (\d+s)? : Opsiyonel; bir veya daha fazla rakam ve 's' (saniye)
   * $ : Metnin sonu
   * 
   * Bu yapı sayesinde:
   * - Sıralama kontrol edilir (h -> m -> s).
   * - Her birim en fazla bir kez kullanılabilir.
   * - Bilinmeyen birimler veya yanlış karakterler eşleşmeyi bozar.
   */
  const regex = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
  const match = trimmed.match(regex);

  // Eğer regex eşleşmezse (yanlış sıra, bilinmeyen birim vb.) veya 
  // metin sadece boşluklardan oluşuyorsa hata fırlatılır.
  if (!match || !trimmed.replace(/\s/g, '')) {
    throw new Error("Invalid duration format.");
  }

  let totalSeconds = 0;

  // match[1] -> "1h" gibi bir değer döner, parseInt bunu 1 olarak okur.
  if (match[1]) {
    totalSeconds += parseInt(match[1], 10) * 3600;
  }
  if (match[2]) {
    totalSeconds += parseInt(match[2], 10) * 60;
  }
  if (match[3]) {
    totalSeconds += parseInt(match[3], 10);
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```

## Notlandırılan kod/komut

```
function parseDuration(str) {
  if (typeof str !== 'string' || str.trim() === '') {
    throw new Error("Invalid input: String must not be empty.");
  }

  const trimmed = str.trim();

  /**
   * Regex Açıklaması:
   * ^ : Metnin başlangıcı
   * (\d+h)? : Opsiyonel; bir veya daha fazla rakam ve 'h' (saat)
   * \s* : Opsiyonel boşluklar
   * (\d+m)? : Opsiyonel; bir veya daha fazla rakam ve 'm' (dakika)
   * \s* : Opsiyonel boşluklar
   * (\d+s)? : Opsiyonel; bir veya daha fazla rakam ve 's' (saniye)
   * $ : Metnin sonu
   * 
   * Bu yapı sayesinde:
   * - Sıralama kontrol edilir (h -> m -> s).
   * - Her birim en fazla bir kez kullanılabilir.
   * - Bilinmeyen birimler veya yanlış karakterler eşleşmeyi bozar.
   */
  const regex = /^(\d+h)?\s*(\d+m)?\s*(\d+s)?$/;
  const match = trimmed.match(regex);

  // Eğer regex eşleşmezse (yanlış sıra, bilinmeyen birim vb.) veya 
  // metin sadece boşluklardan oluşuyorsa hata fırlatılır.
  if (!match || !trimmed.replace(/\s/g, '')) {
    throw new Error("Invalid duration format.");
  }

  let totalSeconds = 0;

  // match[1] -> "1h" gibi bir değer döner, parseInt bunu 1 olarak okur.
  if (match[1]) {
    totalSeconds += parseInt(match[1], 10) * 3600;
  }
  if (match[2]) {
    totalSeconds += parseInt(match[2], 10) * 60;
  }
  if (match[3]) {
    totalSeconds += parseInt(match[3], 10);
  }

  return totalSeconds;
}

module.exports = { parseDuration };
```
