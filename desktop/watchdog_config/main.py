import tkinter as tk
from tkinter import filedialog, messagebox

import webbrowser
import json
import os

import logging
from logging.handlers import RotatingFileHandler
import traceback

import requests

HOME = os.getenv("HOME")
if HOME is None:
    HOME = os.path.expanduser("~")
BACKEND_API_URL = "http://localhost:8000/"
SIGN_UP_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
DEFAULT_KVKS_DIR = os.path.join(HOME, "FPSAimTrainer")
DEFAULT_INSTALL_DIR = os.path.join(HOME, "FPSAimTrainer Tracker")
CREDENTIALS_PATH = os.path.join(HOME, ".kvkstracker", "credentials.json")
CONFIG_PATH = os.path.join(HOME, ".kvkstracker", "config.json")
LOGS_ENDPOINT = "http://localhost:8000/analytics/errors"

# LOGGING
logger = logging.getLogger("kvks_tracker")
logger.setLevel(logging.INFO)

log_file = "config.log"
log_type = log_file.split(".")[0]

handler = RotatingFileHandler(log_file, maxBytes=1_048_576, backupCount=1)
handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s | [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

def post_logs(log_string, error, headers):
    global LOGS_ENDPOINT, log_type

    try:
        response = requests.post(LOGS_ENDPOINT, json={"logs" : log_string, "error" : error, "type": log_type}, headers=headers)
        if response.status_code == 201:
            logger.info(f"Error logs sucessfully sent to {LOGS_ENDPOINT}")
        else:
            logger.error(f"HTTP error posting error logs to {LOGS_ENDPOINT}. Status code: {response.status_code}.")
    except requests.RequestException as e:
        logger.error(f"Client error posting error log to {LOGS_ENDPOINT}: {e}")

def log_exception(exc: type[BaseException], headers: dict[str, str]):
    with open(log_file) as file:
        log_string = file.read()
    exc_info = "".join(traceback.format_exception(None, exc, exc.__traceback__))
    logger.error(f"Exception occurred: {exc_info}")
    post_logs(log_string, exc_info, headers)

try:
    os.mkdir(os.path.join(HOME, ".kvkstracker"))
except FileExistsError:
    logger.warning(f"Dotfile folder already exists at {os.path.join(HOME, ".kvkstracker")}")

try:
    with open(CREDENTIALS_PATH) as file:
        data = json.load(file)
        username = data.get("username")
        access_token = data.get("access_token")
except FileNotFoundError:
    logger.warning(f"Could not locate credentials.json at {CREDENTIALS_PATH}")
    username = None
    access_token = None

try:
    with open(CONFIG_PATH) as file:
        data = json.load(file)
        kvks_dir = data.get("kvks_dir", DEFAULT_KVKS_DIR)
        install_dir = data.get("install_dir", DEFAULT_INSTALL_DIR)
except FileNotFoundError:
    logger.warning(f"Could not locate config.json at {CONFIG_PATH}")
    kvks_dir = DEFAULT_KVKS_DIR
    install_dir = DEFAULT_INSTALL_DIR

def cache() -> None:
    global logger
    try:
        logger.info(f"Caching credentials")
        with open(CREDENTIALS_PATH, "w") as file:
            json.dump({"username" : username, "access_token" : access_token}, file)
        
        logger.info(f"Caching config")
        with open(CONFIG_PATH, "w") as file:
            json.dump({"kvks_dir" : kvks_dir, "install_dir" : install_dir}, file)
    except Exception as e:
        log_exception(e)

class Setup(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        global kvks_dir, username

        self.title("KovaaK's Tracker Config")
        self.geometry("600x350")
        self.resizable(False, False)

        # Authentication GUI elements
        self._username = tk.StringVar(self, username)
        self._password = tk.StringVar(self)

        self.username_label = tk.Label(self, text="Username")
        self.username_entry = tk.Entry(self, textvariable=self._username)
        self.password_label = tk.Label(self, text="Password")
        self.password_entry = tk.Entry(self, textvariable=self._password, show="*")

        self.sign_up_label = tk.Label(self, text="Don't have an account?")
        self.sign_up_button = tk.Button(self, text="Sign Up", command=self._sign_up)

        self.invalid_credentials_label = tk.Label(self, text="Invalid credentials")
        self.server_error_label = tk.Label(self, text="Server error")

        # KovaaK's config GUI elements
        self._kvks_dir = tk.StringVar(self, kvks_dir)

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
        global username, access_token, BACKEND_API_URL
        
        self._username.set(self.username_entry.get())
        self._password.set(self.password_entry.get())
        username = self._username.get()
        password = self._password.get()

        token_json = {
            "grant_type" : "password",
            "username" : username,
            "password" : password,
            "scope" : "",
            "client_id" : "",
            "client_secret" : ""
        }

        response = requests.post(url=BACKEND_API_URL + "auth/token", data=token_json)
        if response.status_code == 200:
            access_token = response.json()["access_token"]
            self.invalid_credentials_label.pack_forget()
            self.server_error_label.pack_forget()

        elif response.status_code == 401:
            self.invalid_credentials_label.pack()
        
        else:
            self.server_error_label.pack()

    def _sign_up(self) -> None:
        global SIGN_UP_URL
        webbrowser.open(SIGN_UP_URL)

    def _browse(self) -> None:
        directory = filedialog.askdirectory()
        self._kvks_dir.set(directory)

    def _wrap_up(self) -> None:
        global kvks_dir, install_dir
        self._sign_in()
        if not os.path.exists(self._kvks_dir.get()):
            self.dir_not_found_label.pack()
        elif self.invalid_credentials_label.winfo_manager() == "pack":
            self.dir_not_found_label.pack_forget()
            return
        else:
            kvks_dir = self._kvks_dir.get()
            cache()
            self.run_tracker(install_dir=install_dir)
            self.quit()

    def run_tracker(self, install_dir):
        """Run the kvks_tracker.exe file."""
        app_path = os.path.join(install_dir, "config.exe")
        if os.path.exists(app_path):
            os.startfile(app_path)
            self.quit()
        else:
            messagebox.showerror("Error", f"kvks_tracker.exe not found in {install_dir}")

def main() -> None:
    global logger
    try:
        app = Setup()    
        app.mainloop()
    except Exception as e:
        log_exception(e)

if __name__ == "__main__":
    main()