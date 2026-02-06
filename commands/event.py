import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def event_cmd():
    # 1. Get the URL from your .env file
    url = os.getenv("APPS_SCRIPT_URL")
    
    if not url:
        return "❌ Error: APPS_SCRIPT_URL is missing in .env file."

    # 2. Prepare the payload
    # "action": "event" tells the Apps Script to run the 'handleEventUpdate' logic
    payload = {
        "action": "event"
    }

    try:
        # 3. Send POST request to Google Script
        response = requests.post(url, json=payload)
        
        # 4. Parse the JSON response
        try:
            data = response.json()
        except json.JSONDecodeError:
             return f"❌ Error: Server returned non-JSON. Status: {response.status_code}"

        # 5. Extract the result
        result = data.get("status")

        if not result:
            return "⚠️ No events found or script returned empty."

        # 6. Fix Formatting for Telegram 'Markdown' mode
        # The script uses "**" for bold, but Telegram Legacy Markdown prefers "*"
        # We replace double stars with single stars to ensure it bolds correctly.
        formatted_result = result.replace("**", "*")
        
        return formatted_result

    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

if __name__ == "__main__":
    # Test block to run this file directly
    print(event_cmd())