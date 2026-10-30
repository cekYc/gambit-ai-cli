# term-grep · puan 1.00

**Not:** doğru

## Prompt

Windows'ta PowerShell 7 (pwsh) kullanıyorum. Bulunduğum klasörün yapısı şöyle:
```text
.
├── logs
│   ├── app1.log
│   ├── app2.log
│   └── old
│       └── app0.log
├── data
│   ├── notes.txt
│   ├── todo.txt
│   ├── report.csv
│   ├── big.bin
│   └── image.png
└── readme.md
```
data/report.csv dosyasının ilk satırı: date,product,amount

Görev: logs klasöründeki (alt klasörler dahil) tüm .log dosyalarında 'ERROR' geçen satırların toplam sayısını yazdır (sadece sayı).

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Düşünme

Thinking Process:

1.  **Analyze the Request:**
    *   Role: Experienced Software Developer.
    *   Task: Write a PowerShell command (PowerShell 7 / pwsh) to count lines containing 'ERROR' in all `.log` files within the `logs` folder (including subfolders).
    *   Input Structure:
        ```text
        .
        ├── logs
        │   ├── app1.log
        │   ├── app2.log
        │   └── old
        │       └── app0.log
        ├── data
        │   ...
        └── readme.md
        ```
    *   Specific Requirement: Output only the count (number).
    *   Constraint 1: Single line command.
    *   Constraint 2: Use `;` to combine commands if necessary.
    *   Constraint 3: Provide output inside a single ```powershell code block.
    *   Language: Turkish (based on the prompt).

2.  **Determine the Logic:**
    *   Target directory: `.logs` (relative path from current location, which is `.`).
    *   Target files: All `.log` files recursively (`-Recurse`).
    *   Search pattern: 'ERROR'.
    *   Action: Count lines containing this pattern.
    *   Output: Just the number.

3.  **Drafting the PowerShell Command:**
    *   Get all log files: `Get-ChildItem -Path logs -Recurse -Filter *.log`
    *   Select content: `Select-Object -ExpandProperty Content` (or pipe to `Select-String`).
    *   Search for 'ERROR': `Select-String -Pattern 'ERROR'`.
    *   Count matches: `.Count` property of the result.

    *Option 1 (Using Select-String):*
    ```powershell
    Get-ChildItem logs -Recurse -Filter *.log | Select-String -Pattern 'ERROR' | Measure-Object -Line
    ```
    Wait, `Measure-Object` counts lines where the match occurred. However, if a line has multiple "ERROR"s, it still counts as one line usually unless `-Count` is used differently. The prompt asks for "satırların toplam sayısı" (total number of lines). So counting lines containing 'ERROR' is correct.
    `Measure-Object -Line` returns an object with `.Lines` property? No, `Measure-Object` without arguments counts objects passed to it. If I pipe `Select-String`, each match creates a line in the output stream. Actually, `Select-String` outputs one object per *match* by default (unless `-SimpleMatch` or specific settings). Wait, standard behavior: `Select-String -Pattern 'ERROR'` returns an object for every occurrence of the pattern on a line? No, it returns one object per match found in the file. If a line has "ERROR ERROR", it counts as 2 matches.
    The prompt asks for "satırların toplam sayısı" (total number of lines). This implies unique lines containing 'ERROR', not total occurrences of the word.
    So, I need to count *lines*, not *matches*.

    *Refined Logic:*
    1. Get files: `Get-ChildItem logs -Recurse -Filter *.log`
    2. Read content and filter lines containing 'ERROR'.
    3. Count those lines.

    *Approach A (Select-String + Group):*
    ```powershell
    Get-Content (Get-ChildItem logs -Recurse -Filter *.log) | Select-String -Pattern 'ERROR' | Measure-Object -Line
    ```
    Wait, `Measure-Object` on the output of `Select-String`. If I pipe `Select-String`, it outputs objects. Each object represents a match. If I want line count (unique lines), I should use `-Unique` or group by line content? No, usually "satırların sayısı" means how many lines have at least one ERROR.
    Actually, standard PowerShell usage for this specific task:
    `Get-Content logs\*.log -Recurse | Select-String 'ERROR' | Measure-Object` -> This counts matches (occurrences).
    To count lines containing the string:
    `Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Get-Content $_.FullName } | Where-Object { $_ -match 'ERROR' } | Measure-Object`
    Or simpler using `Select-String`:
    `Select-String -Path (Get-ChildItem logs -Recurse -Filter *.log).FullName -Pattern 'ERROR' -SimpleMatch` -> Still counts matches.

    Let's look at the requirement again: "logs klasöründeki ... tüm .log dosyalarında 'ERROR' geçen satırların toplam sayısını yazdır".
    Translation: Write the total number of lines where 'ERROR' appears in all .log files...
    This usually means count the lines that contain the string. If a line has "ERROR ERROR", it is one line.

    Correct PowerShell logic for counting lines containing a pattern across multiple files recursively:
    ```powershell
    Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Get-Content $_.FullName } | Where-Object { $_ -match 'ERROR' } | Measure-Object
    ```
    This outputs an object with `.Count`. To get just the number: `... | Measure-Object | Select-Object -ExpandProperty Count` or `... | Measure-Object -Line`. Wait, `Measure-Object` on lines counts objects. If I pipe lines to it, it counts them.

    Let's try a more concise version using `Select-String`:
    ```powershell
    Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Select-String $_.FullName -Pattern 'ERROR' } | Measure-Object -Line
    ```
    Wait, `Measure-Object` on the output of `Select-String`. If I use `-SimpleMatch`, it might behave differently.
    Actually, the most robust way to count lines containing a pattern is:
    1. Get all log files.
    2. Read them line by line (or stream).
    3. Filter lines matching 'ERROR'.
    4. Count.

    Command:
    ```powershell
    Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Get-Content $_ } | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```
    This is a bit long. Can we shorten it?
    `Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Get-Content $_ }` creates an array of lines per file.
    Better:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Select-String 'ERROR' | Measure-Object -Line
    ```
    Wait, `Select-String` with `-Path` takes a path or array of paths. If I pass an array of full names to `-Path`, it searches all files.
    Command:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Select-String 'ERROR' | Measure-Object -Line
    ```
    Wait, `Select-String` output is objects representing matches. If I use `-SimpleMatch`, it's simpler but still counts occurrences usually? No, `Measure-Object -Line` on the stream of `Select-String` results counts how many *objects* were passed to it. Each object in `Select-String` result represents a match (line + context). So if one line has 2 errors, it generates 2 objects.
    To count lines containing 'ERROR' (regardless of frequency):
    We need to ensure we don't double count lines with multiple errors.
    However, often in these tasks, "satır sayısı" implies counting the occurrences of lines that match. If a line matches, it counts as 1. `Select-String` returns one object per match found on a line? No, by default `Select-String` returns an object for every occurrence of the pattern.
    Example: Line "ERROR ERROR". Pattern 'ERROR'. Output: 2 objects.
    If I want to count lines (unique lines containing error), I need to group or use `-SimpleMatch` with specific logic? No, `-SimpleMatch` is for whole line matching.

    Let's check `Select-String` behavior again.
    `Select-String -Pattern 'ERROR'` returns objects where `.Line` property contains the match. If a line has multiple matches, it returns multiple objects.
    To count lines containing 'ERROR':
    We can use `Where-Object { $_ -match 'ERROR' } | Measure-Object`. This counts lines if we process file content directly.

    Best approach for "lines containing ERROR":
    ```powershell
    Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Get-Content $_.FullName } | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```
    This is safe and accurate for "lines".

    Can we make it one line? Yes.
    Can we use `;` to combine? The prompt says "gerekirse komutları ; ile birleştir" (if necessary, join commands with ;). Since this is a single pipeline, no need for semicolons unless I want to set variables or something. But the simplest one-liner is preferred.

    Wait, `Get-Content` might be slow on huge files compared to streaming.
    Alternative:
    ```powershell
    Select-String -Path (Get-ChildItem logs -Recurse -Filter *.log).FullName -Pattern 'ERROR' | Measure-Object -Line
    ```
    Wait, `Measure-Object -Line` counts lines in the input stream. The input stream is the output of `Select-String`. Each object from `Select-String` represents a match. If I want to count *lines* (where at least one error exists), not *matches*, this might be tricky with standard `Select-String`.
    However, usually in these coding interview style questions, "satırların sayısı" often implies counting the matches if they are on different lines. But strictly speaking, a line is a line.
    If I use:
    ```powershell
    Get-Content (Get-ChildItem logs -Recurse -Filter *.log) | Where-Object { $_ -match 'ERROR' } | Measure-Object
    ```
    This counts lines containing ERROR correctly.

    Let's refine the command to be concise and correct.
    `Get-ChildItem` returns FileInfo objects.
    `(Get-ChildItem logs -Recurse -Filter *.log).FullName` gives paths.
    `Select-String -Path ... -Pattern 'ERROR'` finds matches.
    To count lines containing the pattern (not occurrences):
    We can use `-SimpleMatch`? No, that checks if the whole line is the string.
    We need to ensure we don't double count.
    Actually, `Select-String` output objects have a `.Line` property. If I pipe this to `Group-Object -Property Line`, then measure... too complex for one liner.

    Wait, there is a simpler way often accepted in PowerShell contexts:
    ```powershell
    Get-ChildItem logs -Recurse -Filter *.log | ForEach-Object { Select-String $_.FullName -Pattern 'ERROR' } | Measure-Object -Line
    ```
    If I use `Measure-Object -Line`, it counts the number of lines in the input stream. The input stream is the output of `Select-String`. Each object from `Select-String` corresponds to a match. If one line has 2 errors, `Select-String` outputs 2 objects. `Measure-Object -Line` will count them as 2? No, `Measure-Object` counts *objects* passed to it by default unless `-Line` is specified on the input stream (which implies counting lines of text).
    Wait, if I pipe objects to `Measure-Object`, it counts objects. If I use `-Line`, it tries to count lines in the string representation? No.
    Actually, `Measure-Object -Line` counts the number of *lines* in the input stream provided by PowerShell's pipeline. Since `Select-String` outputs one object per match (not per line), this is risky if a line has multiple errors.

    Let's stick to the most reliable method for "count lines containing X":
    1. Get files.
    2. Read content.
    3. Filter lines matching regex.
    4. Count.

    Command:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | ForEach-Object { Get-Content $_ } | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```
    This is verbose.

    Can we do:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```
    This works. `Get-Content` on an array of paths reads all files line by line into the pipeline.

    Wait, is there a shorter way?
    `Select-String` has `-SimpleMatch`. If I use `-Pattern 'ERROR'`, it finds occurrences.
    To count lines:
    ```powershell
    Select-String -Path (Get-ChildItem logs -Recurse -Filter *.log).FullName -Pattern 'ERROR' | Group-Object Line | Measure-Object
    ```
    Too complex.

    Let's go with the `Get-Content` approach, it is standard for "count lines".
    To make it a single line command:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```

    Wait, `Measure-Object` returns an object. `Select-Object -ExpandProperty Count` extracts the number.
    Is there a way to output just the number without extra objects? Yes, `... | Measure-Object`. The default output of `Measure-Object` is a table with "Count". But sometimes it outputs the whole object. To ensure *only* the number (e.g., 5), `Select-Object -ExpandProperty Count` is best. Or just `... | Measure-Object.Count`? No, property access on pipeline output isn't direct like that in one line without variable assignment usually, unless using subexpression `$(...)` but we need to print it.
    Actually, `Measure-Object` outputs an object with properties Count, Average, etc. If I just pipe it, PowerShell displays the table. The user wants "sadece sayı" (only number).
    So `... | Select-Object -ExpandProperty Count` is necessary to print just the integer value cleanly without headers or extra columns.

    Wait, one more optimization: `Get-ChildItem logs -Recurse -Filter *.log` returns FileInfo objects. We can use `-File` flag? No need.
    Also, `logs` folder exists in current directory.
    
    Refined Command:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```

    Wait, `Measure-Object` without arguments counts objects. If I pipe lines to it, it counts lines (objects in the stream are lines of text). So `Measure-Object` is sufficient if we ensure each line is an object. `Get-Content` outputs strings (lines). Each string is an object.
    So `(Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object` will output a table with Count column.
    To get *only* the number: `... | Select-Object -ExpandProperty Count`.

    Is there any risk? `Get-Content` reads whole file into memory line by line. It's fine for standard logs.
    
    Let's check if we can use `Select-String` with `-Count`? No, that counts matches.
    
    Wait, I should verify the output format requirement: "sadece sayı" (only number).
    If I run `... | Measure-Object`, PowerShell outputs:
    ```
    Count : 5
    ```
    This is not just a number. It's an object representation.
    So `Select-Object -ExpandProperty Count` ensures it prints "5".

    Wait, can we use `$()` subexpression?
    No need for variable assignment if we want to print directly.
    
    Final check on constraints:
    1. PowerShell 7 (pwsh). The syntax is compatible.
    2. Single line command.
    3. Inside ```powershell block.
    4. Turkish prompt, but code is English standard.

    One small detail: `logs` folder structure includes `old`. `-Recurse` handles this.
    Files: `app1.log`, `app2.log`, `app0.log`.
    
    Command construction:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```

    Wait, is there a shorter way?
    `Select-String` can be used with `-SimpleMatch` but that matches the whole line.
    What about:
    ```powershell
    (Get-ChildItem logs -Recurse -Filter *.log).FullName | Select-String 'ERROR' | Measure-Object -Line
    ```
    Wait, `Measure-Object -Line` counts lines in the input stream. The input stream is objects from `Select-String`. Each object represents a match. If I have 1 line with "ERROR ERROR", `Select-String` produces 2 objects. `Measure-Object -Line` treats each object as a line? No, it counts the number of lines in the *text* passed to it if input is text. But here input is objects.
    Actually, `Measure-Object -Line` counts the number of lines in the input stream's string representation. Since `Select-String` outputs objects with `.Line`, PowerShell might display them as lines? No.
    
    Safest bet for "lines containing pattern":
    Read content line by line -> Filter -> Count.
    
    Let's verify if `Get-Content` is efficient enough. Yes, standard task.
    
    One more thing: The prompt asks to write the command in a single ```powershell block.
    And "Sadece komutu tek bir ```powershell bloğu içinde ver." (Give only the command inside a single powershell block).

    Wait, I need to make sure I don't include explanations outside the code block if possible? The prompt says "cevabını tam olarak istenen biçimde ver" (give your answer in exactly the requested format) and "Sadece komutu tek bir ```powershell bloğu içinde ver." (Give only the command inside a single powershell block).
    However, usually I should provide the thought process or context? No, "Görevi dikkatle çöz ve cevabını tam olarak istenen biçimde ver" implies strict adherence. But as an AI assistant, I usually wrap the code in markdown. The instruction says "Sadece komutu tek bir ```powershell bloğu içinde ver." which means *only* the command inside the block, no extra text outside? Or just that the command must be inside the block?
    Usually, it's safer to provide a brief intro if allowed, but strict instructions say "Give only the command...". I will interpret this as: The output should primarily contain the code block with the command. I will avoid conversational filler before/after to respect "Sadece komutu... ver" (Only give the command...).
    Wait, looking at the system instruction: "Sen deneyimli bir yazılım geliştiricisin."
    User instruction: "Sadece komutu tek bir ```powershell bloğu içinde ver."
    This implies I should not add explanations outside the block.

    Let's finalize the command string.
    `(Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count`
    
    Wait, `Measure-Object` outputs an object with a property `Count`. `Select-Object -ExpandProperty Count` extracts it.
    Is there any case where this fails? If no files found or no errors found, it returns 0. Correct.
    
    One optimization: `(Get-ChildItem logs -Recurse -Filter *.log).FullName` creates an array of strings. `Get-Content` reads them.
    Can we use `Select-String` with `-SimpleMatch`? No.
    Can we use `Test-Path`? No.
    
    Wait, I can simplify `(Get-ChildItem logs -Recurse -Filter *.log).FullName | Get-Content`.
    Actually, `Get-Content` accepts multiple paths directly if they are an array of strings (paths).
    So:
    ```powershell
    Get-Content (Get-ChildItem logs -Recurse -Filter *.log) | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```
    This is cleaner. `Get-Content` takes the FileInfo objects from `Get-ChildItem`. It reads their content.
    
    Wait, does `Get-Content` accept FileInfo objects directly? Yes, it follows the path property.
    So:
    `Get-Content (Get-ChildItem logs -Recurse -Filter *.log) | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count`
    
    Wait, one detail: `Measure-Object` without arguments counts objects. If I pipe lines to it, it counts the number of lines (objects). This is exactly what we want.
    So `... | Measure-Object` outputs a table with "Count". To get just the number, `Select-Object -ExpandProperty Count`.
    
    Wait, does `Measure-Object` output headers? Yes, by default it might show "Count : 5".
    Using `Select-Object -ExpandProperty Count` ensures only the value is printed.
    
    Final check:
    Command: `Get-Content (Get-ChildItem logs -Recurse -Filter *.log) | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count`
    
    Wait, I should ensure the path is correct. The prompt says "Bulunduğum klasörün yapısı şöyle" (The structure of the folder I am in is as follows). So `logs` is relative to current directory. Correct.

    One more check: `Select-Object -ExpandProperty Count`.
    If no matches, it outputs 0.
    
    Is there any way to make it even shorter?
    `(Get-ChildItem logs -Recurse -Filter *.log).FullName | Select-String 'ERROR' | Measure-Object -Line` -> This counts lines in the output of Select-String. Since Select-String outputs one object per match, this might count occurrences if multiple matches on one line.
    The prompt says "satırların toplam sayısı" (total number of lines). If a line has 2 errors, it is still 1 line. So `Select-String` counting objects is wrong for strict interpretation.
    My proposed solution using `Get-Content | Where-Object` counts lines correctly because each line from `Get-Content` is one object in the pipeline. `Where-Object` filters them. `Measure-Object` counts the remaining objects (lines). This is correct.

    Final Command:
    ```powershell
    Get-Content (Get-ChildItem logs -Recurse -Filter *.log) | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
    ```
    
    Wait, I can remove the outer parentheses if not needed. `(Get-ChildItem ...)` is an array. `Get-Content` takes it as arguments.
    Actually, `Get-Content (Get-ChildItem logs -Recurse -Filter *.log)` works because `Get-ChildItem` returns objects that have a path property which `Get-Content` uses.
    
    Wait, one nuance: `Measure-Object` outputs an object with properties Count, Average, etc. If I pipe to `Select-Object`, it extracts the count.
    Is there any risk of `Measure-Object` outputting headers? Yes, by default it might format as a table. But `Select-Object -ExpandProperty` usually just prints the value.
    
    Wait, does `Measure-Object` return an object that can be piped to `Select-Object`? Yes.
    
    Okay, ready to write.

    Wait, I need to check if there are any specific PowerShell 7 nuances. No, this is standard PS5/PS6/PS7 syntax.
    
    One detail: "Sadece komutu tek bir ```powershell bloğu içinde ver." (Give only the command inside a single powershell block).
    I will output *only* the code block to be safe and compliant with strict instructions.

    Wait, looking at the instruction again: "Görevi dikkatle çöz ve cevabını tam olarak istenen biçimde ver." (Solve carefully and give your answer in exactly the requested format).
    Then: "Sadece komutu tek bir ```powershell bloğu içinde ver." (Give only the command inside a single powershell block).
    This means no markdown text outside the code block.

    Wait, I should check if `Get-Content` handles binary files? The prompt mentions `big.bin`. But we are filtering `.log` files. So it's fine.
    
    Final Command:
    `Get-ChildItem logs -Recurse -Filter *.log | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count`
    (I moved `Get-ChildItem` before `Get-Content` to be explicit about the stream).
    Actually, `(Get-ChildItem logs -Recurse -Filter *.log) | Get-Content` is cleaner.
    
    Let's write it down.

    Wait, one more thing: The prompt asks for "sadece sayı" (only number). `Select-Object -ExpandProperty Count` outputs the number.
    However, if I use `Measure-Object`, it might output a table header in some shells? In pwsh, `Measure-Object` without `-Line` counts objects. The result is an object with properties. Piping to `Select-Object -ExpandProperty Count` prints just the value (e.g., 5).
    
    Okay, I'm confident.

    Wait, one detail in Turkish: "Bulunduğum klasörde yapan PowerShell komutunu yaz".
    So relative path `logs`.
    
    Final check on command syntax:
    `Get-ChildItem logs -Recurse -Filter *.log` -> Returns FileInfo objects.
    `| Get-Content` -> Reads content of those files line by line.
    `| Where-Object { $_ -match 'ERROR' }` -> Filters lines containing ERROR (case sensitive? Prompt says 'ERROR'. Usually case sensitive in PowerShell unless `-CaseSensitive` is specified or regex handles it. Default match is case-sensitive for strings, but `-match` uses Regex which is case-insensitive by default? No, `-match` is case-sensitive by default in PowerShell 7? Actually, standard .NET Regex is case-sensitive unless options are set. Wait, `$_ -match 'ERROR'` is case sensitive. If the log has 'error', it won't match. The prompt says 'ERROR'. I should assume exact string or case-insensitive? Usually logs have uppercase ERROR. But to be safe, maybe `-CaseSensitive:$true` (default) is fine. Or use `$_ -match 'ERROR'`.
    Wait, standard PowerShell `-match` operator uses Regex. By default it is case-sensitive? No, actually in PowerShell 5/6/7, `-match` is case-insensitive by default? Let's check documentation mentally.
    Actually, `$str -match 'pattern'` is case sensitive unless you use `-CaseSensitive:$false`. Wait, no. The Regex engine defaults to case-sensitive for the pattern string itself unless options are specified. But wait...
    Common knowledge: PowerShell `-match` is case-insensitive by default? No, it depends on the regex flags. Default is usually case-sensitive in .NET Regex unless `(?i)` is used or specific options passed. However, many sources say PowerShell `-match` is case sensitive.
    Wait, let's verify. `$a = "error"; $a -match 'ERROR'` -> False. `$a -match 'error'` -> True. So it IS case-sensitive by default in standard PowerShell? Actually, I recall `-match` uses .NET Regex which defaults to case-sensitive.
    However, often log files might have mixed case. But the prompt specifies `'ERROR'`. I will use exact match as requested. If I want to be safe for 'error', 'Error', etc., I should use `(?i)ERROR`. But the prompt says "'ERROR' geçen satırlar" (lines containing 'ERROR'). Usually implies literal string.
    Given "PowerShell 7", `-match` is case sensitive by default? Actually, documentation says: "The -match operator uses regular expressions...". .NET Regex defaults to case-sensitive. So `$_ -match 'ERROR'` matches only uppercase ERROR. This fits the prompt exactly.

    Okay, final command structure confirmed.


## Cevap

```powershell
Get-ChildItem logs -Recurse -Filter *.log | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
```

## Notlandırılan kod/komut

```
Get-ChildItem logs -Recurse -Filter *.log | Get-Content | Where-Object { $_ -match 'ERROR' } | Measure-Object | Select-Object -ExpandProperty Count
```
