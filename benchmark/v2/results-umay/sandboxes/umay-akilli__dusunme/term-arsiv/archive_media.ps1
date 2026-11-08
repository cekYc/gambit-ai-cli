$sourceDir = 'gelen'
$archiveDir = 'arsiv'

if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Path $archiveDir | Out-Null }
$noDateDir = Join-Path $archiveDir 'tarihsiz'
if (-not (Test-Path $noDateDir)) { New-Item -ItemType Directory -Path $noDateDir | Out-Null }

$files = Get-ChildItem -Path $sourceDir -Recurse -File

foreach ($file in $files) {
    $ext = $file.Extension.ToLower()
    $isMedia = $ext -in @('.jpg', '.jpeg', '.png', '.mp4', '.mov')
    
    if (-not $isMedia) {
        Write-Host "Skipped (not media): $($file.FullName)"
        continue
    }
    
    $name = $file.Name
    $date = $null
    
    if ($name -match '(20\d{6})') {
        $match = $matches[1]
        $year = $match.Substring(0,4)
        $month = $match.Substring(4,2)
        $day = $match.Substring(6,2)
        if ([int]$month -ge 1 -and [int]$month -le 12 -and [int]$day -ge 1 -and [int]$day -le 31) {
            $date = "$year/$month"
        }
    }
    elseif ($name -match '(20\d{2}-\d{2}-\d{2})') {
        $match = $matches[1]
        $parts = $match.Split('-')
        $year = $parts[0]
        $month = $parts[1]
        $day = $parts[2]
        if ([int]$month -ge 1 -and [int]$month -le 12 -and [int]$day -ge 1 -and [int]$day -le 31) {
            $date = "$year/$month"
        }
    }
    
    if ($date) {
        $targetDir = Join-Path $archiveDir $date
        if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }
        $targetPath = Join-Path $targetDir $file.Name
        Move-Item -Path $file.FullName -Destination $targetPath -Force
        Write-Host "Moved: $($file.FullName) -> $targetPath"
    } else {
        $targetDir = Join-Path $archiveDir 'tarihsiz'
        $targetPath = Join-Path $targetDir $file.Name
        Move-Item -Path $file.FullName -Destination $targetPath -Force
        Write-Host "Moved (no date): $($file.FullName) -> $targetPath"
    }
}

Write-Host 'Done.'