$sourceDir = 'gelen'
$archiveDir = 'arsiv'

$mediaExts = @('.jpg', '.jpeg', '.png', '.mp4', '.mov')

if (-not (Test-Path $archiveDir)) { New-Item -ItemType Directory -Path $archiveDir | Out-Null }
if (-not (Test-Path '$archiveDir/tarihsiz')) { New-Item -ItemType Directory -Path '$archiveDir/tarihsiz' | Out-Null }

$files = Get-ChildItem -Path $sourceDir -Recurse -File

foreach ($file in $files) {
    $ext = $file.Extension.ToLower()
    if ($mediaExts -contains $ext) {
        $name = $file.Name
        $date = $null
        
        if ($name -match '(20\d{6})') {
            $match = $matches[1]
            $year = $match.Substring(0,4)
            $month = $match.Substring(4,2)
            $date = "$year/$month"
        }
        elseif ($name -match '(\d{4})-(\d{2})-(\d{2})') {
            $year = $matches[1]
            $month = $matches[2]
            $date = "$year/$month"
        }
        
        if ($date) {
            $targetDir = "$archiveDir/$date"
            if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }
            $targetPath = "$targetDir/$($file.Name)"
            if (Test-Path $targetPath) {
                $base = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                $ext2 = $file.Extension
                $i = 1
                while (Test-Path "$targetDir/${base}_$i$ext2") { $i++ }
                $targetPath = "$targetDir/${base}_$i$ext2"
            }
            Move-Item -Path $file.FullName -Destination $targetPath -Force
            Write-Host "TASINDI: $($file.FullName) -> $targetPath"
        } else {
            $targetDir = "$archiveDir/tarihsiz"
            $targetPath = "$targetDir/$($file.Name)"
            if (Test-Path $targetPath) {
                $base = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
                $ext2 = $file.Extension
                $i = 1
                while (Test-Path "$targetDir/${base}_$i$ext2") { $i++ }
                $targetPath = "$targetDir/${base}_$i$ext2"
            }
            Move-Item -Path $file.FullName -Destination $targetPath -Force
            Write-Host "TASINDI TARIHSIZ: $($file.FullName) -> $targetPath"
        }
    } else {
        Write-Host "ATLANAN: $($file.FullName)"
    }
}

Write-Host 'Islem tamamlandi.'