import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

from app.dispatcher import BotDispatcher


from app.keyboards.menus import get_main_menu, get_quick_actions_menu
from app.database.database import Database
from app.service import UserService, ConversationService, BusinessDataService, TemplateService, AnalyticService

# Настройка логирования



# assistant = BusinessAssistant()  подключить ии анализ


# States для сложных операций
class BusinessStates(StatesGroup):
    waiting_for_data = State()
    waiting_for_document = State()
    waiting_for_marketing = State()



# ========== УНИВЕРСАЛЬНЫЙ ОБРАБОТЧИК ==========

# @dp.message(F.text)
# async def handle_any_text(message: Message):
#     """Обработка любых текстовых запросов через ИИ"""
#     user_text = message.text
#
#     # Короткие быстрые ответы
#     quick_replies = {
#         "привет": "👋 Привет! Чем могу помочь вашему бизнесу?",
#         "спасибо": "🙏 Всегда рад помочь! Обращайтесь!",
#         "как дела": "🤖 Работаю над помощью вашему бизнесу! Что нужно сделать?",
#     }
#
#     if user_text.lower() in quick_replies:
#         await message.answer(quick_replies[user_text.lower()])
#         return
#
#     # Сложные запросы - к ИИ
#     await message.answer("🤔 Думаю над ответом...")
#
#     try:
#         # Получаем ответ от ИИ-помощника
#         ai_response = await assistant.process_business_request(
#             user_text,
#             message.from_user.id
#         )
#         await message.answer(ai_response)
#
#         # Сохраняем в историю
#         await db.save_conversation(
#             user_id=message.from_user.id,
#             user_message=user_text,
#             bot_response=ai_response
#         )
#
#     except Exception as e:
#         logger.error(f"AI error: {e}")
#         await message.answer(
#             "❌ Произошла ошибка. Попробуйте переформулировать запрос "
#             "или использовать кнопки меню."
#         )


# ========== ЗАПУСК БОТА ==========

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

    db = Database()
    # Инициализация БД
    await db.init()
    dp["user_service"] = UserService(db)
    dp["conversation_service"] = ConversationService(db)
    # Запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
