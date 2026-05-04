import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Твій токен вже тут
TOKEN = "8788330371:AAGgPYbG0NdHlBqius-RLi12yaeT74lB4Mo"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Функція для створення кнопок
def get_main_menu():
    builder = InlineKeyboardBuilder()
    
    # Кнопка 1: Розклад
    builder.row(types.InlineKeyboardButton(
        text="📅 Розклад", 
        url="https://client.rozklad.org/files/rozklad/rr/r_911.html")
    )
    
    # Кнопка 2: Стікерпак
    builder.row(types.InlineKeyboardButton(
        text="✨ Наш стікерпак", 
        url="https://t.me/addstickers/Odnoklasniky1488_by_fStikBot")
    )

    # Кнопка 3: НАШЕ ДЗ (Додаємо її сюди)
    builder.row(types.InlineKeyboardButton(
        text="📚 Наше ДЗ", 
        url="https://t.me/+Ds0yXnjTpVhlMGNi") # ВСТАВ СЮДИ ПОСИЛАННЯ НА КАНАЛ
    )
    
    return builder.as_markup()

# Обробка команди /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт! Я твій помічник. Скористайся кнопками нижче, щоб знайти потрібну інформацію:",
        reply_markup=get_main_menu()
    )

# Команда /dz для тих, хто пише текстом
@dp.message(Command("dz"))
async def cmd_dz(message: types.Message):
    await message.answer("Ось посилання на канал з ДЗ: ")

# Решта команд (розклад і стікери) залишаються як були...
@dp.message(Command("rozklad"))
async def cmd_rozklad(message: types.Message):
    await message.answer("Ось посилання на розклад: https://client.rozklad.org/files/rozklad/rr/r_911.html")

@dp.message(Command("stickers"))
async def cmd_stickers(message: types.Message):
    await message.answer("Тримай наш крутий стікерпак: https://t.me/addstickers/Odnoklasniky1488_by_fStikBot")

async def main():
    print("Бот запущений і готовий до роботи!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
