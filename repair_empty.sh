#!/bin/bash

LOG_FILE="/root/empty_files_usr.log"
REINSTALL_LIST="/tmp/packages_to_reinstall.txt"

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: $LOG_FILE not found."
    exit 1
fi

echo "Identifying packages associated with empty files..."

# 1. Map files to packages
# 'pacman -Qqo' returns only the package name for a given file
cat "$LOG_FILE" | xargs -r sudo pacman -Qqo 2>/dev/null | sort -u > "$REINSTALL_LIST"

# 2. Check if we found any packages
if [ ! -s "$REINSTALL_LIST" ]; then
    echo "No packages found owning these files. They may be untracked or orphaned."
    exit 0
fi

echo "------------------------------------------"
echo "The following packages need reinstallation:"
cat "$REINSTALL_LIST"
echo "------------------------------------------"

# 3. Reinstall the packages
read -p "Proceed with reinstallation? [y/N] " confirm
if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
    # --noconfirm is omitted so you can see the transaction
    sudo pacman -S $(cat "$REINSTALL_LIST") --overwrite "*"
else
    echo "Operation cancelled."
fi

# Clean up
rm "$REINSTALL_LIST"
