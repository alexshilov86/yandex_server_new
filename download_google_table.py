import os
import time
from io import StringIO
import httpx
import pandas as pd
from dotenv import load_dotenv
# Импортируем инструменты авторизации Google
from google.oauth2 import service_account
import google.auth.transport.requests
import asyncio
load_dotenv()

# НАСТРОЙКИ
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEETS = ["Отгружено", "Контрольный диапазон", "Готовится к отгрузке", "Заявки"]
# Путь к вашему JSON-файлу сервисного аккаунта
CREDENTIALS_FILE = os.getenv("GSPREAD_SERVICE_ACCOUNT_JSON") 


async def update_data_from_base():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Авторизация и запуск обновления...")
    
    try:
        # 1. Загружаем сервисный аккаунт и запрашиваем доступ (Scope) к таблицам
        scopes = ['https://googleapis.com']
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=scopes
        )
        
        # Подготавливаем авторизационный токен (Google OAuth2)
        # Получаем валидные заголовки (Headers) для HTTP-запроса
        auth_request = google.auth.transport.requests.Request()
        creds.refresh(auth_request)
        headers = {"Authorization": f"Bearer {creds.token}"}
        
    except Exception as auth_error:
        print(f"❌ Ошибка авторизации Google: {auth_error}")
        return

    # 2. Скачиваем данные с использованием авторизации
    async with httpx.AsyncClient(timeout=45.0, headers=headers) as client:
        for sheet in SHEETS:
            url = f"https://google.com{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet}"
            
            temp_file = f"{sheet}_temp.feather"
            final_file = f"{sheet}.feather"

            try:
                # Отправляем запрос вместе с токеном в headers
                response = await client.get(url)
                response.raise_for_status()

                df = pd.read_csv(StringIO(response.text))
                df.to_feather(temp_file)

                if os.path.exists(temp_file):
                    os.replace(temp_file, final_file)
                    print(f"  Лист '{sheet}' успешно обновлен.")

            except Exception as e:
                print(f"❌ Ошибка при обновлении листа '{sheet}': {e}. Оставлена прошлая версия.")
                if os.path.exists(temp_file):
                    os.remove(temp_file)

# Этот блок выполнится, только если вы запускаете файл напрямую
if __name__ == "__main__":
    print("Запуск тестового скачивания таблицы...")
    
    # asyncio.run создает событие (event loop) и выполняет асинхронную функцию
    asyncio.run(update_data_from_base())