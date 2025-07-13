import os
from telegram import Update
from telegram.ext import ContextTypes

COOKIE_FILENAME = "cookies.txt"
COOKIE_PATH = "/tmp/cookies.txt"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

async def handle_cookie_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("сорри, только админ может это делать")
        return

    document = update.message.document

    if not document or document.file_name != COOKIE_FILENAME:
        await update.message.reply_text("только печеньки")
        return

    try:
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(COOKIE_PATH)
        await update.message.reply_text("печенька съедена)")
    except Exception as e:
        await update.message.reply_text(f"Упс!\n\n {e}")
