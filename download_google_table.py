import os
import time
import json
import re
import httpx, asyncio
import pandas as pd
from dotenv import load_dotenv

# НАСТРОЙКИ
load_dotenv()
# НАСТРОЙКИ
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")  # Замените на реальный ID вашей таблицы
SHEETS = ["Отгружено", "Контрольный диапазон", "Готовится к отгрузке", "Заявки"]  # Названия листов

def make_columns_unique(columns):
    """Вспомогательная функция, которая делает имена колонок уникальными."""
    seen = {}
    new_columns = []
    for col in columns:
        # Если имя пустое, даем ему техническое название
        if not col or col.strip() == "":
            col = "Unnamed_Col"
            
        if col in seen:
            seen[col] += 1
            new_columns.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_columns.append(col)
    return new_columns

async def update_data_from_base():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Начало скачивания СЫРЫХ данных...")

    async with httpx.AsyncClient(timeout=45.0) as client:
        for sheet in SHEETS:
            # Запрашиваем формат out:json вместо out:csv
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:json&sheet={sheet}"

            temp_file = f"{sheet}_temp.feather"
            final_file = f"{sheet}.feather"

            try:
                response = await client.get(url)
                response.raise_for_status()

                # Google возвращает JSON, обернутый в функцию google.visualization.Query.setResponse(...)
                # Очищаем текст, чтобы остался только чистый JSON
                raw_text = response.text
                json_clean = re.search(r"google\.visualization\.Query\.setResponse\((.*?)\);", raw_text, re.DOTALL)
                
                if not json_clean:
                    raise ValueError("Не удалось распарсить ответ от Google API")
                
                data = json.loads(json_clean.group(1))

                # Извлекаем заголовки колонок
                columns = [col.get('label', f'Col_{i}') for i, col in enumerate(data['table']['cols'])]

                # Применяем исправление дубликатов названий колонок
                unique_columns = make_columns_unique(columns)

                # Собираем строки, вытаскивая СЫРЫЕ значения из поля 'v'
                rows = []
                for row_data in data['table']['rows']:
                    row = []
                    for cell in row_data['c']:
                        # Если ячейка не пустая, берем сырое значение 'v', иначе None
                        val = cell.get('v') if cell else None
                        row.append(val)
                    rows.append(row)

                # Создаем DataFrame
                df = pd.DataFrame(rows, columns=unique_columns)

                # Сохраняем в бинарный feather
                df.to_feather(temp_file)

                if os.path.exists(temp_file):
                    os.replace(temp_file, final_file)
                    print(f"  Лист '{sheet}' (сырые данные) успешно обновлен.")

            except Exception as e:
                print(f"❌ Ошибка при обновлении листа '{sheet}': {e}.")
                if os.path.exists(temp_file):
                    os.remove(temp_file)

# Этот блок выполнится, только если вы запускаете файл напрямую
if __name__ == "__main__":
    print("Запуск тестового скачивания таблицы...")
    
    # asyncio.run создает событие (event loop) и выполняет асинхронную функцию
    asyncio.run(update_data_from_base())


