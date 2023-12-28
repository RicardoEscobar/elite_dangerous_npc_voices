"""This module contains the function for gathering events from Elite Dangerous logs."""
import os
import json
from pathlib import Path


# Get the user's name
user_name = os.getlogin()

# The Player Journal is written in line-delimited JSON format (see son.org and jsonlines.org), to
# provide a standard format for ease of machine parsing, while still being intelligible to the human
# reader. Each Journal file is a series of lines each containing one Json object.

# File Location
# The journal files are written into the user's Saved Games folder, eg, for Windows:
# C:\Users\User Name\Saved Games\Frontier Developments\Elite Dangerous\
# The filename is of the form Journal...log, similar to network log files
log_directory = f"C:\\Users\\{user_name}\\Saved Games\\Frontier Developments\\Elite Dangerous"
