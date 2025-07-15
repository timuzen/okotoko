import re
import asyncio
import random
import os
from telegram import Update
from telegram.ext import ContextTypes

from features import get_quote
from handlers import handle_link


recent_responded = set()


async def unified_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip().lower()
    chat_id = update.effective_chat.id

    if re.fullmatch(r"\d+", text):
        number = int(text)
        if number > 0:
            random_value = random.randint(0, number)
            await update.message.reply_text(f"{random_value}")
            return


    # youtube link validation
    if "youtube.com" in text or "youtu.be" in text:
        return await handle_link(update, context)

    # Remove 👁
    last_emoji_msg_id = context.user_data.get("emoji_msg_id")
    if last_emoji_msg_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=last_emoji_msg_id)
        except Exception:
            pass
        finally:
            context.user_data["emoji_msg_id"] = None

    if chat_id in recent_responded:   # anti-double'/start'
        return

    meaningful_response = False   # anti-double'/start'

    if text in ("йо", "yo"):
        lang = "ru" if text == "йо" else "en"
        quote, author = get_quote(lang=lang)
        await update.message.reply_text(quote)
        key_prefix = "ru" if lang == "ru" else "en"
        context.user_data[f"{key_prefix}_author"] = author
        context.user_data[f"{key_prefix}_used"] = False
        meaningful_response = True

    elif text in ("кто", "who"):
        key_prefix = "ru" if text == "кто" else "en"
        author = context.user_data.get(f"{key_prefix}_author")
        used = context.user_data.get(f"{key_prefix}_used", True)
        if author and not used:
            await update.message.reply_text(f"— {author}")
            context.user_data[f"{key_prefix}_used"] = True
            meaningful_response = True
        else:
            sent = await update.message.reply_text("👁")
            context.user_data["emoji_msg_id"] = sent.message_id

    else:
        sent = await update.message.reply_text("👁")
        context.user_data["emoji_msg_id"] = sent.message_id

    if meaningful_response:
        recent_responded.add(chat_id)

        async def clear_flag():
            await asyncio.sleep(2)
            recent_responded.discard(chat_id)

        asyncio.create_task(clear_flag())