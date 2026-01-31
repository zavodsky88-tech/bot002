import telebot
from telebot import types
import uuid
import datetime

TOKEN = "8542034986:AAHlph-7hJgQn_AxH2PPXhZLUPUKTkztbiI"
ADMIN_ID = 1979125261
SALON_NAME = "Nails & Style"

bot = telebot.TeleBot(TOKEN)

# ===== ХРАНИЛИЩА =====
crm = {}
user_state = {}

# ===== МЕНЮ =====
def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✨ Подобрать услугу")
    kb.add("📅 Записаться")
    kb.add("💰 Цены", "📍 Контакты")
    return kb

# ===== СТАРТ =====
@bot.message_handler(commands=["start"])
def start(message):
    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        f"💅 Привет!\nЯ помощник салона *{SALON_NAME}*.\nПомогу записаться 💖",
        parse_mode="Markdown",
        reply_markup=main_menu()
    )

# ===== МЕНЮ =====
@bot.message_handler(func=lambda m: m.text in ["💰 Цены", "📍 Контакты"])
def info(message):
    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)

    if message.text == "💰 Цены":
        bot.send_message(message.chat.id, "Маникюр — от 1000 ₽\nСтрижка — от 800 ₽")
    else:
        bot.send_message(message.chat.id, "📍 ул. Примерная, 1\n📞 +7 999 000-00-00")

# ===== НАЧАЛО ЗАПИСИ =====
@bot.message_handler(func=lambda m: m.text == "📅 Записаться")
def booking_start(message):
    crm[message.chat.id] = {}
    user_state[message.chat.id] = "WAIT_NAME"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("❌ Отменить запись")

    bot.send_message(
        message.chat.id,
        "Как тебя зовут?",
        reply_markup=kb
    )

# ===== ОТМЕНА =====
@bot.message_handler(func=lambda m: m.text == "❌ Отменить запись")
def cancel(message):
    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        "❌ Запись отменена",
        reply_markup=main_menu()
    )

# ===== FSM =====
@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "WAIT_NAME")
def get_name(message):
    if message.text.startswith("❌"):
        return

    crm[message.chat.id]["name"] = message.text
    user_state[message.chat.id] = "WAIT_PHONE"

    bot.send_message(message.chat.id, "Оставь номер телефона 📞")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "WAIT_PHONE")
def get_phone(message):
    crm[message.chat.id]["phone"] = message.text
    user_state[message.chat.id] = "WAIT_SERVICE"

    bot.send_message(message.chat.id, "Какую услугу выбираешь?")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "WAIT_SERVICE")
def get_service(message):
    crm[message.chat.id]["service"] = message.text
    user_state[message.chat.id] = "WAIT_DATE"

    bot.send_message(message.chat.id, "На какую дату хочешь записаться?")

@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "WAIT_DATE")
def get_date(message):
    data = crm[message.chat.id]

    request_id = str(uuid.uuid4())[:8]
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    print({
        "id": request_id,
        "date": now,
        **data,
        "visit_date": message.text,
        "status": "Новая"
    })

    bot.send_message(
        message.chat.id,
        "✅ Запись принята!\nАдминистратор скоро свяжется с тобой 💖",
        reply_markup=main_menu()
    )

    bot.send_message(
        ADMIN_ID,
        f"🆕 Заявка #{request_id}\n"
        f"{data['name']} | {data['phone']}\n"
        f"{data['service']} | {message.text}"
    )

    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)

bot.infinity_polling()
