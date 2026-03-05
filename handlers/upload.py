from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from test_google_drive import upload_file as drive_upload
from states import ADMIN_IDS
from update_sheets_link import update_sheets_link
from keyboards import get_main_keyboard
from states import DEADLINE_STATE, UPLOAD_STATE, BROADCAST_STATE
import logging 
import os
import asyncio

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.", reply_markup=get_main_keyboard())
    return ConversationHandler.END

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    
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