@echo off
REM Script to check MP4 files for backwards PTS values using ffmpeg
REM Usage: check_pts.bat <input_file.mp4>

if "%~1"=="" (
    echo Usage: %~nx0 ^<input_file.mp4^>
    echo.
    echo Checks a video file for backwards PTS ^(Presentation Time Stamp^) values
    exit /b 1
)

set "INPUT_FILE=%~1"

if not exist "%INPUT_FILE%" (
    echo Error: File "%INPUT_FILE%" not found!
    exit /b 1
)

echo Checking "%INPUT_FILE%" for PTS issues...
echo.

REM Run ffmpeg to check for PTS issues
REM -v warning: Show warnings and errors
REM -i: Input file
REM -f null: Discard output (just analyze)
REM -: Output to null device
ffmpeg -v warning -i "%INPUT_FILE%" -f null - 2>&1 | findstr /C:"pts" /C:"DTS" /C:"Non-monotonous" /C:"Invalid"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo WARNING: Potential PTS/DTS issues detected above!
) else (
    echo No PTS/DTS warnings found. File appears to be clean.
)

echo.
echo Analysis complete.
