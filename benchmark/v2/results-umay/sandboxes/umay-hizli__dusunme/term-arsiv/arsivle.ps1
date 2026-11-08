$ErrorActionPreference = "Stop"
$root = Get-Location
$src = Join-Path $root "gelen"
$dst = Join-Path $root "arsiv"
$mediaExts = @(".jpg", ".jpeg", ".png", ".mp4", ".mov")

$files = Get-ChildItem -Path $src -Recurse -File

foreach ($file in $files) {
    $ext = $file.Extension.ToLowerInvariant()
    if ($mediaExts -notcontains $ext) { continue }

    $base = $file.BaseName
    $dateStr = $null

    # once YYYYMMDD (20 ile baslayan 8 rakam), sonra YYYY-MM-DD
    if ($base -match '(20\d{6})') {
        $dateStr = $matches[1]
    } elseif ($base -match '(\d{4}-\d{2}-\d{2})') {
        $dateStr = $matches[1] -replace '-', ''
    }

    if ($dateStr) {
        $year = $dateStr.Substring(0, 4)
        $month = $dateStr.Substring(4, 2)
        $destDir = Join-Path $dst "$year\$month"
    } else {
        $destDir = Join-Path $dst "tarihsiz"
    }

    $null = New-Item -ItemType Directory -Path $destDir -Force
    $destPath = Join-Path $destDir $file.Name

    # Ayni isimde dosya varsa carpismasi onle
    if (Test-Path $destPath) {
        $nameOnly = $file.BaseName
        $extWithDot = $file.Extension
        $i = 1
        do {
            $destPath = Join-Path $destDir "$nameOnly ($i)$extWithDot"
            $i++
        } while (Test-Path $destPath)
    }

    Move-Item -Path $file.FullName -Destination $destPath -Force
    Write-Host ("{0} -> {1}" -f $file.FullName, $destPath)
}

Write-Host "Islem tamamlandi."
