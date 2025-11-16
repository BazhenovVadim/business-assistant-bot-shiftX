from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fastapi import Depends

from app.dependencies import get_user_service, get_marketing_service, get_document_service
from app.handlers.states import States
from app.keyboards.menus import get_platforms_keyboard, get_post_styles_keyboard, get_content_themes_keyboard
from app.service import UserService, MarketingService, DocumentAnalyzer

router = Router()


@router.message(F.text.contains("анализ") | F.text.contains("отчет") | F.text.contains("продаж"))
async def handle_analysis_request(message: Message, conversation_service):
    analysis_result = (
        "📈 Анализ продаж за неделю:\n\n"
        "• Общая выручка: 150 000 руб.\n"
        "• Средний чек: 1 200 руб.\n"
        "• Топ товары: \n"
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
@router.message(F.text, StateFilter("waiting_personal_data"))
async def process_personal_data(
        message: Message,
        state: FSMContext,
        user_service: UserService = Depends(get_user_service)
):
    """Обработка и сохранение личных данных"""
    try:
        parts = message.text.strip().split()

        if len(parts) < 2:
            await message.answer(
                "❌ Пожалуйста, введите Имя и Фамилию через пробел\n"
                "Пример: <code>Иван Иванов</code>",
                parse_mode="HTML"
            )
            return

        first_name, last_name = parts[0], ' '.join(parts[1:])

        await user_service.update_user_profile(
            message.from_user.id,
            first_name=first_name,
            last_name=last_name
        )

        await message.answer(
            f"✅ Личные данные обновлены!\n"
            f"Теперь вы: <b>{first_name} {last_name}</b>",
            parse_mode="HTML"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при обновлении данных: {str(e)}")

    finally:
        await state.clear()


@router.message(States.waiting_niche)
async def process_niche(message: Message, state: FSMContext):
    await state.update_data(niche=message.text)
    await message.answer(
        "🎯 Какую цель преследуете?\n\n"
        "• Привлечь клиентов\n• Увеличить продажи\n• Повысить узнаваемость\n• Запустить новый продукт"
    )
    await state.set_state(States.waiting_goal)


@router.message(States.waiting_goal)
async def process_goal(message: Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.answer(
        "📱 Выберите основную площадку:",
        reply_markup=get_platforms_keyboard()
    )
    await state.set_state(States.waiting_platform)


@router.callback_query(States.waiting_platform, F.data.startswith("platform:"))
async def process_platform(call: CallbackQuery, state: FSMContext):
    platform = call.data.split(":")[1]
    await state.update_data(platform=platform)
    await call.message.edit_text(
        f"📱 Площадка: {platform}\n\n"
        "💡 Есть особые пожелания?\n"
        "(или напишите 'нет')"
    )
    await state.set_state(States.waiting_custom_request)
    await call.answer()


@router.message(States.waiting_custom_request)
async def process_custom_request(message: Message, state: FSMContext,
                                 marketing_idea_service: MarketingService = Depends(get_marketing_service)):
    user_data = await state.get_data()
    custom_request = message.text if message.text.lower() != "нет" else None

    await message.answer("🚀 Генерирую маркетинговую стратегию...")

    idea = await marketing_idea_service.generate_marketing_idea(
        user_id=message.from_user.id,
        niche=user_data['niche'],
        goal=user_data['goal'],
        platform=user_data['platform'],
        custom_request=custom_request
    )

    response = f"🎯 МАРКЕТИНГОВАЯ СТРАТЕГИЯ\n\n"
    response += f"📌 Название: {idea.get('title', 'Стратегия')}\n\n"
    response += f"🔍 Проблема: {idea.get('problem', 'Не указана')}\n\n"
    response += f"💡 Решение: {idea.get('solution', 'Не указано')}\n\n"
    response += f"📋 План действий:\n"
    for step in idea.get('action_plan', [])[:3]:
        response += f"• {step}\n"

    await message.answer(response)

    if idea.get('content_ideas'):
        content_text = "📝 ИДЕИ ДЛЯ КОНТЕНТА:\n"
        for i, content_idea in enumerate(idea.get('content_ideas', [])[:3], 1):
            content_text += f"{i}. {content_idea}\n"
        await message.answer(content_text)

    metrics_text = "📊 МЕТРИКИ И РЕКОМЕНДАЦИИ\n\n"
    metrics_text += f"📈 KPI: {idea.get('metrics', 'Не указаны')}\n"
    metrics_text += f"💰 Бюджет: {idea.get('budget_tips', 'Не указаны')}"

    await message.answer(metrics_text)
    await state.clear()


@router.message(States.waiting_post_topic)
async def process_post_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await message.answer(
        "🎨 Выберите стиль поста:",
        reply_markup=get_post_styles_keyboard()
    )
    await state.set_state(States.waiting_post_style)


@router.callback_query(States.waiting_post_style, F.data.startswith("style:"))
async def process_post_style(call: CallbackQuery, state: FSMContext,
                             marketing_idea_service: MarketingService = Depends(get_marketing_service)):
    style = call.data.split(":")[1]
    user_data = await state.get_data()

    await call.message.edit_text("🚀 Генерирую пост...")

    post = await marketing_idea_service.generate_social_post(
        user_id=call.from_user.id,
        topic=user_data['topic'],
        style=style
    )

    response = f"📱 ГОТОВЫЙ ПОСТ\n\n"
    response += f"📌 Заголовок:\n{post.get('headline', '')}\n\n"
    response += f"🎣 Крючок:\n{post.get('hook', '')}\n\n"
    response += f"📝 Текст:\n{post.get('body', '')}\n\n"
    response += f"🔗 Призыв: {post.get('cta', '')}\n\n"

    if post.get('hashtags'):
        response += f"🏷️ Хэштеги: {' '.join(post.get('hashtags', []))}\n\n"

    if post.get('visual_tips'):
        response += f"🎨 Визуал: {post.get('visual_tips', '')}"

    await call.message.answer(response)
    await state.clear()


@router.message(States.waiting_business_description)
async def process_business_description(message: Message, state: FSMContext):
    await state.update_data(business_description=message.text)
    await message.answer(
        "🎯 <b>Выберите основную тематику контента:</b>",
        reply_markup=get_content_themes_keyboard()
    )
    await state.set_state(States.waiting_content_theme)


@router.callback_query(States.waiting_content_theme, F.data.startswith("theme:"))
async def process_content_theme(call: CallbackQuery, state: FSMContext,
                                marketing_idea_service: MarketingService = Depends(get_marketing_service)):
    theme = call.data.split(":")[1]
    user_data = await state.get_data()

    await call.message.edit_text("🗓️ Создаю контент-план на 30 дней...")

    content_plan = await marketing_idea_service.generate_content_plan(
        user_id=call.from_user.id,
        business_description=user_data['business_description'],
        theme=theme
    )

    # Показываем общую стратегию
    response = f"🗓️ КОНТЕНТ-ПЛАН НА 30 ДНЕЙ\n\n"
    response += f"📋 Стратегия:\n{content_plan.get('strategy_overview', '')}\n\n"

    await call.message.answer(response)

    week_plan = "📅 <b>ПЕРВАЯ НЕДЕЛЯ:</b>\n\n"
    for day in content_plan.get('daily_posts', [])[:7]:
        week_plan += f"📌 День {day.get('day', '')}:\n"
        week_plan += f"   Тема: {day.get('topic', '')}\n"
        week_plan += f"   Формат: {day.get('format', '')}\n"
        week_plan += f"   Цель: {day.get('goal', '')}\n\n"

    await call.message.answer(week_plan)

    # Рекомендации
    if content_plan.get('tools_recommendations'):
        tools_text = f"🛠️ ИНСТРУМЕНТЫ:\n{content_plan.get('tools_recommendations', '')}"
        await call.message.answer(tools_text)

    await state.clear()

# Договора

@router.message(States.waiting_contract_details)
async def process_contract_details(message: Message, state: FSMContext,
                                   document_service: DocumentAnalyzer = Depends(get_document_service)):
    contract_details = message.text

    await message.answer("⚖️ Генерирую договор...")

    result = await document_service.create_contract(
        user_id=message.from_user.id,
        contract_details=contract_details
    )

    response = f"📄 ДОГОВОР СОЗДАН\n\n"
    response += f"📌 Тип:{result.get('document_type', 'договор')}\n"
    response += f"🏷️ Название: {result.get('title', 'Договор')}\n\n"

    await message.answer(response)

    if result.get('key_points'):
        points_text = "🔑 КЛЮЧЕВЫЕ ПУНКТЫ:\n"
        for point in result.get('key_points', [])[:5]:
            points_text += f"• {point}\n"
        await message.answer(points_text)
    risks_text = f"⚠️ РИСКИ:\n{result.get('risks', 'Не выявлено')}\n\n"
    risks_text += f"💡 РЕКОМЕНДАЦИИ:\n{result.get('recommendations', 'Нет рекомендаций')}"
    await message.answer(risks_text)

    content = result.get('content', '')
    if len(content) > 4000:
        await message.answer("📋 Текст договора слишком длинный для сообщения.\nИспользуйте функцию экспорта.")
    else:
        await message.answer(f"📝 ТЕКСТ ДОГОВОРА:\n\n{content}")

    await state.clear()


@router.message(States.waiting_act_data)
async def process_act_data(message: Message, state: FSMContext,
                           document_service: DocumentAnalyzer = Depends(get_document_service)):
    act_data = message.text

    await message.answer("🧾 Генерирую акт...")

    result = await document_service.create_act(
        user_id=message.from_user.id,
        act_data=act_data
    )

    response = f"🧾 АКТ СОЗДАН\n\n"
    response += f"📌 Тип: {result.get('document_type', 'акт')}\n"
    response += f"🏷️ Название:{result.get('title', 'Акт')}\n\n"

    await message.answer(response)

    # Обязательные поля
    if result.get('required_fields'):
        fields_text = "📋 ОБЯЗАТЕЛЬНЫЕ ПОЛЯ:\n"
        for field in result.get('required_fields', [])[:5]:
            fields_text += f"• {field}\n"
        await message.answer(fields_text)

    # Чек-лист
    if result.get('checklist'):
        await message.answer(f"✅ ЧЕК-ЛИСТ:\n{result.get('checklist', '')}")

    # Текст акта
    content = result.get('content', '')
    if len(content) > 4000:
        await message.answer("📋 Текст акта слишком длинный для сообщения.")
    else:
        await message.answer(f"📝 ТЕКСТ АКТА:\n\n{content}")

    await state.clear()


@router.message(States.waiting_document_text)
async def process_document_text(message: Message, state: FSMContext,
                                document_service: DocumentAnalyzer = Depends(get_document_service)):
    document_text = message.text

    await message.answer("📑 Проверяю документ...")
    result = await document_service.check_document(
        user_id=message.from_user.id,
        document_text=document_text
    )

    status_emojis = {
        "ok": "✅",
        "risky": "⚠️",
        "critical": "❌"
    }

    status = result.get('status', 'ok')
    emoji = status_emojis.get(status, '📄')

    response = f"{emoji} РЕЗУЛЬТАТ ПРОВЕРКИ\n\n"
    response += f"📊 Статус: {status.upper()}\n"
    response += f"📝 Общая оценка: {result.get('summary', 'Не указана')}\n\n"

    await message.answer(response)

    if result.get('errors'):
        errors_text = "❌ ОШИБКИ:\n"
        errors_text += "Ошибок не найдено!\n"
        await message.answer(errors_text)

    if result.get('risks'):
        risks_text = "⚠️ РИСКИ:\n"
        risks_text += "Рисков не обнаружено!\n"
        await message.answer(risks_text)

    if result.get('recommendations'):
        rec_text = "💡 РЕКОМЕНДАЦИИ:\n"
        rec_text += "Прочитать текст, написанный маленьким шрифтом\n"
        await message.answer(rec_text)

    await state.clear()

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


