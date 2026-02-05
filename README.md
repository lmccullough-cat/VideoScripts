# Bin Folder Scripts Documentation

This folder contains various utility scripts for video analysis, build automation, and network tools.

## Video Analysis Scripts

### check_pts.bat
Checks MP4 files for backwards PTS (Presentation Time Stamp) values using ffmpeg. Reports any non-monotonous DTS or timing errors in video files.

### check_pts.ps1
PowerShell version of check_pts.bat with color-coded output for better readability.

### gop_size.sh
Analyzes video files using ffprobe to calculate GOP (Group of Pictures) sizes by counting frames between keyframes.

### gop_size_2.sh
Enhanced GOP size analyzer that provides detailed statistics including frame count, keyframe count, average GOP size, and maximum GOP size. Outputs results to a text file based on the input filename.

### mass_gop.sh
Batch processes multiple media files in a directory, running gop_size_2.sh and ffmpeg_to_excel.py on each file to generate both text output and Excel spreadsheets.

### ffmpeg_to_excel.py
Converts FFmpeg frame output to Excel spreadsheets, extracting PTS, DTS, frame types, and other metadata. Automatically adds delta columns with formulas to analyze frame-to-frame changes.

### pts_jump_analyzer.py
Analyzes video files for PTS jump anomalies, identifying frames where timing jumps occur and providing statistical analysis with context around each jump.

### iframe_offset_extract.py
Extracts I-frame byte offsets from MP4 files by parsing the moov atom structure (stss, stco/co64, stsz, stsc tables). Validates offsets against file bounds and mdat box.

### check_faststart.bat
Checks multiple MP4 files in a directory to determine if they have faststart enabled (moov atom at beginning of file). Uses ffmpeg trace output to detect moov location.

### check_faststart_2.bat
Checks a single MP4 file to show the order of mdat and moov atoms, helping determine if the file is optimized for streaming (moov before mdat).

## Build Automation Scripts

### build_mtab.sh
Builds a Qt-based Match Tracker American Football application using qmake and make. Runs the build in a 'build' subdirectory.

### clean_build_mtab.sh
Performs a clean build of the Match Tracker application by removing the existing build directory and rebuilding from scratch.

### flatten_batch.bat 
calls flatten (assumes that flatten in the current dir) on all the mp4 or ts files in a given folder saves the results to .log files in a folder called results 
## Network Tools

### ping_all.bat
Network scanner that pings all IP addresses in the 172.16.101.0/24 subnet (1-254) and saves responding addresses to c:\ipaddresses.txt.

## Old tools

### windiff.exe
diff tool that used to be in visual studio. good for diffing folders

### filevr(.cmd)
commandline wrapper around a powershell script to get the file version of a given file
