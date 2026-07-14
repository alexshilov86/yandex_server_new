from download_google_table_json import update_data_from_base
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    success = update_data_from_base()
    if success:
        print("✅ Данные успешно обновлены")
    else:
        print("❌ Ошибка при обновлении данных")