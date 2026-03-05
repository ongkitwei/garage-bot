from telegram import Update, ReplyKeyboardMarkup

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