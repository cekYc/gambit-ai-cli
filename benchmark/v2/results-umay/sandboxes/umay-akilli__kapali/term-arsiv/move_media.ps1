$base = 'C:\\AI\\benchmark\\v2\\results-umay\\sandboxes\\umay-akilli__kapali\\term-arsiv'
$gelen = Join-Path $base 'gelen'
$arsiv = Join-Path $base 'arsiv'

if (-not (Test-Path $arsiv)) { New-Item -ItemType Directory -Path $arsiv | Out-Null }

$mediaExt = @('.jpg', '.jpeg', '.png', '.mp4', '.mov')
$dateRegex = '(20\\d{6})|(\\d{4}-\\d{2}-\\d{2})'

# Önce arsiv/tarihsiz içindeki dosyaları geri taşı (gelen'e)
$tarihsizDir = Join-Path $arsiv 'tarihsiz'
if (Test-Path $tarihsizDir) {
    Get-ChildItem -Path $tarihsizDir -File | ForEach-Object {
        $dest = Join-Path $gelen $_.Name
        Move-Item -Path $_.FullName -Destination $dest -Force
    }
    # alt klasörler varsa (tatil vb.) onları da geri taşı
    Get-ChildItem -Path $gelen -Recurse -Directory | Where-Object { $_.Name -ne 'tatil' } | ForEach-Object { }
}

$moved = @()
Get-ChildItem -Path $gelen -Recurse -File | Where-Object { $mediaExt -contains $_.Extension.ToLower() } | ForEach-Object {
    $src = $_.FullName
    $name = $_.Name
    $dateStr = $null
    if ($name -match $dateRegex) {
        # $matches[0] tam eşleşme, $matches[1] ilk grup, $matches[2] ikinci grup
        if ($matches[1]) { $dateStr = $matches[1] } elseif ($matches[2]) { $dateStr = $matches[2] }
    }
    if ($dateStr) {
        if ($dateStr -match '-') {
            $parts = $dateStr.Split('-')
            $year = $parts[0]
            $month = $parts[1]
        } else {
            $year = $dateStr.Substring(0,4)
            $month = $dateStr.Substring(4,2)
        }
        $destDir = Join-Path $arsiv (Join-Path $year $month)
    } else {
        $destDir = Join-Path $arsiv 'tarihsiz'
    }
    if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
    $dest = Join-Path $destDir $name
    Move-Item -Path $src -Destination $dest -Force
    $moved += @{$src=$dest}
}

Write-Host "Tasinan: $($moved.Count)"
$moved | ForEach-Object { Write-Host "  $($_.Keys) -> $($_.Values)" }
