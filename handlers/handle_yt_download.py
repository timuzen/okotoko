import os
import glob
import yt_dlp
import asyncio
from telegram import Update, Bot
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from dotenv import load_dotenv
from features import upload_to_cloud, register_chat_id

load_dotenv()

MAX_SIZE_MB = 50
PIXELDRAIN_API_KEY = os.getenv("PIXELDRAIN_API_KEY")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


def cleanup_files():
    for ext in ('*.m4a', '*.mp3', '*.webm', '*.opus', '*.wav'):
        for f in glob.glob(ext):
            try:
                os.remove(f)
            except Exception:
                pass



async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.RECORD_VOICE)

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'youtube_include_dash_manifest': False,
        'force_generic_extractor': False,
        'source_address': '0.0.0.0',
        'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'},
        'cookiefile': '/tmp/cookies.txt',
        'socket_timeout': 60,
        'retries': 10,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info = ydl.extract_info(url, download=False)

        m4a_files = sorted(glob.glob("*.m4a"), key=os.path.getmtime, reverse=True)
        if not m4a_files:
            raise FileNotFoundError("Упс! файл исчез...")

        filename = m4a_files[0]
        file_size_mb = os.path.getsize(filename) / (1024 * 1024)
        title = os.path.splitext(filename)[0]

        if file_size_mb > MAX_SIZE_MB:
            await update.message.reply_text(f"{round(file_size_mb, 2)}МБ - не влезает в телегу")
            await asyncio.sleep(2)
            await update.message.reply_text("ща скину ссылку на облако...")

            loop = asyncio.get_event_loop()
            upload_task = loop.run_in_executor(None, upload_to_cloud, filename, PIXELDRAIN_API_KEY)

            await asyncio.sleep(2)

            link = await upload_task
            if link:
                await update.message.reply_text(f"!{link}")
            else:
                await update.message.reply_text("Упс! не загрузилось...")
        else:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
            with open(filename, 'rb') as audio_file:
                await update.message.reply_audio(audio=audio_file, title=title)

    except Exception as e:
        error_message = str(e)

        bot: Bot = context.bot
        chat_id = update.effective_chat.id
        username = update.effective_user.username or 'неизвестный'

        if "Sign in to confirm you’re not a bot" in error_message:
            await update.message.reply_text("упс, нужна печенька для работы")
            await asyncio.sleep(3)
            await update.message.reply_text("ща напишу админу")
            await asyncio.sleep(3)
            await update.message.reply_text("как поправит, отпишусь")

            register_chat_id(chat_id)

            # notify admin
            await bot.send_message(
                chat_id=ADMIN_ID,
                text=f"@{username} просит скормить печеньку")
        else:
            await update.message.reply_text(f"Упс!:\n\n{error_message}")
    finally:
        cleanup_files()
