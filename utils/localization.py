
from database.db import get_user_language
from texts import texts

def get_text(user_id, key):
    lang = get_user_language(user_id)
    return texts.get(key, {}).get(lang, texts.get(key, {}).get("ru", ""))
