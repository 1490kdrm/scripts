#!/bin/bash

# Define the target directory and log file
TARGET="/usr /var /opt /etc"
LOG_FILE="$HOME/empty_files_usr.log"

echo "Searching for empty files in $TARGET..."
echo "Results will be saved to $LOG_FILE"

# Find empty files, count them, and write to log
# -type f: look for regular files only
# -empty: matches files with 0 bytes
sudo find "$TARGET" -type f -empty -print > "$LOG_FILE"

COUNT=$(wc -l < "$LOG_FILE")

echo "------------------------------------------"
echo "Search complete."
echo "Found $COUNT empty files."
echo "------------------------------------------"

# Optional: List the first 10 results for a quick glance
if [ "$COUNT" -gt 0 ]; then
echo "First 20 results:"
head -n 10 "$LOG_FILE"
fi
