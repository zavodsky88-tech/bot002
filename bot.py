import telebot
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

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
