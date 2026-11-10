$sourceDir = 'gelen'
$destRoot = 'arsiv'

# Create destination directories
$dirs = @(
    'arsiv/2022/11',
    'arsiv/2023/12',
    'arsiv/2024/01',
    'arsiv/2024/03',
    'arsiv/2024/06',
    'arsiv/2025/07',
    'arsiv/tarihsiz'
)
foreach ($d in $dirs) { 
    if (-not (Test-Path $d)) { 
        New-Item -ItemType Directory -Path $d -Force | Out-Null 
    }
}

# Media file extensions
$mediaExts = @('.jpg', '.jpeg', '.png', '.mp4', '.mov')

# Get all files recursively
$files = Get-ChildItem -Path $sourceDir -Recurse -File

foreach ($file in $files) {
    $ext = $file.Extension.ToLower()
    if ($mediaExts -contains $ext) {
        $name = $file.Name
        $date = $null
        
        # Try YYYYMMDD pattern (starts with 20)
        if ($name -match '(20\d{6})') {
            $dateStr = $matches[1]
            $year = $dateStr.Substring(0,4)
            $month = $dateStr.Substring(4,2)
            $date = "$year/$month"
        }
        # Try YYYY-MM-DD pattern
        elseif ($name -match '(\d{4}-\d{2}-\d{2})') {
            $dateStr = $matches[1]
            $year = $dateStr.Substring(0,4)
            $month = $dateStr.Substring(5,2)
            $date = "$year/$month"
        }
        
        $relPath = $file.FullName.Substring($sourceDir.Length + 1)
        
        if ($date) {
            $targetDir = Join-Path $destRoot $date
            $targetFile = Join-Path $targetDir $file.Name
            if (Test-Path $targetFile) {
                # Handle duplicates - add counter
                $base = [IO.Path]::GetFileNameWithoutExtension($file.Name)
                $ext = $file.Extension
                $counter = 1
                while (Test-Path $targetFile) {
                    $targetFile = Join-Path $targetDir "${base}_$counter$ext"
                    $counter++
                }
            }
            Move-Item -Path $file.FullName -Destination $targetFile -Force
            Write-Host "TAŞINDI: $relPath -> arsiv/$date/"
        } else {
            $targetDir = Join-Path $destRoot 'tarihsiz'
            $targetFile = Join-Path $targetDir $file.Name
            if (Test-Path $targetFile) {
                $base = [IO.Path]::GetFileNameWithoutExtension($file.Name)
                $ext = $file.Extension
                $counter = 1
                while (Test-Path $targetFile) {
                    $targetFile = Join-Path $targetDir "${base}_$counter$ext"
                    $counter++
                }
            }
            Move-Item -Path $file.FullName -Destination $targetFile -Force
            Write-Host "TAŞINDI (TARİHSİZ): $relPath -> arsiv/tarihsiz/"
        }
    } else {
        Write-Host "ATLANDI (MEDYA DEĞİL): $($file.FullName.Substring($sourceDir.Length + 1))"
    }
}

Write-Host 'İşlem tamamlandı.'
