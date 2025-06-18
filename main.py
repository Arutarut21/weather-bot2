import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import pytz
import random
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

USERS = [
    {"name": "Женя", "city": "Warsaw", "timezone": "Europe/Warsaw", "chat_id": "@kkkv22"},
    {"name": "Никита", "city": "Warsaw", "timezone": "Europe/Warsaw", "chat_id": "ТОТ_ЧАТ_ID_Никиты"},
    {"name": "Рома", "city": "Rivne", "timezone": "Europe/Kyiv", "chat_id": "@roman_babun"},
    {"name": "Витек", "city": "Kelowna", "timezone": "America/Vancouver", "chat_id": "@viktip09"}
]

PREDICTIONS = [
    "Сегодня отличный день, чтобы сделать что-то доброе",
    "Возможно, сегодня ты найдешь что-то важное",
    "Не забудь улыбнуться себе в зеркало :)",
    "Этот день пройдёт именно так, как тебе нужно",
    "Ты на правильном пути. Просто продолжай"
]

def get_weather(city: str) -> str:
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()
    if response.status_code != 200 or "weather" not in data:
        return "не удалось получить погоду"
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    return f"{description}, {temp}°C"

async def send_weather(app):
    for user in USERS:
        if not user["chat_id"]:
            continue

        tz = pytz.timezone(user["timezone"])
        now = datetime.now(tz)
        if now.hour == 7 and now.minute < 10:
            weather = get_weather(user["city"])
            prediction = random.choice(PREDICTIONS)
            message = f"Доброе утро, {user['name']}!\n\nПогода в {user['city']}: {weather}\n\n🔮 Предсказание: {prediction}"

            try:
                await app.bot.send_message(chat_id=user["chat_id"], text=message)
            except Exception as e:
                print(f"Ошибка при отправке {user['name']}: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает. Ожидай прогноз в 7 утра 🌤")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: app.create_task(send_weather(app)), trigger="interval", minutes=10)
    scheduler.start()

    print("✅ Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
