import subprocess
import sys
import os

class AdminCommandRunner:
    """
    A class to detect the operating system and run commands with administrator privileges.
    """

    def __init__(self):
        self.platform = self.detect_platform()

    def detect_platform(self):
        """
        Detect the current operating system platform.
        """
        if os.name == 'nt':
            return 'Windows'
        elif sys.platform == 'darwin':
            return 'macOS'
        elif sys.platform.startswith('linux'):
            return 'Linux'
        else:
            return 'Unsupported'

    def run_command(self, command):
        """
        Run the specified command with administrator privileges based on the platform.
        """
        try:
            print(f"Running command on {self.platform}: {command}")

            if self.platform == 'Windows':
                self.run_as_admin_windows(command)
            elif self.platform in ['macOS', 'Linux']:
                self.run_with_sudo(command)
            else:
                print(f"Unsupported platform: {self.platform}")

        except subprocess.CalledProcessError as e:
            print(f"Error: {str(e)}")
        except Exception as ex:
            print(f"An unexpected error occurred: {str(ex)}")

    def run_as_admin_windows(self, command):
        """
        Run the command with admin privileges on Windows using PowerShell.
        """
        subprocess.run(
            ["powershell", "-Command", f"Start-Process powershell -ArgumentList '{command}' -Verb RunAs"],
            check=True
        )

    def run_with_sudo(self, command):
        """
        Run the command with sudo on macOS or Linux.
        """
        subprocess.run(['sudo'] + command.split(), check=True)
