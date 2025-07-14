import os
from telegram import Update
from telegram.ext import ContextTypes
from cryptography.fernet import Fernet
from features import notify_cookie_fixed
import logging

logger = logging.getLogger(__name__)


ENC_FILENAME = "cookies.enc"
ENC_PATH = "/tmp/cookies.enc"
DECRYPTED_PATH = "/tmp/cookies.txt"
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

async def handle_cookie_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("сорри, это дело для админа")
        return

    document = update.message.document

    if not document or document.file_name != ENC_FILENAME:
        await update.message.reply_text("сорри, ем только печеньку)")
        return

    if not ENCRYPTION_KEY:
        await update.message.reply_text("нечем открыть")
        return

    try:
        # step 1 - file download
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(ENC_PATH)

        # step 2 - decryption
        fernet = Fernet(ENCRYPTION_KEY.encode())

        with open(ENC_PATH, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)

        with open(DECRYPTED_PATH, "wb") as f:
            f.write(decrypted_data)

        await update.message.reply_text("печенька съедена)")

        # notify users
        try:
            await notify_cookie_fixed(context.bot)
        except Exception as notify_error:
            logger.warning(f"⚠️ Ошибка при уведомлении пользователей: {notify_error}")


    except Exception as e:
        await update.message.reply_text(f"не могу развернуть")

