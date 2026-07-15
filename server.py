from fastapi import FastAPI, Request, HTTPException
from logger_config import init_logger
import logging


init_logger()
logger = logging.getLogger(__name__)
logger.info ("Запуск сервера")

app = FastAPI()

def text_handler(data: dict):
    """Обработчик текстовых сообщений (update1)"""
    text = data.get('text', '')
    user = data.get('from', {})
    user_name = user.get('display_name', 'Unknown')
    
    logger.info(f"📝 Текстовое сообщение от {user_name}: {text}")
    
    # Здесь ваша логика обработки текста
    logger.info ({"handler": "text_handler", "text": text})

def button_handler(data: dict):
    """Обработчик нажатий кнопок (update2)"""
    bot_request = data.get('bot_request', {})
    server_action = bot_request.get('server_action', {})
    action_name = server_action.get('name', 'unknown')
    payload = server_action.get('payload', {})
    
    logger.info(f"🔘 Нажата кнопка: {action_name}, payload: {payload}")
    
    # Здесь ваша логика обработки кнопок
    logger.info ({"handler": "button_handler", "action": action_name})

@app.post("/webhook")
async def webhook(request: Request):
    try:
        # Получаем данные
        data = await request.json()
        logger.info(f"Получен запрос: {data}")
        
        # Проверяем наличие updates
        updates = data.get('updates', [])
        if not updates:
            raise HTTPException(status_code=400, detail="No updates field")
        
        # Берем первый update
        update = updates[0]
        
        # Определяем тип по наличию полей
        if 'bot_request' in update:
            # Это нажатие кнопки (update2)
            result = button_handler(update)
        elif 'text' in update:
            # Это текстовое сообщение (update1)
            result = text_handler(update)
        else:
            # Неизвестный тип
            print("⚠️ Неизвестный тип update")
            result = {"status": "unknown_type"}
        
        return {
            "status": "ok",
            "handler": result.get("handler"),
            "processed": True
        }
        
    except Exception as e:
        logger.info(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

