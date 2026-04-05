#!/bin/bash

# Define the destination directory in the user's home folder
SNAPSHOT_DIR="$HOME/snapshot"

# Check if the snapshot directory exists, if not create it
mkdir -p "$SNAPSHOT_DIR"

# Loop through each subdirectory under /proc
for proc_dir in /proc/*; do
# Get the base name of the current subdirectory (e.g., get the PID)
    pid=$(basename "$proc_dir")

    # Check if it is a directory and exists, then proceed to copy exe file
    if [[ -d "$proc_dir" && -e "$proc_dir/exe" ]]; then
        # Copy the exe file from /proc/$pid/exe to $SNAPSHOT_DIR with PID in filename
        cp "$proc_dir/exe" "$SNAPSHOT_DIR/${pid}_$(basename $(readlink "$proc_dir/exe"))"
        echo "Copied /proc/$pid/exe to $SNAPSHOT_DIR/${pid}_$(basename $(readlink "$proc_dir/exe"))"

        # Upload the file using vt scan
        FILE_TO_SCAN="$SNAPSHOT_DIR/${pid}_$(basename $(readlink "$proc_dir/exe"))"
        /usr/bin/vt scan file --verbose --wait "$FILE_TO_SCAN"
    fi
done

echo "Snapshot complete. All executable files have been copied to $SNAPSHOT_DIR with PID in filename."
