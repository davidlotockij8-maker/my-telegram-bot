import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web  # Додано для Render

TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Твої кнопки
def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="📅 Розклад", url="https://client.rozklad.org/files/rozklad/rr/r_911.html"))
    builder.row(types.InlineKeyboardButton(text="✨ Наш стікерпак", url="https://t.me/addstickers/Odnoklasniky1488_by_fStikBot"))
    builder.row(types.InlineKeyboardButton(text="📚 Наше ДЗ", url="https://t.me/+Ds0yXnjTpVhlMGNi"))
    return builder.as_markup()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Я твій помічник:", reply_markup=get_main_menu())

# --- ЦЕЙ БЛОК ТРЕБА ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000) # Render зазвичай використовує цей порт
    await site.start()
# --------------------------------

async def main():
    # Запускаємо веб-сервер фоном
    asyncio.create_task(start_webserver())
    print("Бот запущений!")
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
