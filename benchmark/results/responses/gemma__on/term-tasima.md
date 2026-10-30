# term-tasima · puan 1.00

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

Görev: archive adında bir klasör oluştur ve logs klasörünün doğrudan içindeki .log dosyalarını (alt klasördekiler hariç) bu klasöre taşı.

Bu işi bulunduğum klasörde yapan PowerShell komutunu yaz (tek satır; gerekirse komutları ; ile birleştir). Sadece komutu tek bir ```powershell bloğu içinde ver.

## Düşünme

*   OS: Windows, Shell: PowerShell 7 (`pwsh`).
    *   Directory structure provided.
    *   Goal:
        1.  Create a folder named `archive`.
        2.  Move `.log` files located *directly* inside the `logs` folder to the `archive` folder (exclude subdirectories like `logs/old/app0.log`).
    *   Constraint: Single line command, use `;` if necessary, output only a single ```powershell block containing the command.

    *   Create directory: `New-Item -ItemType Directory -Path archive -Force` (using `-Force` is good practice to avoid errors if it already exists).
    *   Find files: `Get-ChildItem -Path logs/*.log`. Note: Using `logs/*.log` or `Get-ChildItem logs -Filter *.log` ensures we only look at the top level of `logs`. If I used `-Recurse`, it would include `old/app0.log`, which is explicitly forbidden by the prompt ("alt klasördekiler hariç").
    *   Move files: `Move-Item -Destination archive`.

    *   `New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive`

    *   Does it create `archive`? Yes.
    *   Does it target `.log` files in `logs/` only? Yes, `logs/*.log` or `Get-ChildItem logs -Filter *.log` (without `-Recurse`) targets the immediate children of `logs`.
    *   Is it a single line? Yes.
    *   Is it inside a ```powershell block? Yes.

    *Refining the command for robustness:*
    `New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs\*.log | Move-Item -Destination archive` (Using backslash or forward slash is fine in PowerShell, but `logs/*.log` is standard).

    Let's check if `Get-ChildItem logs -Filter *.log` is safer.
    If I use `Get-ChildItem logs -File -Filter *.log`, it ensures only files are picked up (though `.log` implies a file usually, but good practice).

    Command: `New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive`

    Wait, if there are no log files in the root of `logs`, `Get-ChildItem` might throw an error. However, for a standard task like this, the direct command is expected.

    Let's try:
    `New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive`

    Wait, if `logs/app1.log` exists, `Get-ChildItem logs/*.log` works perfectly in PowerShell 7.

    *   Create folder: `New-Item -ItemType Directory -Path archive -Force;`
    *   Move files: `Get-ChildItem -Path logs/*.log | Move-Item -Destination archive`

    One detail: If the user runs this and there are no files, it might error. But usually, in these coding challenges, we provide the direct logic.

    Let's double check "logs klasörünün doğrudan içindeki .log dosyalarını (alt klasördekiler hariç)".
    `Get-ChildItem logs -Filter *.log` -> This looks at `logs` directory only. It does *not* recurse unless `-Recurse` is specified. So this is correct.

    Final Command:
    ```powershell
    New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive
    ```

    Actually, `Get-ChildItem -Path logs/*.log` is very clean for PowerShell.

    Let's check if I need to handle the case where `archive` already exists? `-Force` handles it.

    Final verification of requirements:
    - Single line? Yes.
    - Only one ```powershell block? Yes.
    - Task: Create archive, move logs (not subdirs). Yes.

    One small edge case: If there are no files matching `logs/*.log`, `Move-Item` might complain if the pipeline is empty in some versions, but in PS7 it's generally fine or we can pipe to `Where-Object`. But for a "write the command" task, simplicity is key.

    Let's use:
    `New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive`

    Wait, if I use `Get-ChildItem logs -Filter *.log`, it's more "PowerShell idiomatic".

    Let's go with:
    ```powershell
    New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive
    ```

    Actually, `Get-ChildItem -Path logs/*.log` is the most concise way to say "files in logs ending with .log".

    One more check: The prompt says "Sadece komutu tek bir ```powershell bloğu içinde ver." (Give only the command inside a single powershell block). This means no explanation text outside.

    ```powershell
    New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive
    ```

## Cevap

```powershell
New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive
```

## Notlandırılan kod/komut

```
New-Item -ItemType Directory -Path archive -Force; Get-ChildItem -Path logs/*.log | Move-Item -Destination archive
```
