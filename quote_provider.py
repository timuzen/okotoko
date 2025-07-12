import requests

def get_quote():
    url = "http://api.forismatic.com/api/1.0/"
    params = {"method": "getQuote", "format": "json", "lang": "ru"}
    try:
        response = requests.post(url, data=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quote = data.get("quoteText", "").strip()
            author = data.get("quoteAuthor", "").strip() or "неизвестен"
            return quote, author
        return "Ошибка при получении цитаты.", "неизвестен"
    except requests.RequestException:
        return "Ошибка соединения с API.", "неизвестен"
