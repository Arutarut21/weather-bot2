# main.py содержимое (укорочено для читаемости)
import os, random, requests
from datetime import datetime
from pytz import timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

USERS = [{"name": "Женя", "city": "Warsaw", "timezone": "Europe/Warsaw", "chat_id": None},
         {"name": "Никита", "city": "Warsaw", "timezone": "Europe/Warsaw", "chat_id": None},
         {"name": "Рома", "city": "Rivne", "timezone": "Europe/Kyiv", "chat_id": None},
         {"name": "Витек", "city": "Kelowna", "timezone": "America/Vancouver", "chat_id": None}]

PREDICTIONS = ["Сегодня удачный день для новых начинаний.", "Ты сильнее, чем думаешь.", "Будет повод улыбнуться."]

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    try:
        data = requests.get(url).json()
        return f"🌤️ Погода в {city}: {data['main']['temp']}°C, {data['weather'][0]['description']}"
    except: return f"⚠️ Не удалось получить погоду для {city}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я буду присылать тебе прогноз погоды каждый день в 7 утра!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Спасибо за сообщение! Я пока учусь отвечать 🤖")

async def send_weather(app):
    for user in USERS:
        if not user["chat_id"]: continue
        now = datetime.now(timezone(user["timezone"]))
        if now.hour == 7 and now.minute < 10:
            msg = f"{get_weather(user['city'])}\n\n🧾 Предсказание: {random.choice(PREDICTIONS)}"
            await app.bot.send_message(chat_id=user["chat_id"], text=msg)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.create_task(send_weather(app)), "interval", minutes=10)
    scheduler.start()
    print("✅ Бот запущен.")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
