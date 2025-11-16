from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.keyboards.menus import conversation_buttons, get_profile_settings_buttons
from app.service import UserService, ConversationService, AnalyticService

router = Router()


# --------- Quick actions ----------
@router.callback_query(F.data.startswith("quick:"))
async def quick_actions(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    await callback.message.answer(f"Выполняю действие: {action}")
    await callback.answer()


# --------- AI modes ----------
@router.callback_query(F.data == "ai:clients")
async def ai_clients(call: CallbackQuery):
    await call.message.answer("🧠 Ответы клиентам. Напишите вопрос.")
    await call.answer()


@router.callback_query(F.data == "ai:legal")
async def ai_legal(call: CallbackQuery):
    await call.message.answer("⚖️ Юридическая консультация. Напишите вопрос.")
    await call.answer()


@router.callback_query(F.data == "ai:general")
async def ai_general(call: CallbackQuery):
    await call.message.answer("💬 Общая AI-консультация. Опишите задачу.")
    await call.answer()


# --------- Marketing ----------
@router.callback_query(F.data == "mkt:ideas")
async def marketing_ideas(call: CallbackQuery):
    await call.message.answer("📣 Идеи маркетинга. Введите нишу.")
    await call.answer()


@router.callback_query(F.data == "mkt:posts")
async def marketing_posts(call: CallbackQuery):
    await call.message.answer("✍️ Тема поста?")
    await call.answer()


@router.callback_query(F.data == "mkt:plan")
async def marketing_plan(call: CallbackQuery):
    await call.message.answer("🗓 Создаю контент-план. Опишите бизнес.")
    await call.answer()


# --------- Documents ----------
@router.callback_query(F.data == "doc:contract")
async def doc_contract(call: CallbackQuery):
    await call.message.answer("📄 Создание договора. Введите детали.")
    await call.answer()


@router.callback_query(F.data == "doc:act")
async def doc_act(call: CallbackQuery):
    await call.message.answer("🧾 Создание акта. Введите данные.")
    await call.answer()


@router.callback_query(F.data == "doc:analyze")
async def doc_analyze(call: CallbackQuery):
    await call.message.answer("🔍 Отправьте файл PDF/DOCX.")
    await call.answer()


@router.callback_query(F.data == "doc:check")
async def doc_check(call: CallbackQuery):
    await call.message.answer("📑 Загрузите документ для проверки.")
    await call.answer()


# --------- Analytics ----------
@router.callback_query(F.data == "an:sales")
async def analytics_sales(call: CallbackQuery):
    await call.message.answer("📊 Период продаж?")
    await call.answer()


@router.callback_query(F.data == "an:stock")
async def analytics_stock(call: CallbackQuery):
    await call.message.answer("📦 Уточните склад или группу.")
    await call.answer()


@router.callback_query(F.data == "an:finance")
async def analytics_finance(call: CallbackQuery):
    await call.message.answer("💰 Период финансового отчета?")
    await call.answer()


# --------- Profile ----------
@router.callback_query(F.data == "profile:history")
async def profile_history(call: CallbackQuery, conversation_service):
    """
    Обработчик истории сообщений
    """
    conversations = await conversation_service.get_user_conversations(call.from_user.id)

    if not conversations:
        await call.message.answer("📝 У вас пока нет сохранённых диалогов.")
        await call.answer()
        return

    text = "📝 История диалогов:\n\n"
    for conv in conversations:
        last_msg = conv.user_message.split("\n\n")[-1]  # последнее сообщение пользователя
        preview = last_msg[:80] + ("..." if len(last_msg) > 80 else "")
        text += (
            f"🗂 #{conv.id} | {conv.category or '—'} | {conv.created_at.strftime('%d.%m %H:%M')}\n"
            f"💬 {preview}\n\n"
        )

    await call.message.answer(
        text,
        reply_markup=conversation_buttons(conversations)
    )

    await call.answer()


@router.callback_query(F.data == "profile:analytics")
async def profile_analytics(call: CallbackQuery, analytic_service):
    """
    Обработчик кнопки 'Аналитика' в меню профиля.
    """
    user_id = call.from_user.id
    daily_data = await analytic_service.get_daily_activity(user_id)
    category_data = await analytic_service.get_category_insights(user_id)

    report_lines = ["📈 **Ваша недельная активность**\n"]

    total = daily_data["total_last_week"]
    most_active = daily_data["most_active_day"]

    report_lines.append(f"• Всего консультаций за неделю: **{total}**")
    if most_active:
        day, count = most_active
        report_lines.append(f"• Самый активный день: **{day}** ({count} запросов)")

    if daily_data["daily_activity"]:
        report_lines.append("\n📅 **Активность по дням:**")
        max_count = max(daily_data["daily_activity"].values())
        for day, count in sorted(daily_data["daily_activity"].items()):
            blocks = "█" * int((count / max_count) * 10) if max_count > 0 else ""
            report_lines.append(f"{day}: {blocks} ({count})")
    if category_data:
        report_lines.append("\n📂 **Категории запросов:**")
        for category, info in category_data.items():
            examples = "; ".join(info["examples"])
            report_lines.append(f"• {category}: {info['count']} запросов")
            report_lines.append(f"  Примеры: {examples}")

    report_text = "\n".join(report_lines)
    await call.message.answer(report_text)
    await call.answer()


@router.callback_query(F.data == "profile:settings")
async def profile_settings(call: CallbackQuery, user_service):
    """
    Красивый вывод настроек профиля пользователя
    """
    user_id = call.from_user.id
    user = await user_service.get_or_create_user(user_id)

    if not user:
        await call.message.answer("❌ Пользователь не найден")
        await call.answer()
        return

    # Формируем красивый текст
    text_lines = [
        f"👤 **Личный профиль:**",
        f"• ID: {user.id}",
        f"• Никнейм: @{user.username or '—'}",
        f"• Имя: {user.first_name or '—'} {user.last_name or ''}",
        f"• Язык: {user.language}",
        "",
        f"💼 **Бизнес-профиль:**",
        f"• Тип: {user.business_type or '—'}",
        f"• Отрасль: {user.industry or '—'}",
        f"• Размер бизнеса: {user.business_size or '—'}",
        f"• Месячный доход: {user.monthly_revenue or 0} ₽",
        "",
        f"🔔 **Уведомления:** {'Включены ✅' if user.notifications_enabled else 'Выключены ❌'}",
        "",
        f"📅 **Аккаунт создан:** {user.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"🕒 **Последняя активность:** {user.last_active.strftime('%d.%m.%Y %H:%M')}",
    ]

    text = "\n".join(text_lines)

    await call.message.answer(
        text,
        reply_markup=get_profile_settings_buttons()
    )
    await call.answer()


@router.callback_query(F.data.startswith("open_dialog:"))
async def open_dialog(callback: CallbackQuery, conversation_service):
    conversation_id = int(callback.data.split(":")[1])
    conv = await conversation_service.get_conversation(conversation_id)

    if not conv:
        await callback.message.answer("❌ Этот диалог не найден или был удалён.")
        await callback.answer()
        return

    user_lines = conv.user_message.split("\n\n")
    bot_lines = conv.bot_response.split("\n\n")
    messages = []
    for u, b in zip(user_lines, bot_lines):
        messages.append(f"🧑 {u}\n🤖 {b}")

    full_text = (
        f"🗂 <b>Диалог #{conv.id}</b>\n"
        f"Категория: {conv.category or '—'}\n"
        f"Создан: {conv.created_at:%d.%m %H:%M}\n\n"
        + "\n\n".join(messages)
    )

    await callback.message.edit_text(full_text)
    await callback.answer()