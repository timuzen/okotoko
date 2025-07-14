import requests

def get_quote(lang="ru"):
    url = "http://api.forismatic.com/api/1.0/"
    params = {"method": "getQuote", "format": "json", "lang": lang}
    try:
        response = requests.post(url, data=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            quote = data.get("quoteText", "").strip()
            author = data.get("quoteAuthor", "").strip() or (
                "неизвестен" if lang == "ru" else "unknown"
            )
            if quote:
                return quote, author
            else:
                msg = "Упс! Цитата пуста..." if lang == "ru" else "Oops! Quote is empty..."
                return msg, None
        else:
            msg = "Упс! Цитата пуста..." if lang == "ru" else "Oops! Quote is empty..."
            return msg, None
    except requests.RequestException:
        msg = "Не могу открыть цитатник..." if lang == "ru" else "Can't reach the quote book..."
        return msg, None
