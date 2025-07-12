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

    # Удалить предыдущее 👁, если было
    last_emoji_msg_id = context.user_data.get("emoji_msg_id")
    if last_emoji_msg_id:
        try:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=last_emoji_msg_id)
        except Exception:
            pass
        finally:
            context.user_data["emoji_msg_id"] = None

    if text == "йо":
        quote, author = get_quote()
        await update.message.reply_text(quote)
        context.user_data["last_author"] = author
        context.user_data["author_used"] = False  # сбрасываем флаг

    elif text == "автор":
        author = context.user_data.get("last_author")
        used = context.user_data.get("author_used", True)
        if author and not used:
            await update.message.reply_text(f"— {author}")
            context.user_data["author_used"] = True
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
