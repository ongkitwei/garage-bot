import os

UPLOAD_STATE = 1
BROADCAST_STATE = 2
DEADLINE_STATE = 3

USER_DB_FILE = "users.txt"

admin_id_env = os.getenv("ADMIN_ID")
ADMIN_IDS = [int(admin_id_env)] if admin_id_env else []