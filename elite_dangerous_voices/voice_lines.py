"""This module contains the function for gathering events from Elite Dangerous logs to store and
retrieve generated voice lines."""
import os
from pathlib import Path
import json

from dotenv import load_dotenv
from elevenlabs import generate, play, save, Voice, set_api_key

# Load environment variables
load_dotenv()
set_api_key(os.getenv("ELEVENLABS_API_KEY"))


def load_log_file(file_path: Path) -> list:
    """Load a log file and return a list of dicts."""
    data = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Error: La línea no es un JSON válido: {line}")
    return data


def get_latest_npc_line(log_dict) -> dict:
    """Get the latest NPC line from the log dict."""
    # Get the latest NPC line
    npc_lines = [
        line
        for line in log_dict
        if line["event"] == "ReceiveText"
        and line["Channel"] == "npc"
        and "$npc_name_decorate:#name=" in line.get("From", "")
    ]
    if npc_lines:
        return npc_lines[-1]
    else:
        print("No se encontraron líneas de NPC.")
        return {}


def save_voice_line(
    voice_line: dict, file_path: Path, audio_path: Path = Path("./audio")
) -> None:
    """Save a voice line to a json file."""
    # Validate audio path
    if not audio_path.exists():
        audio_path.mkdir()

    data = []
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

    if not already_exists_in_json(voice_line, file_path):
        data.append(voice_line)

    if not voice_line_already_exists(voice_line, Path("audio")):
        print(get_voice_line_path(voice_line, Path("audio")))
        print("La línea de voz NO existe.")
    else:
        print(get_voice_line_path(voice_line, Path("audio")))
        print("La línea de voz YA existe.")

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def already_exists_in_json(voice_line: dict, file_path: Path) -> bool:
    """Check if a voice line already exists in a json file."""
    data = []
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    return voice_line in data


def voice_line_already_exists(voice_line: dict, dir_path: Path) -> bool:
    """Check if a voice line already exists in the audio directory."""
    # Get the voice line path
    voice_line_path = get_voice_line_path(voice_line, dir_path)
    # Check if the voice line already exists
    return voice_line_path.exists()


def get_filename(filename: str) -> str:
    """Get the filename for a voice line."""
    # clean the filename from illegal characters
    illegal_characters = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]
    if filename is not None:
        for character in illegal_characters:
            filename = filename.replace(character, "")
    else:
        print("El nombre del archivo es None.")
    return filename


def get_voice_line_path(voice_line: dict, dir_path: Path) -> Path:
    """Get the path for a voice line."""
    audio_file_extension = ".mp3"
    # Get the voice line filename
    voice_line_filename = get_filename(voice_line.get("Message_Localised"))
    if voice_line_filename is None:
        print("El nombre del archivo de la línea de voz es None.")
        voice_line_filename = ""  # or some default filename
    voice_line_filename += audio_file_extension
    # Return the path
    return dir_path / voice_line_filename

def generate_voice_line_audio_file(voice: Voice, line: str, voice_line_filepath: Path):
    """Generate a voice line audio file."""
    audio = None  # Initialize audio with a default value
    if not voice_line_filepath.exists():
        if isinstance(line, str):
            audio = generate(text=line, voice=voice, model="eleven_turbo_v2")
            save(audio, str(voice_line_filepath))
        else:
            print("La línea no es una cadena.")
    else:
        with open(voice_line_filepath, "rb") as f:
            audio = f.read()
        print(f"File {voice_line_filepath} already exists")
    if audio is not None:
        play(audio)
        print(f"Playing {voice_line_filepath}")
    else:
        print("No audio to play.")

def main():
    """Main function."""
    # Get the user's name
    user_name = os.getlogin()

    # File Location
    # The journal files are written into the user's Saved Games folder, eg, for Windows:
    # C:\Users\User Name\Saved Games\Frontier Developments\Elite Dangerous\
    # The filename is of the form Journal...log, similar to network log files
    log_directory = (
        f"C:\\Users\\{user_name}\\Saved Games\\Frontier Developments\\Elite Dangerous"
    )

    # Get the latest log file
    log_files = [
        file for file in Path(log_directory).iterdir() if file.suffix == ".log"
    ]
    latest_log_file = max(log_files, key=os.path.getctime)

    # Load the log file
    log_dict = load_log_file(latest_log_file)

    # Get the latest NPC line
    latest_npc_line = get_latest_npc_line(log_dict)

    # Save the voice line
    voice_line_file = Path("voice_line.json")
    save_voice_line(latest_npc_line, voice_line_file)


if __name__ == "__main__":
    main()
