import os

import time

import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

HOME = os.getenv("HOME")

class StatsHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'File {event.src_path} has been modified.')

    def on_created(self, event):
        print(f'File {event.src_path} has been created.')

    def on_deleted(self, event):
        print(f'File {event.src_path} has been deleted.')

    def on_moved(self, event):
        print(f'File {event.src_path} was moved to {event.dest_path}.')

def main():
    config_path = os.path.join(HOME, ".kvkstracker/config.json")
    with open(config_path) as f:
        path = os.path.join(json.load(f).get("kvks_dir"), "FPSAimTrainer/stats")

    handler = StatsHandler()
    observer = Observer()
    observer.schedule(handler, path, recursive=True)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()

if __name__ == "__main__":
    main()