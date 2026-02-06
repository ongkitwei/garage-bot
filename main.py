import logging
import asyncio 
import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from commands.introduction import introduction_cmd
from commands.event import event_cmd
from commands.deadlines import deadlines_cmd
from commands.upload_file import upload_file_cmd

from dotenv import load_dotenv  
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from test_google_drive import upload_file as drive_upload
from update_sheets_link import update_sheets_link

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
TEMPLATE_URL = os.getenv("TEMPLATE_URL")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_KEY_FILE")

# Handle Admin ID (Convert string from env to integer)
admin_id_env = os.getenv("ADMIN_ID")
ADMIN_IDS = [int(admin_id_env)] if admin_id_env else []

# Validation: Check if token exists before running
if not BOT_TOKEN:
    raise ValueError("❌ Error: TELEGRAM_BOT_TOKEN is missing in .env file")

# States for ConversationHandler
UPLOAD_STATE = 1
BROADCAST_STATE = 2
DEADLINE_STATE = 3

# Logging Setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

USER_DB_FILE = "users.txt"

async def handle_deadline_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    await update.message.reply_text("⏳ Searching...")

    # Call your python function
    try:
        response = deadlines_cmd(user_input)
    except Exception as e:
        response = f"❌ Error: {e}"

    # CRITICAL FIX: Ensure response is never None or Empty
    if not response or response.strip() == "":
        response = "⚠️ Unknown error: The search returned an empty result."

    await update.message.reply_text(response, parse_mode='Markdown')
    return ConversationHandler.END

# ================= GOOGLE DRIVE HELPER =================
def upload_file_to_drive(file_path, file_name):
    """Uploads a file to the configured Google Drive folder."""
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            logging.error(f"❌ Service account file not found: {SERVICE_ACCOUNT_FILE}")
            return None

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=['https://www.googleapis.com/auth/drive']
        )
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': file_name,
            'parents': [GDRIVE_FOLDER_ID]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        return file.get('id')
    except Exception as e:
        logging.error(f"Drive Error: {e}")
        return None

