# term-uzanti · puan 1.00

**Not:** tamam

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

Görev: data klasöründeki tüm .txt dosyalarının uzantısını .md olarak değiştir (içerikleri aynı kalsın).

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Düşünme

*   OS: Windows, Shell: PowerShell 7 (`pwsh`).
    *   Directory structure provided (though the task is specific to `data` folder).
    *   Goal: Rename all `.txt` files in the `data` directory to `.md` extension.
    *   Constraint 1: Keep content identical.
    *   Constraint 2: Single line command (use `;` if needed).
    *   Constraint 3: Output format must be *only* a single ```powershell block containing the command.

    *   Target directory: `data`.
    *   File pattern: `*.txt`.
    *   Action: Rename extension from `.txt` to `.md`.

    *   Step 1: Get files in `data` folder matching `*.txt`.
        `Get-ChildItem -Path data -Filter *.txt`
    *   Step 2: Pipe them to `Rename-Item`.
    *   Step 3: Use a script block or `-NewName` parameter with replacement.

    *Drafting the command:*
    `Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.FullName -replace '\.txt$', '.md' }`

    *Alternative (simpler for single extension change):*
    `Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }`

    *Let's check the `data` folder structure:*
    `data/notes.txt`, `data/todo.txt`.
    The command should target files *inside* `data`.

    *Refining the command for robustness:*
    `Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.Name -replace '\.txt$', '.md' }`

    Wait, if I use `-Path data`, `$_.Name` is just the filename (e.g., `notes.txt`). Replacing `.txt` with `.md` works perfectly.

    *   Single line? Yes.
    *   Only one ```powershell block? Yes.
    *   Correct logic? Yes.

    Command: `Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.Name -replace '\.txt$', '.md' }`

    Let's double check if there are any edge cases. If a file is named `something.txt.txt`, the regex `\.txt$` ensures only the last one is replaced. This is safer than just replacing `.txt`.

    Actually, even simpler:
    `Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }`
    This is very clean and standard in PowerShell.

    Let's test the logic mentally:
    File: `data/notes.txt`
    `$_.BaseName` -> `notes`
    `$_.BaseName + ".md"` -> `notes.md`
    Resulting command: `Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }`

    Wait, the user asked for "data klasöründeki tüm .txt dosyalarının uzantısını .md olarak değiştir".
    The files are in `data/`.

    Final command choice:
    ```powershell
    Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }
    ```

    *Self-Correction:* The user asked for the command to be run in the *current directory* (bulunduğum klasörde). So `data/*.txt` is correct.

    One more check: Does `Rename-Item` need `-Path` or just the name? When piping from `Get-ChildItem`, it receives objects. Using `$_.BaseName + ".md"` works well with `Rename-Item`.

    Let's try to make it as concise as possible for a "pro developer" feel:
    `gci data -Filter *.txt | Rename-Item -NewName { $_.BaseName + '.md' }` (using aliases is common, but full names are better practice). I will stick to standard cmdlets for clarity and reliability.

    Final check of the prompt requirements: "Sadece komutu tek bir ```powershell bloğu içinde ver." (Only give the command in a single powershell block).

    ```powershell
    Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }
    ```

## Cevap

```powershell
Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }
```

## Notlandırılan kod/komut

```
Get-ChildItem -Path data -Filter *.txt | Rename-Item -NewName { $_.BaseName + ".md" }
```
