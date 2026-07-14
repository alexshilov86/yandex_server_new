import os
import json
from datetime import datetime, timezone
from typing import Dict, List
import gspread
from gspread.utils import ValueRenderOption
from google.oauth2.service_account import Credentials
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging
from logger_config import init_logger
from dotenv import load_dotenv

load_dotenv()
init_logger()
logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=3)


def update_data_from_base() -> bool:
    service_account_path = os.getenv("GSPREAD_SERVICE_ACCOUNT_JSON")
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    local_data_file = os.getenv("LOCAL_DATA_FILE", "base_data.json")
    update_info_file = os.getenv("UPDATE_INFO_FILE", "update_base_info.json")

    if not all([service_account_path, sheet_id]):
        logger.error("Не заданы GSPREAD_SERVICE_ACCOUNT_JSON или GOOGLE_SHEET_ID в .env")
        return False

    try:
        with open(service_account_path, "r", encoding="utf-8") as f:
            creds_data = json.load(f)
    except Exception as e:
        logger.error("Ошибка чтения сервисного аккаунта: %s", e)
        return False

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(creds_data, scopes=scopes)
    gc = gspread.authorize(creds)

    try:
        spreadsheet = gc.open_by_key(sheet_id)
    except gspread.exceptions.SpreadsheetNotFound:
        logger.error("Таблица не найдена: %s", sheet_id)
        return False
    except Exception as e:
        logger.error("Ошибка при открытии таблицы: %s", e)
        return False

    # Явно берём 4 листа по именам
    sheet_names = ["Отгружено", "Контрольный диапазон", "Готовится к отгрузке", "Заявки"]
    worksheets: Dict[str, gspread.Worksheet] = {}
    for name in sheet_names:
        try:
            ws = spreadsheet.worksheet(name)
            worksheets[name] = ws
        except gspread.exceptions.WorksheetNotFound:
            logger.error("Лист не найден: '%s'", name)
            return False
        except Exception as e:
            logger.error("Ошибка получения листа '%s': %s", name, e)
            return False

    all_data: Dict[str, dict] = {}
    sheets_stats = []

    for sheet_name, ws in worksheets.items():
        try:
            all_values = ws.get_all_values(
                value_render_option=ValueRenderOption.unformatted
            )
        except Exception as e:
            logger.error("Ошибка get_all_values для листа '%s': %s", sheet_name, e)
            return False

        if not all_values:
            # Пустой лист
            all_data[sheet_name] = {
                "headers": [],
                "rows": []
            }
            stats = {
                "sheet_name": sheet_name,
                "total_rows": 0,
                "columns_count": 0,
            }
            sheets_stats.append(stats)
            logger.warning("Лист '%s' пустой", sheet_name)
            continue

        # ВАЖНО: игнорируем реальную шапку из таблицы
        # Вместо этого генерируем column1, column2, ...
        real_headers = all_values[0]
        data_rows = all_values[1:]

        n_cols = len(real_headers)
        generated_headers = [f"column{i+1}" for i in range(n_cols)]

        all_data[sheet_name] = {
            "headers": generated_headers,      # column1, column2, ...
            "rows": data_rows,                  # список списков значений
            "original_headers": real_headers   # сохраняем «как было» для отладки
        }

        stats = {
            "sheet_name": sheet_name,
            "total_rows": len(data_rows),
            "columns_count": n_cols,
        }
        sheets_stats.append(stats)

        # logger.info(
        #     "Лист '%s': %d строк, %d колонок",
        #     sheet_name, len(data_rows), n_cols
        # )

    total_rows = sum(s["total_rows"] for s in sheets_stats)
    # logger.info("Всего скачано строк по всем листам: %d", total_rows)

    # Сохраняем данные
    try:
        with open(local_data_file, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logger.info("Локальная база обновлена: %s", local_data_file)
    except Exception as e:
        logger.error("Ошибка записи локальной базы: %s", e)
        return False

    # Пишем метаданные
    now_iso = datetime.now(timezone.utc).isoformat()
    info = {
        "last_updated_utc": now_iso,
        "total_rows": total_rows,
        "sheets": sheets_stats,
        "sheet_id": sheet_id,
    }
    try:
        with open(update_info_file, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        # logger.info("Информация об обновлении записана: %s", update_info_file)
    except Exception as e:
        logger.error("Ошибка записи update_base_info: %s", e)
        return False

    return True
