import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F

from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from app.ServiceMiddleware import ServiceMiddleware
from app.dispatcher import BotDispatcher
from app.database.db import Database


class BusinessStates(StatesGroup):
    waiting_for_data = State()
    waiting_for_document = State()
    waiting_for_marketing = State()


async def main():
    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Инициализация
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot = Bot(token=BOT_TOKEN)
    logger.info("🚀 Запуск Business Assistant Bot...")

    bot_dispatcher = BotDispatcher()
    dp = bot_dispatcher.get_dispatcher()
    dp.update.middleware(ServiceMiddleware())

    db = Database()
    await db.init()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
