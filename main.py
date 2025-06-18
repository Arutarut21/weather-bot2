import asyncio
import os
import random
from datetime import datetime
import pytz
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

USERS = [
    {
        "name": "Женя",
        "chat_id": 123456789,
        "city": "Warsaw",
        "timezone": "Europe/Warsaw"
    },
    # Добавь других людей по аналогии
]

PREDICTIONS = [
    "Сегодня твой день!",
    "Будь осторожен на поворотах судьбы!",
    "Жди приятную новость вечером.",
    "Кто-то думает о тебе прямо сейчас."
]

def get_weather(city):
    api_key = os.getenv("OPENWEATHER_TOKEN")
    if not api_key:
        return "API ключ не задан"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    res = requests.get(url)
    data = res.json()
    if res.status_code != 200 or "main" not in data:
        return "Ошибка погоды"
    temp = data["main"]["temp"]
    descr = data["weather"][0]["description"]
    return f"{temp}°C, {descr}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text(f"Ты написал: {msg}")

async def send_weather(app):
    for user in USERS:
        if not user.get("chat_id"):
            continue
        now = datetime.now(pytz.timezone(user["timezone"]))
        if now.hour == 7 and now.minute < 10:
            weather = get_weather(user["city"])
            prediction = random.choice(PREDICTIONS)
            message = f"☀️ Погода в {user['city']}:\n{weather}\n\n🔮 Предсказание:\n{prediction}"
            try:
                await app.bot.send_message(chat_id=user["chat_id"], text=message)
            except Exception as e:
                print(f"Ошибка отправки {user['name']} ({user['city']}): {e}")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: asyncio.create_task(send_weather(app)), "interval", minutes=10)
    scheduler.start()

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
