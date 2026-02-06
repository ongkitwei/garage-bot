import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.file']
PARENT_FOLDER_ID = "1dok8ZrC9udm5rHiOSKt2_c7bpTgnmI_U"

def get_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def upload_file(file_path):
    creds = get_credentials()
    service = build('drive', 'v3', credentials=creds)

    original_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)
    
    file_metadata = {
        'name': original_name,
        'parents': [PARENT_FOLDER_ID]
    }

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        drive_id = file.get('id')
        print(f"Success! Uploaded as YOU. File ID: {file.get('id')}")
        return drive_id
    except Exception as e:
        print(f"Upload failed: {e}")
        return None
    
if __name__ == "__main__":
    upload_file("users.txt")