import tkinter as tk
from tkinter import filedialog

import webbrowser
import os

import requests

import config

class Setup(tk.Tk):

    def __init__(self) -> None:
        super().__init__()

        self.title("KovaaK's - Voltaic Tracker Setup")
        self.geometry("600x350")
        self.resizable(False, False)

        self.config = config.Config()

        # Authentication GUI elements
        self._username = tk.StringVar(self, self.config.username)
        self._password = tk.StringVar(self, self.config.password)

        self.username_label = tk.Label(self, text="Username")
        self.username_entry = tk.Entry(self, textvariable=self._username)
        self.password_label = tk.Label(self, text="Password")
        self.password_entry = tk.Entry(self, textvariable=self._password, show="*")

        self.sign_up_label = tk.Label(self, text="Don't have an account?")
        self.sign_up_button = tk.Button(self, text="Sign Up", command=self._sign_up)

        self.invalid_credentials_label = tk.Label(self, text="Invalid credentials")

        # KovaaK's config GUI elements
        self._kvks_dir = tk.StringVar(self, self.config.kvks_dir)

        self.kvks_dir_label = tk.Label(self, text="KovaaK's directory")
        self.kvks_dir_entry = tk.Entry(self, textvariable=self._kvks_dir, width=75)
        self.browse_button = tk.Button(self, text="Browse", command=self._browse)
        self.confirm_button = tk.Button(self, text="Done!", command=self._wrap_up)

        self.dir_not_found_label = tk.Label(self, text="Directory not found")

        # Main logic
        self._authenticate()  
        self._config()
            

    def _authenticate(self) -> None:

        self.username_label.pack(pady=(15,0))
        self.username_entry.pack()

        self.password_label.pack()
        self.password_entry.pack()

        self.sign_up_label.pack(pady=(15,0))
        self.sign_up_button.pack(pady=(5,0))

    def _config(self) -> None:
        
        self.kvks_dir_label.pack(pady=(20,0))
        self.kvks_dir_entry.pack()
        self.browse_button.pack(pady=(5,0))
        self.confirm_button.pack(pady=(10,0))


    def _sign_in(self) -> None:
        
        self._username.set(self.username_entry.get())
        self._password.set(self.password_entry.get())
        self.config.username = self._username.get()
        self.config.password = self._password.get()
        self.config.cache()

        response = requests.get(self.config.backend_api_url)
        if not response.status_code == 200:
            self.invalid_credentials_label.pack()

    def _sign_up(self) -> None:
        webbrowser.open(self.config.sign_up_url)

    def _browse(self) -> None:
        directory = filedialog.askdirectory()
        self._kvks_dir.set(directory)

    def _wrap_up(self) -> None:
        if os.path.exists(self._kvks_dir.get()):
            self.config.kvks_dir = self._kvks_dir.get()
            self._sign_in()
            self.config.cache()
            self.quit()
        else:
            self.dir_not_found_label.pack()

def main() -> None:
    app = Setup()    
    app.mainloop()

if __name__ == "__main__":
    main()