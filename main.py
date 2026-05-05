import asyncio
import aiohttp
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- НАЛАШТУВАННЯ ---
TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"
# Твій ID таблиці
SPREADSHEET_ID = "1jLxy3AZaJ0zpDGiw47Gl3K0lGC1KANoXu-jGN-3wpPY" 
# Пряме посилання на фото розкладу дзвінків
PHOTO_URL = "https://i.postimg.cc/cHTNtnj0/IMG-20260505-171528-302.jpg"
# Твоя Google Форма
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfW4jXuoCFNvnQmj9xtVpFsjZMIAqibPikJvXKd3a7aus0xtw/viewform"
# Твоя банка Monobank
MONOBANK_URL = "https://send.monobank.ua/jar/3H7WAgDmnQ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ГОЛОВНЕ МЕНЮ ---
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Розклад уроків", url="https://client.rozklad.org/files/rozklad/rr/r_911.html"))
    builder.row(types.InlineKeyboardButton(text="🔔 Розклад дзвінків", callback_data="bell_schedule"))
    builder.row(types.InlineKeyboardButton(text="📚 Наше ДЗ", callback_data="dz_days"))
    builder.row(types.InlineKeyboardButton(text="✍️ Заповнити ДЗ (Форма)", url=FORM_URL))
    builder.row(types.InlineKeyboardButton(text="💰 Підтримати проєкт", url=MONOBANK_URL))
    return builder.as_markup()

# --- МЕНЮ ДНІВ ТИЖНЯ ---
def get_dz_days_menu():
    builder = InlineKeyboardBuilder()
    days = [("Понеділок", "day_0"), ("Вівторок", "day_1"), ("Середа", "day_2"), ("Четвер", "day_3"), ("П'ятниця", "day_4")]
    for text, callback in days:
        builder.row(types.InlineKeyboardButton(text=text, callback_data=callback))
    builder.row(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я помічник 8-Г класу. Вибери потрібний розділ:", reply_markup=get_main_menu())

# --- ОБРОБНИКИ КНОПОК ---

@dp.callback_query(F.data == "dz_days")
async def show_dz_days(callback: types.CallbackQuery):
    await callback.message.edit_text("На який день тижня ти хочеш подивитися ДЗ?", reply_markup=get_dz_days_menu())
    await callback.answer()

@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery):
    await callback.message.edit_text("Привіт! Я помічник 8-Г класу. Вибери потрібний розділ:", reply_markup=get_main_menu())
    await callback.answer()

@dp.callback_query(F.data.startswith("day_"))
async def send_day_dz(callback: types.CallbackQuery):
    day_index = int(callback.data.split("_")[1])
    days_names = ["Понеділок", "Вівторок", "Середу", "Четвер", "П'ятницю"]
    
    # Зараз бот просто бере дані з головного аркуша таблиці.
    # Якщо ти створиш окремі вкладки для днів, тут можна буде міняти gid.
    dz_text = await fetch_dz() 
    
    await callback.message.answer(f"📅 ДЗ на {days_names[day_index]}:\n\n{dz_text}", parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "bell_schedule")
async def send_bell_schedule(callback: types.CallbackQuery):
    await callback.message.answer_photo(photo=PHOTO_URL, caption="⏰ Розклад дзвінків")
    await callback.answer()

# --- ФУНКЦІЯ ДЛЯ ТАБЛИЦІ ---
async def fetch_dz():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                lines = content.splitlines()
                final_dz = []
                for line in lines:
                    clean_line = line.replace('"', '').replace(',', ' ').strip()
                    if clean_line:
                        final_dz.append(clean_line)
                return "\n".join(final_dz)
            return "Не вдалося отримати ДЗ 😔 Перевір доступ до таблиці."
# --- СЕРВЕР ДЛЯ RAILWAY (ПОРТ) ---
async def handle(request):
    return web.Response(text="Bot is alive!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Railway видає порт автоматично. Якщо його немає — ставимо 10000.
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- ЗАПУСК ---
async def main():
    asyncio.create_task(start_webserver())
    print("Бот запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
