import os
import time
import threading
import requests
import schedule
import logging

PIXELDRAIN_API_URL = 'https://pixeldrain.com/api'
API_KEY = os.getenv("PIXELDRAIN_API_KEY")

logger = logging.getLogger(__name__)

def keep_alive_api_key(api_key: str) -> bool:
    try:
        response = requests.get(
            f'{PIXELDRAIN_API_URL}/user',
            auth=('timuzen', api_key),
            timeout=10
        )
        if response.ok:
            logger.info("✅ API-ключ активен (keep-alive)")
            return True
        else:
            logger.warning(f"⚠️ Ключ недействителен: {response.status_code} {response.text}")
    except Exception as e:
        logger.error(f"❌ Ошибка при keep-alive запросе: {e}")
    return False


def upload_to_cloud(filepath: str, api_key: str) -> str | None:

    try:
        with open(filepath, 'rb') as f:
            response = requests.post(
                f'{PIXELDRAIN_API_URL}/file',
                auth=('timuzen', api_key),
                files={'file': (os.path.basename(filepath), f)},
                data={'name': os.path.basename(filepath)},
                timeout=(10, 180)
            )

        try:
            json_data = response.json()
        except ValueError:
            logger.error("❌ Ответ не является JSON — возможно, HTML-ошибка")
            logger.debug(f"Raw response: {response.text}")
            return None

        if response.ok:
            file_id = json_data.get("id")
            if file_id:
                url = f"https://pixeldrain.com/u/{file_id}"
                logger.info(f"✅ Файл успешно загружен: {url}")
                return url
            else:
                logger.warning(f"⚠️ Успешный ответ без ID: {json_data}")
        else:
            logger.error(f"❌ Ошибка HTTP: {response.status_code} {response.text}")

    except requests.exceptions.Timeout:
        logger.error("⏱️ Таймаут при загрузке файла.")
    except requests.exceptions.RequestException as e:
        logger.error(f"📡 Ошибка сети: {e}")
    except Exception as e:
        logger.exception(f"❌ Непредвиденная ошибка при загрузке файла: {e}")

    return None


def start_keep_alive_scheduler():
    if not API_KEY:
        logger.warning("⚠️ API_KEY не задан — планировщик keep-alive не запущен")
        return

    def _wrapped_keep_alive():
        logger.info("🔁 Keep-alive запрос к PixelDrain...")
        success = keep_alive_api_key(API_KEY)
        if success:
            logger.info("✅ Keep-alive успешен")
        else:
            logger.warning("❌ Keep-alive провален")

    schedule.every(7).days.at("03:00").do(_wrapped_keep_alive)
    logger.info("🕒 Планировщик keep-alive запущен: каждые 7 дней в 03:00")

    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)

    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()
