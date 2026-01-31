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

# ===== ПОДБОР УСЛУГИ =====
@bot.message_handler(func=lambda m: m.text == "✨ Подобрать услугу")
def choose_service(message):
    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💨 Быстро", "✨ Эффектно", "💆‍♀️ Уход")
    kb.add("🔙 В меню")

    bot.send_message(
        message.chat.id,
        "Окей 😊\nЧто для тебя важнее сегодня?",
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: m.text in ["💨 Быстро", "✨ Эффектно", "💆‍♀️ Уход"])
def recommend_service(message):
    recommendations = {
        "💨 Быстро": "Экспресс-маникюр (40 минут)",
        "✨ Эффектно": "Маникюр + дизайн",
        "💆‍♀️ Уход": "Маникюр + SPA-уход"
    }

    service = recommendations[message.text]

    crm[message.chat.id] = {"service": service}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📅 Записаться")
    kb.add("🔙 В меню")

    bot.send_message(
        message.chat.id,
        f"✨ Рекомендую:\n*{service}*\n\nХочешь записаться?",
        parse_mode="Markdown",
        reply_markup=kb
    )



@bot.message_handler(func=lambda m: m.text == "🔙 В меню")
def back_to_menu(message):
    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)

    bot.send_message(
        message.chat.id,
        "Ок, возвращаемся в меню 👇",
        reply_markup=main_menu()
    )


# ===== НАЧАЛО ЗАПИСИ =====
@bot.message_handler(func=lambda m: m.text == "📅 Записаться")
def booking_start(message):
    crm.setdefault(message.chat.id, {})
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
    phone = message.text.strip()

    if not phone.isdigit() or len(phone) < 10:
        bot.send_message(
            message.chat.id,
            "📞 Напиши номер телефона цифрами\nНапример: 89529932098"
        )
        return

    crm.setdefault(message.chat.id, {})
    crm[message.chat.id]["phone"] = phone

    user_state[message.chat.id] = "WAIT_DATE"
    bot.send_message(
        message.chat.id,
        "На какую дату хочешь записаться? (например: 5 февраля)"
    )


@bot.message_handler(func=lambda m: user_state.get(m.chat.id) == "WAIT_DATE")
def get_date(message):
    text = message.text.strip()

    if len(text) < 3:
        bot.send_message(
            message.chat.id,
            "📅 Напиши дату нормально 😊 Например: 6 июня"
        )
        return

    data = crm.get(message.chat.id, {})

    request_id = str(uuid.uuid4())[:8]

    bot.send_message(
        message.chat.id,
        "✅ Запись принята!\nАдминистратор скоро свяжется с тобой 💖",
        reply_markup=main_menu()
    )

    bot.send_message(
        ADMIN_ID,
        f"🆕 Заявка #{request_id}\n"
        f"{data.get('name')} | {data.get('phone')}\n"
        f"{data.get('service')}\n"
        f"Дата: {text}"
    )

    # ❗ важно
    user_state.pop(message.chat.id, None)
    crm.pop(message.chat.id, None)


bot.infinity_polling()
