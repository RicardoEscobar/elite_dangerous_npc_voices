import sys
import os
import time
import logging
import re
from pathlib import Path

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler = logging.FileHandler('watch_logs.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class CustomEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.log_pattern = re.compile(r"Journal\.\d{4}-\d{2}-\d{2}T\d{6}\.\d{2}\.log")

    def on_modified(self, event):
        if self.log_pattern.search(os.path.basename(event.src_path)):
            logging.info(f'Archivo modificado: {event.src_path}')

    def on_created(self, event):
        if self.log_pattern.search(os.path.basename(event.src_path)):
            logging.info(f'Archivo creado: {event.src_path}')



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = CustomEventHandler()
    observer = PollingObserver()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    finally:
        observer.stop()
        observer.join()
