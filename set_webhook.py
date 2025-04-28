import telebot
from decouple import config

TOKEN = config('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = config('WEBHOOK_URL')
WEBHOOK_SECRET_TOKEN = config('WEBHOOK_SECRET_TOKEN')

bot = telebot.TeleBot(TOKEN)

bot.remove_webhook()
response = bot.set_webhook(url=WEBHOOK_URL, secret_token=WEBHOOK_SECRET_TOKEN)
if response:
    print("Webhook установлен успешно")
else:
    print("Не удалось установить webhook")
