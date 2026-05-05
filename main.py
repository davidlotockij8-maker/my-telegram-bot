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
PHOTO_URL = "https://i.postimg.cc/cHTNtnj0/IMG-20260505-171528-302.jpg"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfW4jXuoCFNvnQmj9xtVpFsjZMIAqibPikJvXKd3a7aus0xtw/viewform"
MONOBANK_URL = "https://send.monobank.ua/jar/3H7WAgDmnQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Розклад уроків", url="https://client.rozklad.org/files/rozklad/rr/r_911.html"))
    builder.row(types.InlineKeyboardButton(text="🔔 Розклад дзвінків", callback_data="bell_schedule"))
    builder.row(types.InlineKeyboardButton(text="📚 Наше ДЗ", callback_data="dz_days"))
    builder.row(types.InlineKeyboardButton(text="✍️ Заповнити ДЗ", url=FORM_URL))
    builder.row(types.InlineKeyboardButton(text="💰 Підтримати", url=MONOBANK_URL))
    return builder.as_markup()

def get_dz_days_menu():
    builder = InlineKeyboardBuilder()
    # Callback_data тепер містить повну назву дня, як у твоїй таблиці
    days = [
        ("Понеділок", "day_Понеділок"), 
        ("Вівторок", "day_Вівторок"), 
        ("Середа", "day_Середа"), 
        ("Четвер", "day_Четвер"), 
        ("П'ятниця", "day_П'ятниця")
    ]
    for text, callback in days:
        builder.row(types.InlineKeyboardButton(text=text, callback_data=callback))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я помічник 8-Г класу.", reply_markup=get_main_menu())

async def fetch_dz_by_day(target_day):
    # Використовуємо твій GID для відповідей форми
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=924216808"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return "Помилка доступу до таблиці 😔"
            
            content = await response.text()
            f = StringIO(content)
            # Читаємо CSV, ігноруючи можливі помилки в заголовках
            reader = csv.reader(f)
            headers = next(reader)
            
            latest_dz_row = None
            for row in reader:
                # Перевіряємо стовпець "День тижня" (зазвичай це другий стовпець, індекс 1)
                if len(row) > 1 and row[1].strip() == target_day:
                    latest_dz_row = row
            
            if latest_dz_row:
                subjects = []
                for i in range(len(headers)):
                    # Пропускаємо службові стовпці
                    if headers[i] not in ['Позначка часу', 'День тижня'] and latest_dz_row[i].strip():
                        subjects.append(f"🔹 {headers[i]}: {latest_dz_row[i]}")
                return "\n".join(subjects)
            
            return f"На {target_day} ДЗ ще не додали 📭"

@dp.callback_query(F.data == "dz_days")
async def show_dz_days(callback: types.CallbackQuery):
    await callback.message.edit_text("Вибери день тижня:", reply_markup=get_dz_days_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("day_"))
async def send_day_dz(callback: types.CallbackQuery):
    day_name = callback.data.split("_")[1]
    dz_text = await fetch_dz_by_day(day_name)
    await callback.message.answer(f"📅 ДЗ на {day_name}:\n\n{dz_text}", parse_mode="Markdown")
    await callback.answer()
@dp.callback_query(F.data == "bell_schedule")
async def send_bell_schedule(callback: types.CallbackQuery):
    await callback.message.answer_photo(photo=PHOTO_URL, caption="⏰ Розклад дзвінків")
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Вибери розділ:", reply_markup=get_main_menu())
    await callback.answer()

async def handle(request):
    return web.Response(text="Bot is running")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    await web.TCPSite(runner, '0.0.0.0', port).start()

async def main():
    asyncio.create_task(start_webserver())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
