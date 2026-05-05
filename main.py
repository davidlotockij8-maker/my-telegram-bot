import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"
# ВСТАВ СВІЙ ID ТАБЛИЦІ СЮДИ
SPREADSHEET_ID = "1jLxy3AZaJ0zpDGiw47Gl3K0lGC1KANoXu-jGN-3wpPY" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Розклад", url="https://client.rozklad.org/files/rozklad/rr/r_911.html"))
    builder.row(types.InlineKeyboardButton(text="✨ Наш стікерпак", url="https://t.me/addstickers/Odnoklasniky1488_by_fStikBot"))
    # Тепер це не посилання, а команда для бота
    builder.row(types.InlineKeyboardButton(text="📚 Наше ДЗ", callback_data="get_dz"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я твій помічник:", reply_markup=get_main_menu())

# Функція, яка бере текст із Google Таблиці (клітинка A1)
async def fetch_dz():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.text()
                # Беремо перший рядок і першу колонку
                first_row = data.split('\n')[0]
                return first_row
            return "Не вдалося отримати ДЗ 😔"

# Обробка натискання на кнопку "Наше ДЗ"
@dp.callback_query(F.data == "get_dz")
async def send_dz(callback: types.CallbackQuery):
    dz_text = await fetch_dz()
    await callback.message.answer(f"📖 Актуальне ДЗ:\n\n{dz_text}", parse_mode="Markdown")
    await callback.answer() # Прибирає годинник з кнопки

# Блок для Render (веб-сервер)
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

async def main():
    asyncio.create_task(start_webserver())
    print("Бот запущений!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
