import telebot
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN:
    raise Exception("TOKEN не задан")

if not ADMIN_ID:
    raise Exception("ADMIN_ID не задан")

ADMIN_ID = int(ADMIN_ID)

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "🤖 Бот запущен и работает!"
    )

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.send_message(message.chat.id, "Сообщение получено ✅")
    bot.send_message(ADMIN_ID, f"Новое сообщение:\n{message.text}")

bot.infinity_polling()
