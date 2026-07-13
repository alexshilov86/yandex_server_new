@echo off
REM Активируем виртуальное окружение
:: Активация виртуального окружения (если есть venv)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Предупреждение: папка venv не найдена. Используем системный Python.
)

:: Обновляем зависимости (если requirements.txt изменился — всё подтянется)
REM pip install -r requirements.txt

REM Запускаем Uvicorn как ASGI-приложение: server:app
REM --host 0.0.0.0 чтобы слушать все интерфейсы
REM --port 8000 — твой порт
REM --ssl-certfile и --ssl-keyfile — пути к сертификатам
REM --workers 1 — количество процессов (можно увеличить при нагрузке)

uvicorn server:app --host 0.0.0.0 --port 8000 --ssl-certfile="C:\Certbot\live\bot.globalinstore.ru\fullchain.pem" --ssl-keyfile="C:\Certbot\live\bot.globalinstore.ru\privkey.pem" --workers 1
