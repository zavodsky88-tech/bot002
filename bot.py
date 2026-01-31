import telebot
from telebot import types
import uuid
import datetime

TOKEN = "8542034986:AAHlph-7hJgQn_AxH2PPXhZLUPUKTkztbiI"
ADMIN_ID = 1979125261
SALON_NAME = "Nails & Style"

bot = telebot.TeleBot(TOKEN)

# Простая CRM в памяти (можно заменить на БД)
crm = {}

# ===== СТАРТ =====
@bot.message_handler(commands=["start"])
def start(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("✨ Подобрать услугу")
    kb.add("📅 Записаться", "🔥 Акции")

    bot.send_message(
        message.chat.id,
        f"💅 Привет!\nЯ помощник салона *{SALON_NAME}*.\nПомогу выбрать услугу и записаться 💖",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ===== ПОДБОР УСЛУГИ =====
@bot.message_handler(func=lambda m: m.text == "✨ Подобрать услугу")
def choose_service(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💨 Быстро", "✨ Эффектно", "💆‍♀️ Уход")
    bot.send_message(message.chat.id, "Что для тебя важнее сегодня?", reply_markup=kb)

@bot.message_handler(func=lambda m: m.text in ["💨 Быстро", "✨ Эффектно", "💆‍♀️ Уход"])
def recommend(message):
    recommendations = {
        "💨 Быстро": "Экспресс-маникюр",
        "✨ Эффектно": "Маникюр + дизайн",
        "💆‍♀️ Уход": "Маникюр + SPA"
    }
    service = recommendations[message.text]
    crm[message.chat.id] = {"service": service}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📅 Записаться", "🔙 В меню")

    bot.send_message(
        message.chat.id,
        f"✨ Рекомендую:\n*{service}*\n\nХочешь записаться?",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ===== ЗАПИСЬ =====
@bot.message_handler(func=lambda m: m.text == "📅 Записаться")
def ask_name(message):
    crm[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    crm[message.chat.id]["name"] = message.text
    msg = bot.send_message(message.chat.id, "Оставь номер телефона 📞")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(message):
    crm[message.chat.id]["phone"] = message.text
    msg = bot.send_message(message.chat.id, "Какую услугу выбираешь?")
    bot.register_next_step_handler(msg, get_service)

def get_service(message):
    crm[message.chat.id]["service"] = message.text
    msg = bot.send_message(message.chat.id, "На какую дату хочешь записаться?")
    bot.register_next_step_handler(msg, get_date)

def get_date(message):
    data = crm[message.chat.id]
    request_id = str(uuid.uuid4())[:8]
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    # Лог в консоль (Railway Logs = CRM)
    print({
        "id": request_id,
        "date": now,
        "name": data["name"],
        "phone": data["phone"],
        "service": data["service"],
        "visit_date": message.text,
        "status": "Новая"
    })

    bot.send_message(
        message.chat.id,
        "✅ Запись принята!\nАдминистратор скоро свяжется с тобой 💖"
    )

    bot.send_message(
        ADMIN_ID,
        f"🆕 Заявка #{request_id}\n"
        f"{data['name']} | {data['phone']}\n"
        f"{data['service']} | {message.text}"
    )

# ===== АКЦИИ =====
@bot.message_handler(func=lambda m: m.text == "🔥 Акции")
def promo(message):
    bot.send_message(
        message.chat.id,
        "🔥 Акция недели!\nМаникюр + уход со скидкой 💅"
    )

bot.infinity_polling()
