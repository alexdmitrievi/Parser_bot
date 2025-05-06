import os
import requests
from shared.parser import parse_documents

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_file_url(file_id):
    r = requests.get(f"{API_URL}/getFile?file_id={file_id}")
    file_path = r.json()["result"]["file_path"]
    return f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

def process_document(file_id, chat_id):
    url = get_file_url(file_id)
    content = requests.get(url).content
    parsed_data = parse_documents(content)
    requests.post(f"{API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": f"Файл обработан. Найдено: {parsed_data}"
    })
