from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from commands.deadlines import deadlines_cmd

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