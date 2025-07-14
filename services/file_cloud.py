import os
import requests


def upload_to_cloud(filepath: str, api_key: str) -> str | None:
    try:
        with open(filepath, 'rb') as f:
            response = requests.post(
                'https://pixeldrain.com/api/file',
                auth=('timuzen', api_key),
                files={'file': (os.path.basename(filepath), f)},
                data={'name': os.path.basename(filepath)},
                timeout=60
            )

        if response.ok:
            file_id = response.json().get("id")
            if file_id:
                return f"https://pixeldrain.com/u/{file_id}"
            else:
                print("Ответ без ID:", response.json())
        else:
            print("Ошибка HTTP:", response.status_code, response.text)
    except Exception as e:
        print(f"Ошибка при загрузке: {e}")
    return None
