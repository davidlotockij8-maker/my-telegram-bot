import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- НАЛАШТУВАННЯ (ПЕРЕВІРЕНО) ---
TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"
# Твій ID таблиці зі скриншота
SPREADSHEET_ID = "1jLxy3AZaJ0zpDGiw47Gl3K0lGC1KANoXu-jGN-3wpPY" 
# Пряме посилання на фото (те, що з "i.postimg")
PHOTO_URL = "https://i.postimg.cc/cHTNtnj0/IMG-20260505-171528-302.jpg"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ГОЛОВНЕ МЕНЮ ---
def get_main_menu():
    builder = InlineKeyboardBuilder()
    # Кнопка 1: Розклад уроків (зовнішнє посилання)
    builder.row(types.InlineKeyboardButton(
        text="📅 Розклад уроків", 
        url="https://client.rozklad.org/files/rozklad/rr/r_911.html")
    )
    # Кнопка 2: Розклад дзвінків (надсилає фото)
    builder.row(types.InlineKeyboardButton(
        text="🔔 Розклад дзвінків", 
        callback_data="bell_schedule")
    )
    # Кнопка 3: Стікерпак
    builder.row(types.InlineKeyboardButton(
        text="✨ Наш стікерпак", 
        url="https://t.me/addstickers/Odnoklasniky1488_by_fStikBot")
    )
    # Кнопка 4: Наше ДЗ (бере дані з таблиці)
    builder.row(types.InlineKeyboardButton(
        text="📚 Наше ДЗ", 
        callback_data="get_dz")
    )
    return builder.as_markup()

# --- ОБРОБНИКИ КОМАНД ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Я помічник 8-Г класу. Вибери, що тебе цікавить:", 
        reply_markup=get_main_menu()
    )

# --- ФУНКЦІЯ ЧИТАННЯ ТАБЛИЦІ ---
async def fetch_dz():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.text()
                lines = content.splitlines()
                final_dz = []
                for line in lines:
                    # Очищення від технічних символів CSV
                    clean_line = line.replace('"', '').replace(',', ' ').strip()
                    if clean_line:
                        final_dz.append(clean_line)
                return "\n".join(final_dz)
            return "Не вдалося отримати ДЗ 😔 Перевір доступ до таблиці."

# --- ОБРОБКА НАТИСКАНЬ КНОПОК ---
@dp.callback_query(F.data == "get_dz")
async def send_dz(callback: types.CallbackQuery):
    dz_text = await fetch_dz()
    await callback.message.answer(
        f"📖 Актуальне ДЗ:\n\n{dz_text}", 
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "bell_schedule")
async def send_bell_schedule(callback: types.CallbackQuery):
    await callback.message.answer_photo(
        photo=PHOTO_URL,
        caption="⏰ Розклад дзвінків на 2024/2025 рік",
        parse_mode="Markdown"
    )
    await callback.answer()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (ОБОВ'ЯЗКОВО) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Порт 10000 для Render
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# --- ГОЛОВНИЙ ЗАПУСК ---
async def main():
    # Запускаємо веб-сервер у фоні
    asyncio.create_task(start_webserver())
    print("Бот успішно запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
