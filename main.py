import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import router

# Объект бота
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

# Основной запуск бота
async def main():
    dp.include_router(router)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        await bot.session.close()
        print(f"error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
