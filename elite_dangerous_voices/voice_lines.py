"""This module contains the function for gathering events from Elite Dangerous logs to store and
retrieve generated voice lines."""
import os
from pathlib import Path
import json


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
    npc_lines = [line for line in log_dict if line["event"] == "ReceiveText" and line["Channel"] == "npc" and "$npc_name_decorate:#name=" in line.get("From", "")]
    if npc_lines:
        return npc_lines[-1]
    else:
        print("No se encontraron líneas de NPC.")
        return {}

def save_voice_line(voice_line: dict, file_path: Path) -> None:
    """Save a voice line to a json file."""
    data = []
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    if not already_exists(voice_line, file_path):
        data.append(voice_line)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def already_exists(voice_line: dict, file_path: Path) -> bool:
    """Check if a voice line already exists in a json file."""
    data = []
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    return voice_line in data

def main():
    """Main function."""
    # Get the user's name
    user_name = os.getlogin()

    # File Location
    # The journal files are written into the user's Saved Games folder, eg, for Windows:
    # C:\Users\User Name\Saved Games\Frontier Developments\Elite Dangerous\
    # The filename is of the form Journal...log, similar to network log files
    log_directory = f"C:\\Users\\{user_name}\\Saved Games\\Frontier Developments\\Elite Dangerous"

    # Get the latest log file
    log_files = [file for file in Path(log_directory).iterdir() if file.suffix == ".log"]
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