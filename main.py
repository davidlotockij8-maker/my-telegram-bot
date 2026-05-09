import asyncio
import aiohttp
import os
import csv
from io import StringIO
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- НАЛАШТУВАННЯ ---
TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"
SPREADSHEET_ID = "1jLxy3AZaJ0zpDGiw47Gl3K0lGC1KANoXu-jGN-3wpPY" 

# Переконайся, що цей GID відповідає твоїй вкладці "Актуальне_ДЗ"
GID_ACTUAL_DZ = "924216808" 

PHOTO_URL = "https://i.postimg.cc/cHTNtnj0/IMG-20260505-171528-302.jpg"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfW4jXuoCFNvnQmj9xtVpFsjZMIAqibPikJvXKd3a7aus0xtw/viewform"
MONOBANK_URL = "https://send.monobank.ua/jar/3H7WAgDmnQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- МЕНЮ ---
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📰 Новина дня", callback_data="news_day"))
    builder.row(types.InlineKeyboardButton(text="📅 Розклад уроків", url="https://client.rozklad.org/files/rozklad/rr/r_911.html"))
    builder.row(types.InlineKeyboardButton(text="🔔 Розклад дзвінків", callback_data="bell_schedule"))
    builder.row(types.InlineKeyboardButton(text="📚 Наше ДЗ", callback_data="dz_days"))
    builder.row(types.InlineKeyboardButton(text="✍️ Заповнити ДЗ", url=FORM_URL))
    builder.row(types.InlineKeyboardButton(text="💰 Підтримати проєкт", url=MONOBANK_URL))
    return builder.as_markup()

def get_dz_days_menu():
    builder = InlineKeyboardBuilder()
    days = [
        ("Понеділок", "day_Понеділок"), ("Вівторок", "day_Вівторок"), 
        ("Середа", "day_Середа"), ("Четвер", "day_Четвер"), ("П'ятниця", "day_П'ятниця")
    ]
    for text, callback in days:
        builder.row(types.InlineKeyboardButton(text=text, callback_data=callback))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я помічник 8-Г класу. Вибери потрібний розділ:", reply_markup=get_main_menu())

# --- ТАБЛИЦІ ---
async def fetch_news():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet=Новини"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "Новин поки немає або вкладка не знайдена 🚧"
            content = await response.text()
            return content.replace('"', '').strip()

async def fetch_dz_by_day(target_day):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_ACTUAL_DZ}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "Помилка доступу до таблиці 😔 Перевір доступ 'Усі, хто має посилання'."
            
            content = await response.text()
            f = StringIO(content)
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration:
                return "Таблиця порожня 📭"
            
            for row in reader:
                # Перевіряємо, чи збігається день тижня (стовпець B)
                if len(row) > 1 and row[1].strip().lower() == target_day.lower():
                    subjects = []
                    for i in range(len(headers)):
                        # Виводимо предмети, де є текст домашнього завдання
                        if headers[i] not in ['Позначка часу', 'День тижня'] and i < len(row) and row[i].strip():
                            subjects.append(f"🔹 **{headers[i]}**: {row[i]}")
                    
                    if not subjects:
                        return f"На {target_day} ДЗ не записано 📭"
                    return "\n".join(subjects)
            
            return f"ДЗ на {target_day} ще не додали 📭"

# --- ОБРОБНИКИ ---
@dp.callback_query(F.data == "news_day")
async def show_news(callback: types.CallbackQuery):
    text = await fetch_news()
    await callback.message.answer(f"📢 **ОСТАННЯ НОВИНА:**\n\n{text}", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "dz_days")
async def show_dz_days(callback: types.CallbackQuery):
    await callback.message.edit_text("Вибери день тижня:", reply_markup=get_dz_days_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("day_"))
async def send_day_dz(callback: types.CallbackQuery):
    day_name = callback.data.split("_")[1]
    dz_text = await fetch_dz_by_day(day_name)
    await callback.message.answer(f"📅 **ДЗ на {day_name}:**\n\n{dz_text}", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "bell_schedule")
async def send_bell_schedule(callback: types.CallbackQuery):
    await callback.message.answer_photo(photo=PHOTO_URL, caption="⏰ **Розклад дзвінків**")
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Головне меню:", reply_markup=get_main_menu())
    await callback.answer()

# --- СЕРВЕР (Для AWS/Railway) ---
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    await web.TCPSite(runner, '0.0.0.0', port).start()

async def main():
    asyncio.create_task(start_webserver())
    print("Бот запущений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
