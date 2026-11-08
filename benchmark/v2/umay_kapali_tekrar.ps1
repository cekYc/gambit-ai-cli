# Düşünme kapalı koşuları yeniden yapar; bu kez istekte enable_thinking: false açıkça gönderilir.
# Önceki koşular "düşünme alanı gönderilmedi" (varsayilan) etiketiyle raporda kalır.
# Anahtar bir kez gizli sorulur, yalnızca bu PowerShell oturumunda tutulur ve sonunda silinir.
# Yarıda kalırsa aynı komutla yeniden başlat: biten görevler atlanır.
Set-Location $PSScriptRoot
$setHere = -not $env:UMAY_API_KEY
if ($setHere) {
    $secure = Read-Host 'Umay API anahtarı (gizli)' -AsSecureString
    $env:UMAY_API_KEY = [System.Net.NetworkCredential]::new('', $secure).Password
}
try {
    python umay_kos.py --model umay-hizli --no-thinking
    python umay_kos.py --model umay-akilli --no-thinking
    python umay_kos.py --report
}
finally {
    if ($setHere) { Remove-Item Env:UMAY_API_KEY -ErrorAction SilentlyContinue }
}
