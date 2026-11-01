# Gambit Bench v2'yi gözetimli çalıştırır: run.py beklenmedik şekilde çökerse 30 sn sonra kaldığı yerden yeniden
# başlatır (en fazla 6 kez). Tüm plan bitince results\BITTI.txt yazılır.
#   pwsh -File benchmark\v2\calistir.ps1 [run.py argümanları]
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$results = Join-Path $here "results"
New-Item -ItemType Directory -Force $results | Out-Null
Remove-Item (Join-Path $results "BITTI.txt") -ErrorAction SilentlyContinue
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8  # günlükte Türkçe karakterler bozulmasın
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$log = Join-Path $results "calisma.log"
for ($i = 1; $i -le 6; $i++) {
    "`n##### çalıştırma $i · $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File -Append -Encoding utf8 $log
    & python -u (Join-Path $here "run.py") @args *>> $log
    if (Test-Path (Join-Path $results "BITTI.txt")) { break }
    "##### run.py beklenmedik şekilde durdu (çıkış kodu $LASTEXITCODE); 30 sn sonra yeniden başlatılıyor" | Out-File -Append -Encoding utf8 $log
    Start-Sleep -Seconds 30
}
