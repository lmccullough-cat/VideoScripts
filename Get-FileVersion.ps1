#!/usr/bin/env pwsh
# Get-FileVersion.ps1
# Displays file version information for the specified file
# This is a replacement for the Windows SDK filever.exe utility

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$FilePath
)

# Check if file exists
if (-not (Test-Path $FilePath)) {
    Write-Error "File not found: $FilePath"
    exit 1
}

# Get the full path
$FullPath = (Resolve-Path $FilePath).Path

try {
    # Get file version information
    $FileVersionInfo = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($FullPath)

    # Display file information in a format similar to filever.exe
    Write-Host ""
    Write-Host "--a-- W32i   " -NoNewline
    Write-Host "APP" -ForegroundColor Cyan -NoNewline
    Write-Host "  $FullPath"

    # File Version
    if ($FileVersionInfo.FileVersion) {
        Write-Host "  FileVersion:     " -NoNewline
        Write-Host $FileVersionInfo.FileVersion -ForegroundColor Yellow
    }

    # Product Version
    if ($FileVersionInfo.ProductVersion) {
        Write-Host "  ProductVersion:  " -NoNewline
        Write-Host $FileVersionInfo.ProductVersion -ForegroundColor Yellow
    }

    # File Description
    if ($FileVersionInfo.FileDescription) {
        Write-Host "  Description:     $($FileVersionInfo.FileDescription)"
    }

    # Company Name
    if ($FileVersionInfo.CompanyName) {
        Write-Host "  Company:         $($FileVersionInfo.CompanyName)"
    }

    # Product Name
    if ($FileVersionInfo.ProductName) {
        Write-Host "  Product:         $($FileVersionInfo.ProductName)"
    }

    # Copyright
    if ($FileVersionInfo.LegalCopyright) {
        Write-Host "  Copyright:       $($FileVersionInfo.LegalCopyright)"
    }

    # Original Filename
    if ($FileVersionInfo.OriginalFilename) {
        Write-Host "  OriginalName:    $($FileVersionInfo.OriginalFilename)"
    }

    # Internal Name
    if ($FileVersionInfo.InternalName) {
        Write-Host "  InternalName:    $($FileVersionInfo.InternalName)"
    }

    # Language
    if ($FileVersionInfo.Language) {
        Write-Host "  Language:        $($FileVersionInfo.Language)"
    }

    Write-Host ""

} catch {
    Write-Error "Error reading file version information: $_"
    exit 1
}
