from dotenv import load_dotenv  
import logging
import os

from handlers.menu import handle_menu_buttons, start
from handlers.deadlines import handle_deadline_input
from handlers.upload import receive_file, cancel
from handlers.broadcast import broadcast_message
from keyboards import get_main_keyboard
from states import DEADLINE_STATE, UPLOAD_STATE, BROADCAST_STATE, ADMIN_IDS, USER_DB_FILE

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
TEMPLATE_URL = os.getenv("TEMPLATE_URL")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_KEY_FILE")

if not BOT_TOKEN:
    raise ValueError("❌ Error: TELEGRAM_BOT_TOKEN is missing in .env file")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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