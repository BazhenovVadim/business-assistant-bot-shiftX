from aiogram import Router, F
from aiogram.types import Message

router = Router()


@router.message(F.text.contains("анализ") | F.text.contains("отчет") | F.text.contains("продаж"))
async def handle_analysis_request(message: Message, conversation_service):
    analysis_result = (
        "📈 Анализ продаж за неделю:\n\n"
        "• Общая выручка: 150 000 руб.\n"
        "• Средний чек: 1 200 руб.\n"
        "• Топ товары: Капучино, Латте, Выпечка\n"
        "💡 Рекомендация: увеличить ассортимент выпечки."
    )

    await message.answer(analysis_result)

    await conversation_service.add_message(
        message.from_user.id,
        message.text,
        analysis_result,
        "analytics"
    )


@router.message(F.text.contains("ответ") | F.text.contains("клиен") | F.text.contains("шаблон"))
async def handle_template_request(message: Message, conversation_service):
    quick_responses = (
        "💬 Готовые ответы:\n"
        "— Отследить заказ: …\n"
        "— Ответ на жалобу: …\n"
        "— Уточнение деталей: …\n"
        "— Благодарность за отзыв…"
    )

    await message.answer(quick_responses)

    await conversation_service.add_message(
        message.from_user.id,
        message.text,
        quick_responses,
        "templates"
    )


@router.message(F.text.contains("договор") | F.text.contains("документ"))
async def handle_document_request(message: Message, conversation_service):
    document_types = (
        "📝 Генератор документов:\n"
        "• Договор\n"
        "• Акт\n"
        "• Коммерческое предложение\n"
        "• Уведомления"
    )

    await message.answer(document_types)

    await conversation_service.add_message(
        message.from_user.id,
        message.text,
        document_types,
        "documents"
    )


@router.message(F.text.contains("маркетинг") | F.text.contains("пост") | F.text.contains("акци"))
async def handle_marketing_request(message: Message, conversation_service):
    marketing_ideas = (
        "📈 Идеи для маркетинга:\n"
        "— Акции недели\n"
        "— Идеи для соцсетей\n"
        "— Готовые тексты постов"
    )

    await message.answer(marketing_ideas)

    await conversation_service.add_message(
        message.from_user.id,
        message.text,
        marketing_ideas,
        "marketing"
    )


@router.message(F.text.contains("налог") | F.text.contains("юри") | F.text.contains("отчетност"))
async def handle_legal_request(message: Message, conversation_service):
    legal_advice = (
        "⚖️ Консультация:\n"
        "— Сроки отчетности\n"
        "— Налоги\n"
        "— Претензии клиентов"
    )

    await message.answer(legal_advice)

    await conversation_service.add_message(
        message.from_user.id,
        message.text,
        legal_advice,
        "legal"
    )


@router.message(F.text)
async def handle_any_text(message: Message, conversation_service):
    user_text = message.text.lower()

    quick = {
        "привет": "👋 Привет! Чем помочь?",
        "спасибо": "🙏 Обращайтесь!",
        "как дела": "🤖 Отлично!",
    }

    if user_text in quick:
        resp = quick[user_text]
        await message.answer(resp)
        await conversation_service.add_message(
            message.from_user.id,
            message.text,
            resp,
            "general"
        )
        return

    response = (
        "🤔 Я понял запрос, но пока работаю в тестовом режиме.\n"
        "Запрос сохранён, позже я дам полноценный ответ."
    )

    await message.answer(response)

    await conversation_service.add_message(
        message.from_user.id,
        message.text,
        response,
        "general"
    )
