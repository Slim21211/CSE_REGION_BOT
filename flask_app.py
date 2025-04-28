from flask import Flask, request
import telebot
from decouple import config
import botr

app = Flask(__name__)

bot = botr.bot

WEBHOOK_SECRET_TOKEN = config('WEBHOOK_SECRET_TOKEN')
WEBHOOK_PATH = config('WEBHOOK_PATH')


@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('X-Telegram-Bot-Api-Secret-Token') == WEBHOOK_SECRET_TOKEN:
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Invalid secret token', 403


if __name__ == "__main__":
    app.run(host="0.0.0.0")

