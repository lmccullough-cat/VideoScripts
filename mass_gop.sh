#!/bin/bash

# mass_gop.sh - Process multiple media files with gop_size_2.sh and ffmpeg_to_excel.py
# Usage: mass_gop.sh <input_dir> <output_dir>
# Example: mass_gop.sh ~/input/ ~/output/

# Check if correct number of arguments provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_dir> <output_dir>"
    echo "Example: $0 ~/input/ ~/output/"
    exit 1
fi

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory does not exist: $INPUT_DIR"
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Using script directory: $SCRIPT_DIR"

# Counter for processed files
PROCESSED=0
FAILED=0

echo "==================================="
echo "Mass GOP Size Analysis"
echo "==================================="
echo "Input directory: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Process each file in the input directory
for INPUT_FILE in "$INPUT_DIR"/*; do
    # Check if file exists and is a regular file
    if [ ! -f "$INPUT_FILE" ]; then
        continue
    fi
    
    # Get the base filename
    BASENAME=$(basename "$INPUT_FILE")
    echo "-----------------------------------"
    echo "Processing: $BASENAME"
    echo "-----------------------------------"
    
    # Change to output directory to run gop_size_2.sh
    cd "$OUTPUT_DIR" || { echo "Error: Cannot access output directory"; exit 1; }
    
    # Run gop_size_2.sh on the input file
    echo "Running gop_size_2.sh..."
    "$SCRIPT_DIR/gop_size_2.sh" "$INPUT_FILE"
    GOP_EXIT_CODE=$?
    
    if [ $GOP_EXIT_CODE -ne 0 ]; then
        echo "Error: gop_size_2.sh failed for $BASENAME"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    # The output file should be named ${BASENAME}.txt in current directory
    TXT_FILE="${BASENAME}.txt"
    
    if [ ! -f "$TXT_FILE" ]; then
        echo "Error: Expected output file $TXT_FILE not found"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    echo "Created: $TXT_FILE"
    
    # Run ffmpeg_to_excel.py on the txt file
    echo "Running ffmpeg_to_excel.py..."
    python3 "$SCRIPT_DIR/ffmpeg_to_excel.py" "$TXT_FILE" -o "${BASENAME}_frames.xlsx"
    EXCEL_EXIT_CODE=$?
    
    if [ $EXCEL_EXIT_CODE -ne 0 ]; then
        echo "Error: ffmpeg_to_excel.py failed for $TXT_FILE"
        FAILED=$((FAILED + 1))
        continue
    fi
    
    echo "Created: ${BASENAME}_frames.xlsx"
    echo "✓ Successfully processed $BASENAME"
    PROCESSED=$((PROCESSED + 1))
    echo ""
done

# Return to original directory
cd - > /dev/null

# Summary
echo "==================================="
echo "Processing Complete"
echo "==================================="
echo "Files processed successfully: $PROCESSED"
if [ $FAILED -gt 0 ]; then
    echo "Files failed: $FAILED"
fi
echo "Output directory: $OUTPUT_DIR"
echo ""

# Exit with error if any files failed
if [ $FAILED -gt 0 ]; then
    exit 1
fi

exit 0
