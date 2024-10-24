import os
import json
import uuid
import hashlib
import platform
from cryptography.fernet import Fernet

# List of files and directories to skip (if needed)
skip_files = [
    'os.py',
    'test.py',
    'encryption_test.py',
    'register_device.py',
    'key.txt',
    'decryption_test.py',
    'pending_registration.json'
]

skip_directories = ['Server', '__pycache__']

def create_syshealthcheck_folder():
    """Create the syshealthcheck folder in the root directory."""
    platform_system = platform.system()
    if platform_system == "Windows":
        folder_path = "C:\\syshealthcheck"
    elif platform_system in ["Darwin", "Linux"]:  # Darwin is macOS
        folder_path = "/syshealthcheck"
    else:
        raise ValueError("Unsupported platform")

    # Create folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def get_files_to_decrypt():
    """Read file paths to decrypt from encrypted_files.txt in the syshealthcheck folder."""
    try:
        syshealth_folder = create_syshealthcheck_folder()
        encrypted_file_path = os.path.join(syshealth_folder, 'encrypted_files.txt')
        
        with open(encrypted_file_path, 'r') as f:
            files = [line.strip() for line in f.readlines()]
            # Filter out any skipped files or directories, if needed
            files = [
                f for f in files 
                if os.path.basename(f) not in skip_files 
                and not any(d in f for d in skip_directories)
            ]
            print(f"Files to decrypt: {files}")  # Debugging print
            return files
    except FileNotFoundError:
        print(f"Error: '{encrypted_file_path}' not found.")
        return []

def log_decrypted_file(file_path):
    """Log decrypted file paths to decrypted_files.txt in syshealthcheck folder."""
    try:
        # Create syshealthcheck folder if it doesn't exist
        syshealth_folder = create_syshealthcheck_folder()
        log_file_path = os.path.join(syshealth_folder, 'decrypted_files.txt')

        # Debugging info to check if the function is called
        print(f"Attempting to log decrypted file: {file_path}")
        
        # Check if the file exists or needs to be created
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"{file_path}\n")
        
        print(f"Successfully logged decrypted file: {file_path}")
    
    except Exception as e:
        print(f"Error logging decrypted file '{file_path}': {e}")

def decrypt_file(file_path, key):
    """Decrypt a single file using Fernet."""
    f = Fernet(key)
    print(f'Decryption key: {key}')
    
    # Read the encrypted file content
    try:
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
    except PermissionError:
        print(f"Permission denied to access: '{file_path}'")
        return  # Skip this file if there's a permission error

    # Attempt to decrypt the content
    try:
        decrypted_data = f.decrypt(encrypted_data)
    except Exception as e:
        print(f"Failed to decrypt {file_path}: {str(e)}")
        return  # Skip this file on decryption failure

    # Write the decrypted data back to the file
    try:
        with open(file_path, "wb") as file:
            file.write(decrypted_data)
        print(f"Decrypted: {file_path}")
        
        # Ensure log is written only after successful decryption
        log_decrypted_file(file_path)
        
    except PermissionError:
        print(f"Permission denied when writing to: '{file_path}'")

def decrypt_files(key):
    """Decrypt files using the provided key."""
    files_to_decrypt = get_files_to_decrypt()
    if not files_to_decrypt:
        print("No files to decrypt.")
        return

    for file_path in files_to_decrypt:
        decrypt_file(file_path, key)

def compare_encrypted_and_decrypted_files():
    """Compare encrypted_files.txt and decrypted_files.txt."""
    print("Comparing encrypted and decrypted files...")  # Debugging print
    
    syshealth_folder = create_syshealthcheck_folder()
    decrypted_file_path = os.path.join(syshealth_folder, 'decrypted_files.txt')
    encrypted_file_path = os.path.join(syshealth_folder, 'encrypted_files.txt')

    if not os.path.exists(encrypted_file_path):
        print(f"'{encrypted_file_path}' does not exist.")
        return
    if not os.path.exists(decrypted_file_path):
        print(f"'{decrypted_file_path}' does not exist.")
        return

    with open(encrypted_file_path, 'r') as encrypted_file:
        encrypted_files = {line.strip() for line in encrypted_file.readlines()}

    with open(decrypted_file_path, 'r') as decrypted_file:
        decrypted_files = {line.strip() for line in decrypted_file.readlines()}

    pending_decryption = encrypted_files - decrypted_files

    if pending_decryption:
        print("Files pending decryption:")
        for file in pending_decryption:
            print(file)
    else:
        print("All encrypted files have been decrypted.")

def get_mac_address():
    """Get the MAC address of the first network interface."""
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
        return mac
    except Exception as e:
        print(f"Error getting MAC address: {e}")
        return "00:00:00:00:00:00"  # Default MAC if an error occurs

def generate_device_id():
    """Generate a unique device ID based on system information."""
    # Get the MAC address
    mac_address = get_mac_address()

    # Get additional system information
    system_info = f"{platform.node()}-{platform.system()}-{platform.release()}"

    # Create a unique string
    unique_string = f"{mac_address}-{system_info}"

    # Generate a stable ID using SHA-256 hash
    device_id = hashlib.sha256(unique_string.encode()).hexdigest()

    return device_id

def run_decryption(key):
    """Main function to run the decryption using a given key."""
    print("Decryption process initiated.")
    
    # Decrypt files if a valid key is passed
    decrypt_files(key)
    
    # Compare files after decryption
    compare_encrypted_and_decrypted_files()

# Now this file can be used as a module
if __name__ == "__main__":
    print("This file is intended to be used as a module. Pass the decryption key to `run_decryption()`.")
