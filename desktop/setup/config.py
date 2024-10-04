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
            "http://backup-mirror-link-to-app.com/app.zip"
        ]