# ================= HELPER FUNCTIONS =================
def save_user(user_id):
    """Saves user ID to a text file to track registered users."""
    users = set()
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "r") as f:
            users = set(f.read().splitlines())
    
    if str(user_id) not in users:
        with open(USER_DB_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_upload_keyboard():
    keyboard = [
    ["🔥 builder", "🔥 thunder"],
        ["🔥 tim", "🔥 deepsit"],
        ["🔥 strikers", "🔥 newentrepreneurs"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_main_keyboard():
    keyboard = [
        ["👋 Introduction", "📅 Deadlines"],
        ["📥 Upload File", "📌 Event"],
        ["⏰ Set Reminder"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ================= HANDLERS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user(user.id)
    await update.message.reply_text(
        f"Hi {user.first_name}! 👋 Choose what you want to do:",
        reply_markup=get_main_keyboard()
    )

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "👋 Introduction":
        await update.message.reply_text(introduction_cmd(), parse_mode='Markdown')


    elif text == "📅 Deadlines":
        await update.message.reply_text(
                    "🔎 Please enter the **Module No** (e.g 1):", 
                    parse_mode='Markdown'
                )
        return DEADLINE_STATE

    elif text == "📌 Event":
        await update.message.reply_text("⏳ Searching for upcoming events...")
        response = event_cmd()
        await update.message.reply_text(response, parse_mode='Markdown')

    elif text == "📥 Upload File":
        sent_message = await update.message.reply_text(
         "📥 **Upload Menu**\n\n"
            "Please select the category for your upload:",
            reply_markup=get_upload_keyboard(), 
            parse_mode='HTML'
        )
        context.user_data['menu_message_id'] = sent_message.message_id
        return UPLOAD_STATE

    elif text == "⏰ Set Reminder":
        if user_id in ADMIN_IDS:
            await update.message.reply_text(
                "🔓 **Admin Access Granted**\n"
                "Type the broadcast message below.\nType /cancel to stop."
            )
            return BROADCAST_STATE
        else:
            await update.message.reply_text("⛔ You do not have permission to use this feature.")

    return ConversationHandler.END

# ================= UPLOAD FLOW =================

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    teams = ["🔥 builder", "🔥 thunder", "🔥 tim", "🔥 deepsit", "🔥 strikers", "🔥 newentrepreneurs"]

    # --- PHASE 1: User selected a team ---
    if text in teams:
        context.user_data['upload_category'] = text

        menu_msg_id = context.user_data.get('menu_message_id')
        if menu_msg_id:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=menu_msg_id)
            except Exception:
                pass 

        from telegram import ReplyKeyboardRemove
        await update.message.reply_text(
            f"✅ Team **{text}** selected.\n\n📤 **Please upload your file here now.**",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='Markdown'
        )
        return UPLOAD_STATE 

    # --- PHASE 2: User sends the actual file ---
    if update.message.document:
        doc = update.message.document
        category = context.user_data.get('upload_category', 'General')
        status_msg = await update.message.reply_text("📥 Downloading from Telegram...")

        local_filename = doc.file_name
        
        try:
            # 1. Download the file locally
            telegram_file = await context.bot.get_file(doc.file_id)
            await telegram_file.download_to_drive(local_filename)

            # 2. Upload to Google Drive
            await status_msg.edit_text(f"📤 Uploading <b>{local_filename}</b> to Drive...", parse_mode='HTML')
            
            loop = asyncio.get_event_loop()
            drive_id = await loop.run_in_executor(None, drive_upload, local_filename)

            # ... (Inside Phase 2: if update.message.document) ...
            if drive_id:
                link = f"https://drive.google.com/file/d/{drive_id}/view"
                
                # 1. Initialize status_text immediately
                status_text = "✅ <b>File Uploaded!</b>"
                
                # 2. Try to update the sheet
                try:
                    sheet_success = update_sheets_link(category, link)
                    if sheet_success:
                        status_text += "\n📊 <i>Google Sheet updated successfully.</i>"
                    else:
                        status_text += "\n⚠️ <i>Drive OK, but Sheet update failed.</i>"
                except Exception as sheet_err:
                    logging.error(f"Sheet logic crash: {sheet_err}")
                    status_text += "\n⚠️ <i>Sheet update system error.</i>"

                # 3. Safe delete the "Uploading..." message
                try:
                    await status_msg.delete()
                except:
                    pass

                # 4. Final Reply
                await update.message.reply_text(
                    f"{status_text}\n\n"
                    f"<b>Team:</b> {category}\n"
                    f"🔗 <a href='{link}'>View on Drive</a>",
                    parse_mode='HTML',
                    reply_markup=get_main_keyboard()
                )
            else:
                await update.message.reply_text("❌ Upload failed: Drive did not return an ID.", reply_markup=get_main_keyboard())

        except Exception as e:
            logging.error(f"Upload flow error: {e}")
            await update.message.reply_text(f"❌ Error: {e}", reply_markup=get_main_keyboard())
        
        finally:
            # 3. CLEANUP: Final safe delete and local file removal
            try:
                # If it wasn't deleted in the success block, delete it now
                await status_msg.delete()
            except Exception:
                pass 

            if os.path.exists(local_filename):
                os.remove(local_filename)

        return ConversationHandler.END

    await update.message.reply_text("Please send a valid file (Document).")
    return UPLOAD_STATE

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_to_send = update.message.text
    
    if not os.path.exists(USER_DB_FILE):
        await update.message.reply_text("No registered users found.")
        return ConversationHandler.END

    with open(USER_DB_FILE, "r") as f:
        user_ids = f.read().splitlines()

    count = 0
    await update.message.reply_text(f"📢 Sending broadcast to {len(user_ids)} users...")

    for uid in user_ids:
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"⏰ **REMINDER**\n\n{message_to_send}", parse_mode='Markdown')
            count += 1
        except Exception:
            continue

    await update.message.reply_text(f"✅ Broadcast complete. Sent to {count} users.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

# ================= MAIN =================

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    upload_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📥 Upload File$"), handle_menu_buttons)],
        states={UPLOAD_STATE: [# 1. Listen for the team selection (Text)
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_file),
            MessageHandler(filters.Document.ALL, receive_file)]},
        fallbacks=[CommandHandler("cancel", cancel), MessageHandler(filters.TEXT, cancel)]
    )

    broadcast_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^⏰ Set Reminder$"), handle_menu_buttons)],
        states={BROADCAST_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    deadline_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^📅 Deadlines$"), handle_menu_buttons)],
            states={
                DEADLINE_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_deadline_input)]
            },
            fallbacks=[CommandHandler("cancel", cancel)]
        )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(upload_handler)
    application.add_handler(broadcast_handler)
    application.add_handler(deadline_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    print(f"🤖 Bot is running with Admin ID: {ADMIN_IDS}")
    application.run_polling()