import os
import pickle
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

async def upload_file_cmd(update, context, folder_id, token_file='token.pickle'):
    user = update.effective_user
    document = update.message.document
    category = context.user_data.get('upload_category', 'General')
    
    file = await document.get_file()
    local_path = f"temp_{user.id}_{document.file_name}"
    await file.download_to_drive(local_path)

    try:
        # Load OAuth credentials from token file
        if not os.path.exists(token_file):
            await update.message.reply_text("❌ Bot not authenticated! Contact admin.")
            return None
            
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
        
        # Refresh token if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': f"[{category}] {document.file_name}",
            'parents': [folder_id]
        }
        media = MediaFileUpload(local_path, resumable=True)
        
        # Upload file
        drive_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        return drive_file.get('webViewLink')

    except Exception as e:
        print(f"Error during Drive process: {e}")
        return None
    finally:
        if os.path.exists(local_path):
            os.remove(local_path)