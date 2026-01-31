import telebot
from telebot import types
import uuid
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ===== НАСТРОЙКИ =====
TOKEN = "8542034986:AAHlph-7hJgQn_AxH2PPXhZLUPUKTkztbiI"
ADMIN_ID = 1979125261
SALON_NAME = "Nails & Style"

# ===== GOOGLE SHEETS =====
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "creds.json", SCOPE
)
client = gspread.authorize(creds)
sheet = client.open("CRM_Salon").sheet1

bot = telebot.TeleBot(TOKEN)

# временное хранилище диалогов
user_data = {}

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

# ===== ПОДБОР УСЛУГИ (КРЕАТИВ) =====
@bot.message_handler(func=lambda m: m.text == "✨ Подобрать услугу")
def choose_service(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💨 Быстро", "✨ Эффектно", "💆‍♀️ Уход")
    bot.send_message(
        message.chat.id,
        "Что для тебя важнее сегодня?",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text in ["💨 Быстро", "✨ Эффектно", "💆‍♀️ Уход"])
def recommend(message):
    recommendations = {
        "💨 Быстро": "Экспресс-маникюр (40 минут)",
        "✨ Эффектно": "Маникюр + дизайн",
        "💆‍♀️ Уход": "Маникюр + SPA уход"
    }
    service = recommendations[message.text]
    user_data[message.chat.id] = {"service": service}

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("📅 Записаться", "🔙 В меню")

    bot.send_message(
        message.chat.id,
        f"✨ Рекомендую:\n*{service}*\n\nХочешь записаться?",
        parse_mode="Markdown",
        reply_markup=kb
    )

# ===== ЗАПИСЬ (ПОШАГОВО) =====
@bot.message_handler(func=lambda m: m.text == "📅 Записаться")
def ask_name(message):
    user_data[message.chat.id] = {}
    msg = bot.send_message(message.chat.id, "Как тебя зовут?")
    bot.register_next_step_handler(msg, get_name)

def get_name(message):
    user_data[message.chat.id]["name"] = message.text
    msg = bot.send_message(message.chat.id, "Оставь номер телефона 📞")
    bot.register_next_step_handler(msg, get_phone)

def get_phone(message):
    user_data[message.chat.id]["phone"] = message.text

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Маникюр", "Стрижка", "Брови", "Макияж")
    msg = bot.send_message(message.chat.id, "Выбери услугу:", reply_markup=kb)
    bot.register_next_step_handler(msg, get_service)

def get_service(message):
    user_data[message.chat.id]["service"] = message.text
    msg = bot.send_message(message.chat.id, "На какую дату хочешь записаться? (например: 5 февраля)")
    bot.register_next_step_handler(msg, get_date)

def get_date(message):
    data = user_data[message.chat.id]

    request_id = str(uuid.uuid4())[:8]
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")

    sheet.append_row([
        request_id,
        now,
        data["name"],
        data["phone"],
        data["service"],
        message.text,
        "🟡 Новая",
        "Telegram"
    ])

    bot.send_message(
        message.chat.id,
        f"✅ Запись принята!\n\n"
        f"📌 Услуга: {data['service']}\n"
        f"📅 Дата: {message.text}\n\n"
        f"Администратор скоро свяжется с тобой 💖"
    )

    bot.send_message(
        ADMIN_ID,
        f"🆕 Новая заявка #{request_id}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Услуга: {data['service']}\n"
        f"Дата: {message.text}"
    )

# ===== АКЦИИ =====
@bot.message_handler(func=lambda m: m.text == "🔥 Акции")
def promo(message):
    bot.send_message(
        message.chat.id,
        "🔥 *Акция недели!*\nМаникюр + уход — со скидкой 💅",
        parse_mode="Markdown"
    )

# ===== ЗАПУСК =====
bot.infinity_polling()
