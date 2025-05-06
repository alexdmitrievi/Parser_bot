from fastapi import FastAPI, Request
import os
import requests
import logging
from redis import Redis
from rq import Queue
from shared.parser import parse_documents

app = FastAPI()
q = Queue(connection=Redis.from_url(os.getenv("REDIS_URL")))
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@app.get("/ping")
def ping():
    return {"pong": True}

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text")

    if text == "/start" or text == "🔄 Перезапустить бота":
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": "Бот перезапущен. Отправьте инвойс и TIR/CMR для обработки.",
                    "reply_markup": {
                        "keyboard": [[{"text": "🔄 Перезапустить бота"}]],
                        "resize_keyboard": True,
                        "one_time_keyboard": False
                    }
                }
            )
            logging.info(f"Telegram ответ: {resp.status_code} - {resp.text}")
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения: {e}")
        return {"ok": True}

    doc = message.get("document")
    if doc:
        file_id = doc["file_id"]
        q.enqueue("worker.worker.process_document", file_id, chat_id)
        return {"status": "queued"}

    return {"status": "ignored"}


