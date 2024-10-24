# gui_app.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Cracking Application")

        # Set the application window icon (logo)
        self.root.iconphoto(False, ImageTk.PhotoImage(file='cnn.png'))

        # Create a label to display the logo
        self.logo_label = tk.Label(root)
        self.logo_label.pack(pady=20)

        # Create a label to display description text
        self.description_label = tk.Label(root, text="", font=("Arial", 14))
        self.description_label.pack(pady=10)

        # Create a progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=20)

        # Button to start the initialization process
        self.start_button = tk.Button(root, text="Start Initialization", command=self.initialize)
        self.start_button.pack(pady=10)

        # Placeholder for logos and descriptions
        self.logo_images = ["cnn.png", "cnn.png"]  # Paths to your logo images
        self.descriptions = ["Initializing component A...", "We are cracking cnn for you, please  hold on as this might take some time."]

    def initialize(self):
        # Hide the Start button after it's clicked
        self.start_button.pack_forget()

        # Simulate progress with logo and description changes
        total_time = 3600 // 2  # Simulate half an hour (in seconds) instead of 1 hour
        progress_goal = 50  # Set the progress bar to move to 50%
        step_duration = total_time // progress_goal  # Time between progress increments

        # Update the first logo and description, then start progress
        self.update_logo_and_description(0)

        for progress_value in range(1, progress_goal + 1):
            self.update_progress(progress_value)
            time.sleep(step_duration / 1000)  # Sleep in smaller increments (milliseconds)
            if progress_value == progress_goal // 2:
                # At halfway (50%), update logo and description
                self.update_logo_and_description(1)

    def update_logo_and_description(self, index):
        # Load and update the logo
        image = Image.open(self.logo_images[index])
        image = image.resize((150, 150), Image.LANCZOS)  # Use LANCZOS for resizing
        logo = ImageTk.PhotoImage(image)
        self.logo_label.config(image=logo)
        self.logo_label.image = logo  # Keep a reference to avoid garbage collection

        # Update the description text
        self.description_label.config(text=self.descriptions[index])

    def update_progress(self, progress_value):
        # Gradually update the progress bar
        self.progress['value'] = progress_value
        self.root.update_idletasks()  # Update the UI
