import os
import hashlib
import shutil

def get_file_hash(filepath, block_size=65536):
    """Compute the SHA-1 hash of a file."""
    sha1 = hashlib.sha1()
    with open(filepath, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b""):
            sha1.update(block)
    return sha1.hexdigest()

def deduplicate_files(directory):
    """Deduplicate files in the specified directory."""
    file_hashes = {}
    duplicates = []

    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            file_size = os.path.getsize(filepath)

            if file_size == 0:
                # Skip zero-sized files as they are likely placeholders or empty copies
                continue

            file_hash = get_file_hash(filepath)

            if file_hash in file_hashes:
                duplicates.append((filepath, file_hashes[file_hash]))
            else:
                file_hashes[file_hash] = filepath

    # Remove duplicates by keeping the first occurrence and deleting the rest
    for duplicate_path, original_path in duplicates:
        try:
            os.remove(duplicate_path)
            print(f"Deleted duplicate: {duplicate_path}")
        except Exception as e:
            print(f"Error deleting {duplicate_path}: {e}")

    return len(duplicates)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deduplicate files in a directory.")
    parser.add_argument("directory", type=str, help="The directory to deduplicate.")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"The provided path '{args.directory}' is not a directory.")
    else:
        deleted_count = deduplicate_files(args.directory)
        print(f"Deleted {deleted_count} duplicate files.")
