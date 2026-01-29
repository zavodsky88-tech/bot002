import telebot
from telebot import types
import json
import os

# ====== Настройки ======
TOKEN = "8542034986:AAHlph-7hJgQn_AxH2PPXhZLUPUKTkztbiI"
ADMIN_ID = 1979125261  # Ваш Telegram ID
SALON_NAME = "Салон красоты"
ADDRESS = "ул. Примерная, 1"
WORK_HOURS = "10:00–20:00"
PHONE = "+7 (999) 123-45-67"
PAY_LINK = "https://pay.qiwi.com/order/external/ВАША_СУММА"  # ссылка на оплату

bot = telebot.TeleBot(TOKEN)

# ====== Локальное хранилище заявок (JSON) ======
DB_FILE = "applications.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def save_application(app):
    with open(DB_FILE, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(app)
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)

# ====== Главное меню ======
def menu():
    m = types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.row("💇‍♀️ Услуги", "📅 Записаться")
    m.row("💰 Цены", "📍 Контакты")
    return m

# ====== Старт ======
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"💅 Добро пожаловать в {SALON_NAME}!\nВыберите пункт меню:",
        reply_markup=menu()
    )

# ====== Обработка кнопок ======
@bot.message_handler(func=lambda m: True)
def handler(message):
    if message.text == "💇‍♀️ Услуги":
        bot.send_message(message.chat.id, "Маникюр • Стрижки • Брови • Макияж")
    elif message.text == "💰 Цены":
        bot.send_message(message.chat.id, "Маникюр — от 1000 ₽\nСтрижка — от 800 ₽\nБрови — от 500 ₽")
    elif message.text == "📍 Контакты":
        bot.send_message(message.chat.id, f"{ADDRESS}\n{PHONE}\nЧасы работы: {WORK_HOURS}")
    elif message.text == "📅 Записаться":
        msg = bot.send_message(message.chat.id, "Напишите заявку в формате:\nИмя, услуга, дата, телефон")
        bot.register_next_step_handler(msg, application)
    else:
        bot.send_message(message.chat.id, "Выберите пункт из меню", reply_markup=menu())

# ====== Получение заявки ======
def application(message):
    # Формируем заявку
    app = {
        "user_id": message.chat.id,
        "text": message.text
    }
    save_application(app)

    # Отправляем пользователю ссылку на оплату
    markup = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton(text="💳 Оплатить", url=PAY_LINK)
    markup.add(pay_button)
    bot.send_message(message.chat.id, "✅ Ваша заявка принята! Оплатите, чтобы подтвердить:", reply_markup=markup)

    # Уведомляем администратора
    bot.send_message(ADMIN_ID, f"Новая заявка:\n{message.text}\nОплата через: {PAY_LINK}")

# ====== Запуск бота ======
bot.infinity_polling()
