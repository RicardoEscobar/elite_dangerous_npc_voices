"""This module contains the function for gathering events from Elite Dangerous logs."""
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import generate, play, save, Voice, set_api_key

from voice_lines import (
    load_log_file,
    get_latest_npc_line,
    save_voice_line,
    get_voice_line_path,
    generate_voice_line_audio_file,
)

# Get the user's name
user_name = os.getlogin()

# Load environment variables
load_dotenv()
set_api_key(os.getenv("ELEVENLABS_API_KEY"))

# The Player Journal is written in line-delimited JSON format (see son.org and jsonlines.org), to
# provide a standard format for ease of machine parsing, while still being intelligible to the human
# reader. Each Journal file is a series of lines each containing one Json object.

# File Location
# The journal files are written into the user's Saved Games folder, eg, for Windows:
# C:\Users\User Name\Saved Games\Frontier Developments\Elite Dangerous\
# The filename is of the form Journal...log, similar to network log files
log_directory = (
    f"C:\\Users\\{user_name}\\Saved Games\\Frontier Developments\\Elite Dangerous"
)


def main():
    """Main function."""
    voice_used = Voice(voice_id="SwO8WtmPRCrI62g6hDwf")
    # Test voice generation
    generate_voice_line_audio_file(
        voice=voice_used,
        line="You've got no right to scan me, officer!",
        voice_line_filepath=Path(
            "./audio/You've got no right to scan me, officer!.mp3"
        ),
    )


if __name__ == "__main__":
    main()
