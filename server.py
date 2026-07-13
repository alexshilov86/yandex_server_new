from fastapi import FastAPI, Request
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

@app.post("/webhook")
async def handle_post_From_webhook(request: Request):
    data = await request.json()
    logger.info(f"Получен POST запрос: {data}")
    return {"received": data}

