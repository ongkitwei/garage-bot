import requests
import os
import logging
def update_sheets_link(category_text, file_link):
    script_url = os.getenv("APPS_SCRIPT_URL")
    
    if not script_url or "macros/s/" not in script_url:
        logging.error("❌ Invalid or missing APPS_SCRIPT_URL in .env")
        return False

    category_text = category_text.strip()
    if " " in category_text:
        clean_team_name = category_text.split(" ")[1].lower()
    else:
        clean_team_name = category_text.lower()

    # --- ADD THE ACTION HERE ---
    payload = {
        "action": "upload",  # <--- THIS MUST MATCH your Apps Script 'if' condition
        "teamName": clean_team_name,
        "fileLink": file_link
    }
    # ---------------------------

    try:
        response = requests.post(script_url, json=payload, timeout=10, allow_redirects=True)
        
        # Add this print temporarily to see what the script actually says!
        print(f"DEBUG: Apps Script Response -> {response.text}")

        if response.status_code == 200:
            logging.info(f"✅ Sheet updated for: {clean_team_name}")
            return True
        else:
            logging.error(f"❌ Sheet Error {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"❌ Sheet Connection Failed: {e}")
        return False