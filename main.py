import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, sys, json, time
from pathlib import Path
import webbrowser

from typing import Dict, Annotated

import requests


HOME = os.getenv("HOME")

def obtain_paths(
    platform: Annotated[str, "The operating system that the tracker is being ran on."]
    ) -> Annotated[Dict[str, str], "Contains different useful paths as values"]:

    if platform != "win32":
        raise Exception(f"{platform=} not suported")

    paths = {}

    paths["x86"] = os.getenv("PROGRAMFILES(X86)")
    paths["steamapps"] = os.path.join(paths["x86"], "Steam/steamapps")
    paths["kvks"] = os.path.join(paths["steamapps"], "common/FPSAimTrainer")
    paths["stats"] = os.path.join(paths["kvks"], "FPSAimTrainer/stats")

    return paths

class SetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()

        tk.Label(self, text="").pack()

        self.title("Setup Wizard")
        self.geometry("300x350")
        self.resizable(False, False)

        self.username = ""
        self.password = ""

        self.username_label = None
        self.username_entry = None
        self.password_label = None
        self.password_entry = None
        self.button_next = None
        self.signup_button = None

        self.token = self.authenticate()
        stats_path = self.load_stats_directory()
        if stats_path is None:
            stats_path = str(Path(obtain_paths(sys.platform)["stats"]))
            self.stats_path = tk.StringVar(self, stats_path) 
            self.setup_kvks_directory()
        else:
            self.main()


    def load_credentials(self):
        print("Loading credentials")
        credentials_path = os.path.join(HOME, ".kovaaks_tracker/credentials.json")
        if os.path.exists(credentials_path):
            with open(credentials_path) as file:
                return json.load(file)

    def save_credentials(self, credentials):
        print("Saving credentials")
        credentials_path = os.path.join(HOME, ".kovaaks_tracker/credentials.json")
        local_path = os.path.join(HOME, ".kovaaks_tracker")
        if not os.path.exists(local_path):
            os.mkdir(local_path)
        with open(credentials_path, "w") as file:
            return json.dump(credentials, file)

    def request_auth(self):
        print("Requesting authentication")
        response = requests.post("http://google.es", json={"username" : self.username, "password" : self.password})
        if response.status_code == 200:
            return response
        return {"token" : "abcd"}

    def manual_auth(self):
        print("Initiating manual authentication")
        self.username_label = ttk.Label(self, text="Username:")
        self.username_label.pack(pady=(15,5))
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        self.password_label = ttk.Label(self, text="Password:")
        self.password_label.pack(pady=5)
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        self.button_next = ttk.Button(self, text="Sign In", command=self.authenticate)
        self.button_next.pack(pady=30)

        self.signup_button = ttk.Button(self, text="Sign Up", command=self.open_signup_page)
        self.signup_button.pack(pady=50, side="bottom")

    def authenticate(self):
        print("Authenticating")
        if self.username_label:
            self.username_label.pack_forget()
        if self.username_entry:
            self.username = self.username_entry.get()
            self.username_entry.pack_forget()
        if self.password_label:
            self.password_label.pack_forget()
        if self.password_entry:
            self.password = self.password_entry.get()
            self.password_entry.pack_forget()
        if self.button_next:
            self.button_next.pack_forget()
        if self.signup_button:
            self.signup_button.pack_forget()

        if self.username and self.password:
            self.save_credentials({"username" : self.username, "password" : self.password})


        credentials = self.load_credentials()

        if credentials is not None:
            self.username = credentials.get("username")
            self.password = credentials.get("password")
            response = self.request_auth()
            if response:
                return response["token"]
            else:
                self.manual_auth()
        else:
            self.manual_auth()

    def load_stats_directory(self):
        print("Loading stats dir")
        stats_path = os.path.join(HOME, ".kovaaks_tracker/stats_path.txt")
        if os.path.exists(stats_path):
            with open(stats_path) as file:
                return file.read()

    def save_stats_directory(self):
        print("Saving stats dir")
        stats_path = os.path.join(HOME, ".kovaaks_tracker/stats_path.txt")
        local_path = os.path.join(HOME, ".kovaaks_tracker")
        if not os.path.exists(local_path):
            os.mkdir(local_path)
        with open(stats_path, "w") as file:
            file.write(self.stats_path.get())

    def browse_directory(self):
        print("Browsing dirs")
        directory = filedialog.askdirectory()
        if directory:
            self.stats_path.set(directory)

    def open_signup_page(self):
        print("Signing up")
        signup_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with your actual sign-up URL
        webbrowser.open(signup_url)

    def setup_kvks_directory(self):
        print("Preparing stats dir")
        self.kvks_dir_label = tk.Label(self, text="KovaaK's directory")
        self.kvks_dir_label.pack(pady=5)
        self.kvks_dir_entry = tk.Entry(self, textvariable=self.stats_path, width=30)
        self.kvks_dir_entry.pack(pady=5)

        self.browse_button = tk.Button(text="Browse", command=self.browse_directory)
        self.browse_button.pack(pady=5)
        self.done_button = tk.Button(text="Done", command=self.finish_setup)
        self.done_button.pack(pady=5, side="bottom")

    def finish_setup(self):
        print("Finishing setup")
        if not os.path.exists(self.stats_path.get()):
            messagebox.showinfo("Not Found", "The selected directory does not exist on your system.")
        else:
            self.save_stats_directory()
            self.main()

    def main(self):
        print("Main func", self.token)
        
        tk.Label(text=f"Welcome {self.username}!").pack(fill=tk.BOTH)
        self.quit()

if __name__ == "__main__":
    app = SetupWizard()
    app.mainloop()