import os
import json

from typing import TypeVar

T = TypeVar("T", bound="Config")

class Config:
    _instance: "Config" = None

    def __new__(cls, *args, **kwargs) -> T:
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self) -> None:
        
        self.HOME = os.getenv("HOME")
        self.backend_api_url = "https://www.google.com"
        self.sign_up_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self._default_kvks_dir = f"{self.HOME}\\FPSAimTrainer"
        self.credentials_path = f"{self.HOME}\\.kvkstracker\\credentials.json"
        self.config_path = f"{self.HOME}\\.kvkstracker\\config.json"

        try:
            os.mkdir(f"{self.HOME}\\.kvkstracker")
        except FileExistsError: pass

        try:
            with open(self.credentials_path) as file:
                data = json.load(file)
                self.username = data.get("username")
                self.password = data.get("password")
        except FileNotFoundError:
            self.username = None
            self.password = None

        try:
            with open(self.config_path) as file:
                data = json.load(file)
                self.kvks_dir = data.get("kvks_dir", self._default_kvks_dir)
        except FileNotFoundError:
            self.kvks_dir = self._default_kvks_dir

    def cache(self) -> None:
        with open(self.credentials_path, "w") as file:
            json.dump({"username" : self.username, "password" : self.username}, file)
        
        with open(self.config_path, "w") as file:
            json.dump({"kvks_dir" : self.kvks_dir}, file)