import asyncio
import re
import random
from telegram import Update
from telegram.ext import ContextTypes
import json
from pathlib import Path

from features import get_quote
from handlers import handle_link


recent_responded = set()
help_file = Path("configs/help.json")


async def unified_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip().lower()
    chat_id = update.effective_chat.id

    # print(f"[debug] raw text: {repr(text)}")

    max_random_limit = 10 ** 12
    if re.fullmatch(r"[0-9]+", text):
        number = int(text)
        if 0 < number <= max_random_limit:
            if number == 1:
                random_value = random.random()
            else:
                random_value = random.randint(1, number)
            await update.message.reply_text(str(random_value))
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

    elif text in ("чо", "wha"):
        answer = random.choice(["да", "нет"] if text == "чо" else ["yes", "no"])
        await update.message.reply_text(answer)
        meaningful_response = False

    elif text in ("кто", "who"):
        key_prefix = "ru" if text == "кто" else "en"
        author = context.user_data.get(f"{key_prefix}_author")
        used = context.user_data.get(f"{key_prefix}_used", True)
        if author and not used:
            await update.message.reply_text(f"— {author}")
            context.user_data[f"{key_prefix}_used"] = True
            meaningful_response = False
        else:
            sent = await update.message.reply_text("👁")
            context.user_data["emoji_msg_id"] = sent.message_id

    elif text.lower() in ("хэлп", "help"):
        if help_file.exists():
            try:
                with open(help_file, encoding="utf-8") as f:
                    help_data = json.load(f)

                help_text = (
                                help_data.get("helpRu") if text.lower() == "хэлп"
                                else help_data.get("helpEng")
                            ) or "упс, нет записи в инструкции..."
            except Exception as e:
                help_text = f"⚠️ Ошибка чтения help.json: {e}"
        else:
            help_text = "упс, инструкция не найдена..."
        await update.message.reply_text(help_text)
        meaningful_response = True

    else:
        sent = await update.message.reply_text("👁")
        context.user_data["emoji_msg_id"] = sent.message_id

    if meaningful_response:
        recent_responded.add(chat_id)

        async def clear_flag():
            await asyncio.sleep(3)
            recent_responded.discard(chat_id)

        asyncio.create_task(clear_flag())