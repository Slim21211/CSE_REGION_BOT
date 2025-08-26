import os
import sys
import logging
from flask import Flask, request
import telebot

# Добавляем путь к botr.py
botr_path = '/home/CSEREGION2022/CSE REGION BOT'
if botr_path not in sys.path:
    sys.path.insert(0, botr_path)

# Получаем токен из переменной окружения
telegram_bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
if not telegram_bot_token:
    raise Exception("TELEGRAM_BOT_TOKEN not found in environment variables!")

# Инициализируем бота и Flask-приложение
bot = telebot.TeleBot(telegram_bot_token, threaded=False, parse_mode='HTML')
app = Flask(__name__)

# Вебхук-обработчик
@app.route('/' + telegram_bot_token, methods=['POST'])
def webhook():
    logging.info(">>> Webhook triggered")
    data = request.get_data(as_text=True)
    logging.info(f">>> Incoming update:\n{data}")
    try:
        update = telebot.types.Update.de_json(data)
        bot.process_new_updates([update])
    except Exception as e:
        logging.error(f">>> Error while processing update: {e}")
    return 'ok', 200

# Стартовая страница
@app.route('/')
def index():
    return 'Webhook running!', 200

# Импорт обработчиков
from botr import *

if __name__ == '__main__':
    app.run()
