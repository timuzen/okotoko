import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
from quote_provider import get_quote

logging.basicConfig(level=logging.INFO)
load_dotenv()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip().lower()

    # Удалить предыдущий глаз
    last_emoji_msg_id = context.user_data.get("emoji_msg_id")
    if last_emoji_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_emoji_msg_id)
        except Exception:
            pass
        finally:
            context.user_data["emoji_msg_id"] = None

    if text in ("йо", "yo"):
        lang = "ru" if text == "йо" else "en"
        quote, author = get_quote(lang=lang)
        await update.message.reply_text(quote)
        key_prefix = "ru" if lang == "ru" else "en"
        context.user_data[f"{key_prefix}_author"] = author
        context.user_data[f"{key_prefix}_used"] = False

    elif text in ("автор", "author"):
        key_prefix = "ru" if text == "автор" else "en"
        author = context.user_data.get(f"{key_prefix}_author")
        used = context.user_data.get(f"{key_prefix}_used", True)
        if author and not used:
            await update.message.reply_text(f"— {author}")
            context.user_data[f"{key_prefix}_used"] = True
        else:
            sent = await update.message.reply_text("👁")
            context.user_data["emoji_msg_id"] = sent.message_id

    else:
        sent = await update.message.reply_text("👁")
        context.user_data["emoji_msg_id"] = sent.message_id

if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise RuntimeError("Переменная окружения BOT_TOKEN не установлена.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
