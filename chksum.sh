#!/bin/bash

# Check if the user has sufficient privileges (root)
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi

# Clear or create the output file
> system.txt

# Function to recursively find files and compute SHA-256 checksums
compute_sha256sum() {
    for file in "$1"/*; do
        if [ -d "$file" ]; then
            # If it's a directory, recurse into it
            compute_sha256sum "$file"
        elif [ -f "$file" ]; then
            # If it's a file, compute the SHA-256 checksum and append to system.txt
            sha256sum "$file" >> system.txt 2>/dev/null
        fi
done
}

# Start from the root directory
compute_sha256sum "/"

echo "SHA-256 checksums have been computed and saved to system.txt"
