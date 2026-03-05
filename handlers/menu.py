from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from states import ADMIN_IDS
from commands.introduction import introduction_cmd
from keyboards import get_main_keyboard, get_upload_keyboard
from utils import save_user
from states import DEADLINE_STATE, UPLOAD_STATE, BROADCAST_STATE
from commands.event import event_cmd

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