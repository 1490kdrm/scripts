#!/bin/bash

# Set the directory to start searching from
START_DIR="/"

# Set the output file
OUTPUT_FILE=~/bogey.txt

# Loop through all files and directories in the START_DIR
`find $START_DIR -type f -o -type d -exec /usr/bin/pacman -Qo {} \; | grep -v "is owned by" > $OUTPUT_FILE 2>&1`
