import asyncio
import aiohttp
import os
import csv
from io import StringIO
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- НАЛАШТУВАННЯ (Перевір ці дані!) ---
TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"
SPREADSHEET_ID = "1jLxy3AZaJ0zpDGiw47Gl3K0lGC1KANoXu-jGN-3wpPY" 

# GID вкладок у твоїй таблиці
GID_RESPONSES = "924216808"  # Вкладка з ДЗ
GID_NEWS = "265453971"       # Вкладка з Новинами

# Пряме посилання на розклад дзвінків (якщо він рідко змінюється)
PHOTO_ROZKLAD = "https://i.postimg.cc/Wb5zqp0n/IMG-20260505-171528-302.jpg"

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfW4jXuoCFNvnQmj9xtVpFsjZMIAqibPikJvXKd3a7aus0xtw/viewform"
MONOBANK_URL = "https://send.monobank.ua/jar/3H7WAgDmnQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ГОЛОВНЕ МЕНЮ ---
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
    days = [("Понеділок", "day_Понеділок"), ("Вівторок", "day_Вівторок"), ("Середа", "day_Середа"), ("Четвер", "day_Четвер"), ("П'ятниця", "day_П'ятниця")]
    for text, callback in days:
        builder.row(types.InlineKeyboardButton(text=text, callback_data=callback))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я помічник 8-Г класу. Вибери потрібний розділ:", reply_markup=get_main_menu())

# --- ЛОГІКА НОВИН (З ТАБЛИЦІ) ---
@dp.callback_query(F.data == "news_day")
async def show_news(callback: types.CallbackQuery):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_NEWS}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await callback.message.answer("Помилка доступу до таблиці новин 🚧")
                return
            content = await response.text()
            reader = list(csv.reader(StringIO(content)))
            if reader and len(reader) > 0:
                row = reader[0]
                text = row[0].strip() if len(row) > 0 else "Новин поки немає 📭"
                photo_url = row[1].strip() if len(row) > 1 else ""

                if photo_url and photo_url.startswith("http"):
                    try:
                        await callback.message.answer_photo(photo=photo_url, caption=f"📢 **ОСТАННЯ НОВИНА:**\n\n{text}", parse_mode="Markdown")
                    except Exception:
                        await callback.message.answer(f"📢 **ОСТАННЯ НОВИНА:**\n\n{text}\n\n*(Фото не завантажилось, перевір посилання)*")
                else:
                    await callback.message.answer(f"📢 **ОСТАННЯ НОВИНА:**\n\n{text}", parse_mode="Markdown")
            else:
                await callback.message.answer("Розділ новин порожній 📭")
    await callback.answer()

# --- ЛОГІКА РОЗКЛАДУ ДЗВІНКІВ ---
@dp.callback_query(F.data == "bell_schedule")
async def send_bell_schedule(callback: types.CallbackQuery):
    try:
        await callback.message.answer_photo(photo=PHOTO_ROZKLAD, caption="⏰ **Розклад дзвінків**")
    except Exception as e:
        await callback.message.answer(f"Помилка завантаження фото розкладу. Перевір PHOTO_ROZKLAD у коді.")
    await callback.answer()

# --- ЛОГІКА ДЗ ---
async def fetch_dz_by_day(target_day):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID_RESPONSES}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200: return "Помилка доступу 😔"
            content = await response.text()
            reader = list(csv.reader(StringIO(content)))
            if len(reader) < 2: return "ДЗ поки порожньо 📭"
            headers = [h.strip() for h in reader[0]]
            latest_row = None
            # Шукаємо останній доданий запис для цього дня
            for row in reversed(reader[1:]):
                if len(row) > 1 and row[1].strip().lower() == target_day.lower():
                    latest_row = row
                    break
            if latest_row:
                res = [f"🔹 **{headers[i]}**: {latest_row[i].strip()}" for i in range(len(headers)) if i < len(latest_row) and headers[i] not in ['Позначка часу', 'День тижня'] and latest_row[i].strip().lower() != "нічого" and latest_row[i].strip()]
                return "\n".join(res) if res else "ДЗ не записано 📭"
            return f"ДЗ на {target_day} ще немає 📭"

@dp.callback_query(F.data == "dz_days")
async def show_dz_days(callback: types.CallbackQuery):
    await callback.message.edit_text("Вибери день тижня:", reply_markup=get_dz_days_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("day_"))
async def send_day_dz(callback: types.CallbackQuery):
    day = callback.data.split("_")[1]
    text = await fetch_dz_by_day(day)
    await callback.message.answer(f"📅 **ДЗ на {day}:**\n\n{text}", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Головне меню:", reply_markup=get_main_menu())
    await callback.answer()

# --- ЗАПУСК ---
async def handle(request): return web.Response(text="Bot is alive!")

async def main():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    await web.TCPSite(runner, '0.0.0.0', port).start()
    print("Помогатор-8Г запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
