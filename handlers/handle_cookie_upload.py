import os
from telegram import Update
from telegram.ext import ContextTypes
from cryptography.fernet import Fernet

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
        await update.message.reply_text("нужна печенька в обвертке")
        return

    if not ENCRYPTION_KEY:
        await update.message.reply_text("нечем открыть печеньку")
        return

    try:
        # Шаг 1 — загрузка файла
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(ENC_PATH)
        await update.message.reply_text("печенька получена")

        # Шаг 2 — расшифровка
        fernet = Fernet(ENCRYPTION_KEY.encode())

        with open(ENC_PATH, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)

        with open(DECRYPTED_PATH, "wb") as f:
            f.write(decrypted_data)

        await update.message.reply_text("печенька съедена)")
    except Exception as e:
        await update.message.reply_text(f"Упс!:\n\n{e}")

