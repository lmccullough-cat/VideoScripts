# Script to check MP4 files for backwards PTS values using ffmpeg
# Usage: .\check_pts.ps1 <input_file.mp4>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile
)

# Check if file exists
if (-not (Test-Path $InputFile)) {
    Write-Host "Error: File '$InputFile' not found!" -ForegroundColor Red
    exit 1
}

Write-Host "Checking '$InputFile' for PTS issues..." -ForegroundColor Cyan
Write-Host ""

# Run ffmpeg to check for PTS issues
# -v warning: Show warnings and errors
# -i: Input file
# -f null: Discard output (just analyze)
# -: Output to null device
$output = & ffmpeg -v warning -i "$InputFile" -f null - 2>&1 | Out-String

# Filter for PTS/DTS related issues
$ptsIssues = $output -split "`n" | Where-Object { 
    $_ -match "pts|DTS|Non-monotonous|Invalid|backwards" 
}

if ($ptsIssues) {
    Write-Host "WARNING: Potential PTS/DTS issues detected:" -ForegroundColor Yellow
    Write-Host ""
    $ptsIssues | ForEach-Object { 
        Write-Host $_ -ForegroundColor Red
    }
} else {
    Write-Host "No PTS/DTS warnings found. File appears to be clean." -ForegroundColor Green
}

Write-Host ""
Write-Host "Analysis complete." -ForegroundColor Cyan
