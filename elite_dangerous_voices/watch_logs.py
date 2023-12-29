import sys
import os
import time
import logging
import re
from pathlib import Path

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from elevenlabs import Voice

from voice_lines import (
    generate_voice_line_audio_file,
    load_log_file,
    get_latest_npc_line,
    save_voice_line,
    get_voice_line_path,
)


# Logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(message)s")
file_handler = logging.FileHandler("./logs/watch_logs.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class CustomEventHandler(FileSystemEventHandler):
    # Get the user's name
    user_name = os.getlogin()

    # File Location
    # The journal files are written into the user's Saved Games folder, eg, for Windows:
    # C:\Users\User Name\Saved Games\Frontier Developments\Elite Dangerous\
    # The filename is of the form Journal...log, similar to network log files
    log_directory = (
        f"C:\\Users\\{user_name}\\Saved Games\\Frontier Developments\\Elite Dangerous"
    )

    # Voice
    voice = Voice(voice_id="SwO8WtmPRCrI62g6hDwf")

    def __init__(self):
        self.log_pattern = re.compile(r"Journal\.\d{4}-\d{2}-\d{2}T\d{6}\.\d{2}\.log")
        self.last_npc_line = None

    def on_modified(self, event):
        if self.log_pattern.search(os.path.basename(event.src_path)):
            logger.info(f"Archivo modificado: {event.src_path}")
            self.run_voice_generation()

    def on_created(self, event):

        if self.log_pattern.search(os.path.basename(event.src_path)):
            logger.info(f"Archivo creado: {event.src_path}")

    def run_voice_generation(self):
        # Get the latest log file
        log_files = [
            file for file in Path(self.log_directory).iterdir() if file.suffix == ".log"
        ]
        latest_log_file = max(log_files, key=os.path.getctime)

        # Load the log file
        log_dict = load_log_file(latest_log_file)

        # Get the latest NPC line
        new_npc_line = get_latest_npc_line(log_dict)
        if new_npc_line == self.last_npc_line:
            return
        else:
            self.last_npc_line = new_npc_line

        # Save the voice line
        voice_line_file = Path("voice_line.json")
        save_voice_line(self.last_npc_line, voice_line_file)

        # Save voice line audio file
        voice_line_filepath = get_voice_line_path(self.last_npc_line, Path("./audio"))
        generate_voice_line_audio_file(
            voice=self.voice,
            line=self.last_npc_line.get("Message_Localised"),
            voice_line_filepath=voice_line_filepath,
        )

    @classmethod
    def run_watchdog(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        path = self.log_directory
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


if __name__ == "__main__":
    CustomEventHandler.run_watchdog()
