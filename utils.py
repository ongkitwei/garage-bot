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

