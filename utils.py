# utils.py
import os
from states import USER_DB_FILE

def save_user(user_id):
    """Saves user ID to a text file."""
    users = set()
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            users = set(f.read().splitlines())
    
    if str(user_id) not in users:
        with open(USER_DB_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_allowed_usernames():
    """Reads the allowed_users.txt file and returns a list of lowercase handles."""
    file_path = "allowed_users.txt"
    if not os.path.exists(file_path):
        # If the file doesn't exist, you might want to log a warning
        return []
    
    with open(file_path, "r") as f:
        # strip() removes spaces/newlines, lower() ensures case-insensitive matching
        return [line.strip().lower() for line in f if line.strip()]