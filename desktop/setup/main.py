import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import requests
import zipfile

from typing import TypeVar

T = TypeVar("T", bound="Config")

class Config:
    _instance: "Config" = None

    def __new__(cls, *args, **kwargs) -> T:
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.MIRRORS = [
            "http://localhost:8000/download/desktop_client.zip",
        ]

class Setup(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.title("KovaaK's - Voltaic Tracker Setup")
        self.geometry("600x350")
        self.resizable(False, False)

        self.config = Config()

        # Setup the initial frames and layout
        self.create_widgets()

    def create_widgets(self):
        """Create the main UI layout."""
        self.welcome_frame = tk.Frame(self)
        self.terms_frame = tk.Frame(self)
        self.install_frame = tk.Frame(self)
        self.progress_frame = tk.Frame(self)
        self.complete_frame = tk.Frame(self)

        self.show_welcome_screen()

    def show_welcome_screen(self):
        """Display the welcome screen."""
        self.clear_frames()

        label = tk.Label(self.welcome_frame, text="Welcome to KovaaK's - Voltaic Tracker Setup", font=("Arial", 16))
        label.pack(pady=20)

        next_button = tk.Button(self.welcome_frame, text="Next", command=self.show_terms_screen)
        next_button.pack(pady=20)

        self.welcome_frame.pack()

    def show_terms_screen(self):
        """Display the terms and conditions screen."""
        self.clear_frames()

        label = tk.Label(self.terms_frame, text="Please accept the Terms of Service and Privacy Policy", font=("Arial", 12))
        label.pack(pady=10)

        self.terms_var = tk.BooleanVar()
        terms_checkbox = tk.Checkbutton(self.terms_frame, text="I accept the Terms of Service and Privacy Policy", variable=self.terms_var)
        terms_checkbox.pack(pady=20)

        next_button = tk.Button(self.terms_frame, text="Next", command=self.check_terms_accepted)
        next_button.pack(pady=20)

        self.terms_frame.pack()

    def check_terms_accepted(self):
        """Check if terms are accepted before proceeding."""
        if not self.terms_var.get():
            messagebox.showwarning("Warning", "You must accept the terms to proceed.")
        else:
            self.show_install_screen()

    def show_install_screen(self):
        """Display the installation path selection screen."""
        self.clear_frames()

        label = tk.Label(self.install_frame, text="Choose the installation directory", font=("Arial", 12))
        label.pack(pady=10)

        self.install_dir_var = tk.StringVar()

        install_entry = tk.Entry(self.install_frame, textvariable=self.install_dir_var, width=50)
        install_entry.pack(pady=5)

        browse_button = tk.Button(self.install_frame, text="Browse", command=self.select_install_dir)
        browse_button.pack(pady=5)

        install_button = tk.Button(self.install_frame, text="Install", command=self.start_installation)
        install_button.pack(pady=20)

        self.install_frame.pack()

    def select_install_dir(self):
        """Open a file dialog for installation path selection."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.install_dir_var.set(dir_path)

    def start_installation(self):
        """Start the download and installation process in a separate thread."""
        install_dir = self.install_dir_var.get()

        if not install_dir:
            messagebox.showwarning("Warning", "Please select an installation directory.")
            return

        self.clear_frames()
        label = tk.Label(self.progress_frame, text="Installing...", font=("Arial", 12))
        label.pack(pady=20)

        self.progress_frame.pack()

        # Start the download in a separate thread to avoid blocking the UI
        threading.Thread(target=self.download_and_install, args=(install_dir,)).start()

    def download_and_install(self, install_dir):
        """Download the app and extract it to the installation directory."""
        mirrors = self.config.MIRRORS
        app_file = os.path.join(install_dir, "app.zip")

        try:
            for mirror in mirrors:
                try:
                    # Attempt to download the file
                    with requests.get(mirror, stream=True) as response:
                        response.raise_for_status()  # Raise error for bad status codes
                        with open(app_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                    break  # If download succeeds, exit the loop
                except requests.RequestException as e:
                    print(f"Download failed from {mirror}. Trying the next mirror. Error: {e}")

            # Extract the zip file
            with zipfile.ZipFile(app_file, 'r') as zip_ref:
                zip_ref.extractall(install_dir)

            os.remove(app_file)  # Remove the zip file after extraction

            self.show_complete_screen(install_dir)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to install the app. Error: {e}")

    def show_complete_screen(self, install_dir):
        """Display the installation completion screen."""
        self.clear_frames()

        label = tk.Label(self.complete_frame, text="Installation Complete!", font=("Arial", 16))
        label.pack(pady=20)

        run_button = tk.Button(self.complete_frame, text="Run app", command=lambda: self.run_app(install_dir))
        run_button.pack(pady=10)

        finish_button = tk.Button(self.complete_frame, text="Finish", command=self.quit)
        finish_button.pack(pady=10)

        self.complete_frame.pack()

    def run_app(self, install_dir):
        """Run the config.exe file."""
        app_path = os.path.join(install_dir, "config.exe")
        if os.path.exists(app_path):
            os.startfile(app_path)
        else:
            messagebox.showerror("Error", f"config.exe not found in {install_dir}")

    def clear_frames(self):
        """Remove all current frames from the window."""
        for widget in self.winfo_children():
            widget.pack_forget()


def main() -> None:
    app = Setup()
    app.mainloop()


if __name__ == "__main__":
    main()