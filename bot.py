import telebot

# ====== ВАШИ НАСТРОЙКИ ======
TOKEN = "8542034986:AAHlph-7hJgQn_AxH2PPXhZLUPUKTkztbiI"  # вставьте токен, который получите у BotFather
ADMIN_ID = 1979125261      # вставьте свой Telegram ID, куда будут приходить заявки

bot = telebot.TeleBot(TOKEN)

# ====== ДАННЫЕ САЛОНА ======
SALON_NAME = "Салон красоты 'Люкс'"
ADDRESS = "г. Москва, ул. Примерная, 10"
WORK_HOURS = "Пн-Сб 10:00–20:00"
PHONE = "+7 900 123-45-67"

SERVICES = {
    "Маникюр / Педикюр": ["Классический", "Аппаратный", "С покрытием", "Дизайн"],
    "Парикмахерские услуги": ["Стрижка", "Окрашивание", "Укладка"],
    "Брови / Ресницы": ["Коррекция бровей", "Наращивание ресниц"],
    "Косметология": ["Чистка лица", "Массаж лица"]
}

PRICES = {
    "Маникюр / Педикюр": "от 1000 ₽",
    "Парикмахерские услуги": "от 1500 ₽",
    "Брови / Ресницы": "от 500 ₽",
    "Косметология": "от 2000 ₽"
}

# ====== МЕНЮ ======
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💇‍♀️ Услуги", "💰 Цены")
    markup.row("📅 Записаться", "❓ Вопросы")
    markup.row("📍 Контакты")
    return markup

# ====== СТАРТ ======
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"💅 Добро пожаловать в {SALON_NAME}!\nЯ помогу узнать услуги, цены и записаться.",
        reply_markup=main_menu()
    )

# ====== МЕНЮ ======
@bot.message_handler(func=lambda message: True)
def menu(message):
    text = message.text

    if text == "💇‍♀️ Услуги":
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for service in SERVICES.keys():
            markup.row(service)
        markup.row("🔙 Назад")
        bot.send_message(message.chat.id, "Выберите услугу:", reply_markup=markup)

    elif text in SERVICES:
        bot.send_message(message.chat.id, f"{text} включает:\n- " + "\n- ".join(SERVICES[text]))
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📅 Записаться", "🔙 Назад")
        bot.send_message(message.chat.id, "Хотите записаться?", reply_markup=markup)

    elif text == "💰 Цены":
        prices_text = "\n".join([f"{k}: {v}" for k,v in PRICES.items()])
        bot.send_message(message.chat.id, f"💰 Наши цены:\n{prices_text}")

    elif text == "📅 Записаться":
        bot.send_message(message.chat.id, "Отправьте данные в формате:\nИмя, Услуга, Дата/Время, Телефон")
        bot.register_next_step_handler(message, collect_application)

    elif text == "❓ Вопросы":
        bot.send_message(message.chat.id, "Выберите вопрос:\n1. Где находимся?\n2. Время работы?\n3. Контакты")
        bot.register_next_step_handler(message, faq_handler)

    elif text == "📍 Контакты":
        bot.send_message(message.chat.id, f"📍 Адрес: {ADDRESS}\n⏰ Время работы: {WORK_HOURS}\n📞 Телефон: {PHONE}")

    elif text == "🔙 Назад":
        bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())

    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте меню.")

# ====== СОБИРАЕМ ЗАЯВКУ ======
def collect_application(message):
    application = message.text
    bot.send_message(message.chat.id, "✅ Спасибо! Заявка отправлена. Мы свяжемся с вами.")
    bot.send_message(ADMIN_ID, f"Новая заявка:\n{application}")

# ====== FAQ ======
def faq_handler(message):
    text = message.text.lower()
    if "1" in text or "где" in text:
        bot.send_message(message.chat.id, f"Мы находимся по адресу: {ADDRESS}")
    elif "2" in text or "время" in text:
        bot.send_message(message.chat.id, f"Время работы: {WORK_HOURS}")
    elif "3" in text or "контакты" in text:
        bot.send_message(message.chat.id, f"Телефон: {PHONE}")
    else:
        bot.send_message(message.chat.id, "Выберите вариант из списка.")
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())

# ====== ЗАПУСК ======
bot.infinity_polling()
