import os

def find_hidden_files(directory):
    """ Recursively finds all hidden files in the given directory and returns their paths. """
    hidden_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('.'):
                hidden_files.append(os.path.join(root, file))
        for dir_name in dirs:
            if dir_name.startswith('.'):
                hidden_files.append(os.path.join(root, dir_name))
    return hidden_files

def write_to_file(file_paths, filename="hidden.txt"):
    """ Writes the list of file paths to a specified file. """
    with open(filename, 'w') as f:
        for path in file_paths:
            f.write(f"{path}\n")

if __name__ == "__main__":
    root_directory = "/"  # Change this to another path if needed
    hidden_files = find_hidden_files(root_directory)

    write_to_file(hidden_files)

    print(f"Found {len(hidden_files)} hidden files. Paths have been written to hidden.txt.")

    # Assuming vt-scan is the command for VirusTotal scan, adjust accordingly if different
    os.system(f"/usr/local/bin/vt scan file --verbose --wait $(cat hidden.txt)")
