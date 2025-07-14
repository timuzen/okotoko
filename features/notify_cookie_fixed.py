from features import get_registered_chat_ids, unregister_chat_id
from telegram import Bot
import logging

logger = logging.getLogger(__name__)

async def notify_cookie_fixed(bot: Bot):
    try:
        chat_ids = get_registered_chat_ids()
    except Exception as e:
        logger.error(f"❌ Не удалось получить chat_id из Redis: {e}")
        return

    if not chat_ids:
        logger.info("🔕 Нет пользователей, ожидающих печеньку")
        return

    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="ютубчик снова в деле\nможешь кидать ссылку"
            )
            unregister_chat_id(chat_id)
            logger.info(f"✅ Уведомлен chat_id {chat_id} и удалён из Redis")
        except Exception as e:
            logger.warning(f"⚠️ Ошибка отправки chat_id {chat_id}: {e}")
