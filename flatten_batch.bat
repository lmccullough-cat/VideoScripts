@echo off
setlocal enabledelayedexpansion

REM Get the directory to process (first argument or current directory)
if "%~1"=="" (
    set "TARGET_DIR=%CD%"
) else (
    set "TARGET_DIR=%~1"
)

echo Target directory: !TARGET_DIR!
echo.

REM Find an available results directory name
set "RESULTS_DIR=!TARGET_DIR!\results"
set "COUNTER=0"

:find_results_dir
if exist "!RESULTS_DIR!" (
    set /a COUNTER+=1
    set "RESULTS_DIR=!TARGET_DIR!\results.!COUNTER!"
    goto find_results_dir
)

REM Create the results directory
echo Creating results directory: !RESULTS_DIR!
mkdir "!RESULTS_DIR!"
if errorlevel 1 (
    echo ERROR: Failed to create results directory
    exit /b 1
)
echo.

REM Process each .mp4 and .ts file in the target directory (not subdirectories)
set "FILE_COUNT=0"
for %%F in ("!TARGET_DIR!\*.mp4" "!TARGET_DIR!\*.ts") do (
    REM Check if file exists and is not a directory
    if exist "%%F" (
        if not exist "%%F\*" (
            set /a FILE_COUNT+=1
            echo [!FILE_COUNT!] Processing: %%~nxF
            flatten -x --v "%%F" > "!RESULTS_DIR!\%%~nF.log" 2>&1
            if errorlevel 1 (
                echo     WARNING: flatten returned error code !errorlevel!
            )
        )
    )
)

echo.
echo Done. Processed !FILE_COUNT! file(s)
echo Results stored in: !RESULTS_DIR!
