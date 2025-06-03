
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes
from config import TOKEN, OPERATOR_CHAT_ID
from init_db import init_db, add_application

# Отримати доступ до колекції
applications = init_db()

# Стан для опитування
FULL_NAME, PHONE, ADDRESS, TARIFF = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📡 Тарифи", "📞 Залишити заявку"], ["💳 Оплата", "📲 Контакти"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Вітаємо! Я — бот вашого інтернет-провайдера.", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📡 Тарифи":
        await update.message.reply_text("Наші тарифи:\n🔹 Базовий — 100 Мбіт/с — 150 грн/міс\n🔹 Преміум — 300 Мбіт/с — 250 грн/міс")
    elif text == "📞 Залишити заявку":
        await update.message.reply_text("Вкажіть ваше ПІБ:")
        return FULL_NAME
    elif text == "💳 Оплата":
        await update.message.reply_text("Сплатити онлайн можна тут: https://вашсайт/оплата")
    elif text == "📲 Контакти":
        await update.message.reply_text("📞 +380961234567\n🏢 вул. Шевченка, 12\n🕐 Пн-Пт 09:00-18:00")

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text
    await update.message.reply_text("Ваш номер телефону:")
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Ваша адреса підключення:")
    return ADDRESS

async def get_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text
    await update.message.reply_text("Бажаний тариф (Базовий / Преміум):")
    return TARIFF

async def get_tariff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tariff = update.message.text
    full_name = context.user_data["full_name"]
    phone = context.user_data["phone"]
    address = context.user_data["address"]
    
    add_application(full_name, phone, address, tariff)
    
    message = f"📥 Нова заявка:\n👤 {full_name}\n📞 {phone}\n🏠 {address}\n📶 Тариф: {tariff}"
    
    # Надіслати оператору
    await context.bot.send_message(chat_id=OPERATOR_CHAT_ID, text=message)
    
    await update.message.reply_text("✅ Дякуємо! Ваша заявка прийнята. Очікуйте дзвінка оператора.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Заявку скасовано.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("📞 Залишити заявку"), handle_message)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
            TARIFF: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tariff)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
