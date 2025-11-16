from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from fastapi import Depends

from app.keyboards.menus import (
    get_main_menu,
    get_quick_actions_menu,
    get_intelligence_menu,
    get_marketing_menu,
    get_documents_menu,
    get_analytics_menu,
    get_profile_menu
)
from app.dependencies import (
    get_user_service,
    get_conversation_service
)
from app.service import UserService, ConversationService

router = Router()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    user_service: UserService = Depends(get_user_service)
):
    """Обработчик команды /start"""
    user = await user_service.get_or_create_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )

    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я твой ИИ-помощник для управления бизнесом. "
        "Помогаю с операционными задачами:\n\n"
        "• 💬 Быстрые ответы клиентам\n"
        "• 📊 Анализ продаж и остатков\n"
        "• 📝 Договоры и документы\n"
        "• 📈 Маркетинг и посты\n"
        "• ⚖️ Юридические консультации\n\n"
        "Выбери что нужно сделать:"
    )

    await message.answer(welcome_text, reply_markup=get_main_menu())


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🆘 **Business Assistant - помощь**\n\n"
        "**Основные команды:**\n"
        "/start - главное меню\n"
        "/help - эта справка\n"
        "/profile - мой профиль\n"
        "/history - история консультаций\n\n"
        "**Быстрые действия (просто напиши):**\n"
        "• 'анализ продаж' - отчет по продажам\n"
        "• 'ответ клиенту' - шаблоны ответов\n"
        "• 'договор' - создать документ\n"
        "• 'маркетинг' - идеи для постов\n"
        "• 'налоги' - консультация\n\n"
        "Или используй кнопки меню 👇"
    )
    await message.answer(help_text)


@router.message(Command("profile"))
async def cmd_profile(
    message: Message,
    user_service: UserService = Depends(get_user_service)
):
    """Обработчик команды /profile"""
    user_id = message.from_user.id
    stats = await user_service.get_user_stats(user_id)
    profile_text = (
        f"👤 **Ваш бизнес-профиль:**\n\n"
        f"• Консультаций: {stats['consultations_count']}\n"
        f"• Популярные темы: {', '.join([cat[0] for cat in stats['popular_categories']]) if stats['popular_categories'] else 'Еще нет'}\n\n"
        "Чтобы обновить профиль, напишите:\n"
        "• 'мой бизнес: кофейня' - указать отрасль\n"
        "• 'размер: 5 сотрудников' - указать размер"
    )

    await message.answer(profile_text)


@router.message(Command("history"))
async def cmd_history(
    message: Message,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """Обработчик команды /history - история консультаций"""
    user_id = message.from_user.id
    conversations = await conversation_service.get_user_conversations(user_id, limit=5)

    if not conversations:
        await message.answer("📝 У вас еще не было консультаций.")
        return

    history_text = "📝 **Последние консультации:**\n\n"
    for i, conv in enumerate(conversations, 1):
        preview = conv.user_message[:30] + "..." if len(conv.user_message) > 30 else conv.user_message
        history_text += f"{i}. {conv.category or 'Общее'} - {conv.created_at.strftime('%d.%m %H:%M')}\n"
        history_text += f"   💬 {preview}\n\n"

    await message.answer(history_text)


@router.message(Command("quick"))
async def cmd_quick(message: Message):
    """Обработчик команды /quick - быстрые действия"""
    await message.answer(
        "🚀 **Быстрые действия для бизнеса:**\n\n"
        "Выберите категорию:",
        reply_markup=get_quick_actions_menu()
    )


@router.message(F.text == "Интеллект")
async def open_ai_section(message: Message):
    await message.answer("🧠 Раздел: Интеллект", reply_markup=get_intelligence_menu())


@router.message(F.text == "Аналитика")
async def open_analytics_section(message: Message):
    await message.answer("📊 Раздел: Аналитика", reply_markup=get_analytics_menu())


@router.message(F.text == "Документы")
async def open_documents_section(message: Message):
    await message.answer("📄 Раздел: Документы", reply_markup=get_documents_menu())


@router.message(F.text == "Маркетинг")
async def open_marketing_section(message: Message):
    await message.answer("📈 Раздел: Маркетинг", reply_markup=get_marketing_menu())


@router.message(F.text == "Быстрое")
async def open_quick_section(message: Message):
    await message.answer("⚡ Быстрые действия:", reply_markup=get_quick_actions_menu())


@router.message(F.text == "Поддержка")
async def open_support_section(message: Message):
    await message.answer("Чем могу помочь?", reply_markup=None)


@router.message(F.text == "Мой профиль")
async def open_profile_section(message: Message):
    await message.answer("Профиль", reply_markup=get_profile_menu())