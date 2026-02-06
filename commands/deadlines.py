import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def deadlines_cmd(task_input):
    url = os.getenv("APPS_SCRIPT_URL")
    
    # 1. Safety Check: Is the URL set?
    if not url:
        return "❌ Error: APPS_SCRIPT_URL is missing in .env file."

    payload = {
        "action": "deadline",
        "moduleNo": task_input
    }
    
    try:
        response = requests.post(url, json=payload)
        
        # 2. Try parsing JSON
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            return f"❌ Error: Server returned non-JSON response. (Status: {response.status_code})"

        # 3. Extract status, handling 'None' explicitly
        status = response_data.get("status")
        
        if status is None:
            return "⚠️ Error: Google Script returned no status (null)."
        
        # 4. Ensure we return a string, even if status is something else
        return str(status)

    except Exception as e:
        return f"❌ Connection Error: {str(e)}"

if __name__ == "__main__":
    print(deadlines_cmd("15"))