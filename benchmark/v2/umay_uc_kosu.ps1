# Umay'ın üç yapılandırmasını sırayla koşturur: Akıllı düşünme kapalı, Hızlı düşünme açık, Hızlı düşünme kapalı.
# Anahtar bir kez gizli sorulur, yalnızca bu PowerShell oturumunda tutulur ve sonunda silinir.
# Yarıda kalırsa aynı komutla yeniden başlat: biten görevler atlanır.
Set-Location $PSScriptRoot
$setHere = -not $env:UMAY_API_KEY
if ($setHere) {
    $secure = Read-Host 'Umay API anahtarı (gizli)' -AsSecureString
    $env:UMAY_API_KEY = [System.Net.NetworkCredential]::new('', $secure).Password
}
try {
    python umay_kos.py --model umay-akilli --no-thinking
    python umay_kos.py --model umay-hizli
    python umay_kos.py --model umay-hizli --no-thinking
    python umay_kos.py --report
}
finally {
    if ($setHere) { Remove-Item Env:UMAY_API_KEY -ErrorAction SilentlyContinue }
}
