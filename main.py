import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

from features import start_keep_alive_scheduler
from handlers import unified_handler, handle_cookie_upload

start_keep_alive_scheduler()

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

recent_responded = set()   # anti-double'/start' for mobile devices


# === /start ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id

    # remove previous 👁
    last_emoji_msg_id = context.user_data.get("emoji_msg_id")
    if last_emoji_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=last_emoji_msg_id)
        except Exception:
            pass
        finally:
            context.user_data["emoji_msg_id"] = None

    # send new 👁
    sent = await update.message.reply_text("👁")
    context.user_data["emoji_msg_id"] = sent.message_id


# === Run ===
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("Переменная окружения BOT_TOKEN не установлена.")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_cookie_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unified_handler))
    app.run_polling(allowed_updates=["message", "document", "text"])

