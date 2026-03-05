from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import ADMIN_IDS
from commands.introduction import introduction_cmd
from keyboards import get_main_keyboard, get_upload_keyboard
from utils import save_user
from states import USER_DB_FILE
import os

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