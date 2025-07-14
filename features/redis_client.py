import redis
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# logging
logging.basicConfig(level=logging.INFO, force=True)
logger = logging.getLogger(__name__)

# Connect to Redis
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError("REDIS_URL не задан")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

# set template
ERROR_USER_SET = "error:users:need_cookie"

# ping redis
def ping_redis():
    try:
        redis_client.ping()
        logger.info("✅ Redis доступен")
        return True
    except redis.exceptions.RedisError as e:
        logger.error(f"❌ Redis недоступен: {e}")
        return False

# adding chat_id
def register_chat_id(chat_id: int) -> bool:
    result = redis_client.sadd(ERROR_USER_SET, chat_id)
    if result == 1:
        logger.info(f"🔹 chat_id {chat_id} добавлен в {ERROR_USER_SET}")
        return True
    else:
        logger.info(f"🔁 chat_id {chat_id} уже существует в {ERROR_USER_SET}")
        return False

# get all chat_id
def get_registered_chat_ids() -> set:
    chat_ids = redis_client.smembers(ERROR_USER_SET)
    logger.info(f"📋 Список chat_id в {ERROR_USER_SET}: {chat_ids}")
    return chat_ids

# delete chat_id
def unregister_chat_id(chat_id: int) -> bool:
    result = redis_client.srem(ERROR_USER_SET, chat_id)
    if result == 1:
        logger.info(f"🗑️ chat_id {chat_id} удалён из {ERROR_USER_SET}")
        return True
    else:
        logger.info(f"ℹ️ chat_id {chat_id} не найден в {ERROR_USER_SET}")
        return False

# clear
def clear_all_chat_ids():
    redis_client.delete(ERROR_USER_SET)
    logger.info(f"♻️ Очищено множество {ERROR_USER_SET}")
