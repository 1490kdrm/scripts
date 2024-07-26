#!/bin/bash

# Set your git repo dir
LIB_DIR=/home/mrkd1904/lib/

# Set the directory to start searching from
START_DIR=$LIB_DIR

# Loop through all directories in the START_DIR
for DIR in $(find "$START_DIR" -type d); do
    # Check if the directory is a Git repository
    if [ -d "$DIR/.git" ]; then
     # Go into the Git repository and update it
     cd "$DIR"
     /usr/bin/git pull origin master --verify-signatures --recurse-submodules | /usr/bin/git maintenance run
     cd ..
    fi
done
