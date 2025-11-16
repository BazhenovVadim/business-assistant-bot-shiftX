from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from fastapi import Depends

from app.database.db import logger
from app.handlers.states import States
from app.keyboards.menus import conversation_buttons, get_profile_settings_buttons, get_analytics_menu
from app.dependencies import (
    get_user_service,
    get_conversation_service,
    get_analytic_service, get_warehouse_service
)
from app.service import UserService, ConversationService, AnalyticService, WarehouseService

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
async def start_marketing_ideas(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "🎯 <b>Генератор маркетинговых идей</b>\n\n"
        "📝 Введите вашу нишу (чем занимаетесь):",
        reply_markup=None
    )
    await state.set_state(States.waiting_niche)
    await call.answer()


@router.callback_query(F.data == "mkt:posts")
async def start_post_generator(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "✍️ <b>Генератор постов</b>\n\n"
        "📝 О чем будет пост?",
        reply_markup=None
    )
    await state.set_state(States.waiting_post_topic)
    await call.answer()


@router.callback_query(F.data == "mkt:plan")
async def start_content_plan(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "🗓️ <b>Контент-план на 30 дней</b>\n\n"
        "📝 Опишите ваш бизнес кратко:",
        reply_markup=None
    )
    await state.set_state(States.waiting_business_description)
    await call.answer()


@router.callback_query(F.data == "mkt:business_ideas")
async def generate_business_ideas(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "💡 Генератор бизнес-идей\n\n"
        "🎯 В чем вы разбираетесь? Какие у вас интересы?",
        reply_markup=None
    )
    await state.set_state(States.waiting_niche)
    await call.answer()


# --------- Documents ----------
@router.callback_query(F.data == "doc:contract")
async def start_contract_creation(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "📄 <b>Создание договора</b>\n\n"
        "Опишите детали договора:\n"
        "• Стороны договора\n• Предмет договора\n• Сроки\n• Условия оплаты\n• Особые условия",
        reply_markup=None
    )
    await state.set_state(States.waiting_contract_details)
    await call.answer()


@router.callback_query(F.data == "doc:act")
async def start_act_creation(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "🧾 <b>Создание акта</b>\n\n"
        "Введите данные для акта:\n"
        "• Наименование работ/услуг\n• Стоимость\n• Сроки выполнения\n• Участники",
        reply_markup=None
    )
    await state.set_state(States.waiting_act_data)
    await call.answer()



@router.callback_query(F.data == "doc:analyze")
async def doc_analyze(call: CallbackQuery):
    await call.message.answer("🔍 Отправьте файл PDF/DOCX.")
    await call.answer()


@router.callback_query(F.data == "doc:check")
async def start_document_check(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "📑 <b>Проверка документа</b>\n\n"
        "Введите текст документа для проверки на ошибки и риски:",
        reply_markup=None
    )
    await state.set_state(States.waiting_document_text)
    await call.answer()

# --------- Analytics ----------
@router.callback_query(F.data == "an:sales")
async def handle_sales_report(callback: CallbackQuery,
                              warehouse_service: WarehouseService = Depends(get_warehouse_service)):
    """Обработчик отчета по продажам"""
    try:
        user_id = callback.from_user.id
        report = await warehouse_service.get_sales_report(user_id, 7)

        # Первое сообщение - основная статистика
        text = f"📈 <b>ОТЧЕТ ПО ПРОДАЖАМ</b> (за 7 дней)\n\n"
        text += f"💰 <b>Выручка:</b> {report['total_revenue']:,.0f} руб\n"
        text += f"📦 <b>Продано:</b> {report['total_quantity']} шт\n"
        text += f"🛒 <b>Транзакций:</b> {report['total_sales']}\n"
        text += f"📊 <b>Средний чек:</b> {report['avg_sale_amount']:,.0f} руб\n"

        await callback.message.edit_text(text, reply_markup=get_analytics_menu())

        # Второе сообщение - топ товаров
        if report['top_products']:
            top_text = "🏆 <b>ТОП ТОВАРОВ ПО ВЫРУЧКЕ:</b>\n\n"
            for i, product_data in enumerate(report['top_products'], 1):
                product = product_data['product']
                top_text += f"{i}. {product.name}\n"
                top_text += f"   💰 {product_data['revenue']:,.0f} руб\n"
                top_text += f"   📦 {product_data['quantity']} шт\n\n"

            await callback.message.answer(top_text)
        else:
            await callback.message.answer("📝 <i>Пока нет данных о продажах</i>")

        # Третье сообщение - последние продажи если есть
        if report.get('sales_data'):
            recent_text = "🕒 <b>ПОСЛЕДНИЕ ПРОДАЖИ:</b>\n\n"
            for sale in report['sales_data'][:5]:  # Последние 5 продаж
                recent_text += f"📅 {sale['date']}\n"
                recent_text += f"🛒 {sale['product']} - {sale['quantity']} шт\n"
                recent_text += f"💰 {sale['amount']:,.0f} руб\n\n"

            await callback.message.answer(recent_text)

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in sales report: {str(e)}", exc_info=True)
        # Короткое сообщение об ошибке для alert
        await callback.answer("❌ Ошибка загрузки отчета", show_alert=True)
        # Полная ошибка в отдельном сообщении
        error_msg = f"⚠️ <b>Произошла ошибка:</b>\n<code>{str(e)[:500]}</code>"
        await callback.message.answer(error_msg)


@router.callback_query(F.data == "an:stock")
async def handle_stock_report(callback: CallbackQuery,
                              warehouse_service: WarehouseService = Depends(get_warehouse_service)):
    """Обработчик отчета по остаткам"""
    try:
        report = await warehouse_service.get_stock_report(callback.from_user.id)

        text = f"📦 <b>ОСТАТКИ ТОВАРА</b>\n\n"
        text += f"📊 <b>Товаров:</b> {report['total_products']}\n"
        text += f"💰 <b>Стоимость запасов:</b> {report['total_stock_value']:,.0f} руб\n"
        text += f"⚠️  <b>Низкий запас:</b> {report['low_stock_count']} позиций\n\n"

        if report['need_restock']:
            text += "🚨 <b>СРОЧНО ПОПОЛНИТЬ:</b>\n"
            for item in report['need_restock'][:3]:
                text += f"• {item['name']} - {item['current_stock']} шт (нужно +{item['need_quantity']})\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_analytics_menu()
        )
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


@router.callback_query(F.data == "an:finance")
async def handle_financial_overview(callback: CallbackQuery,
                                    warehouse_service: WarehouseService = Depends(get_warehouse_service)):
    """Обработчик финансового обзора"""
    try:
        report = await warehouse_service.get_financial_overview(callback.from_user.id, 30)

        text = f"💰 <b>ФИНАНСОВЫЙ ОБЗОР</b> (за 30 дней)\n\n"
        text += f"📈 <b>Выручка:</b> {report['revenue']['total']:,.0f} руб\n"
        text += f"💵 <b>Прибыль:</b> {report['profit']['total']:,.0f} руб\n"
        text += f"🎯 <b>Маржа:</b> {report['profit']['margin']:.1f}%\n\n"
        text += f"🏭 <b>Активы:</b> {report['assets']['stock_value']:,.0f} руб\n"
        text += f"📊 <b>Оборот:</b> {report['efficiency']['stock_turnover']:.1f}\n"

        if report['category_performance']:
            text += "\n📂 <b>Эффективность по категориям:</b>\n"
            for category, perf in list(report['category_performance'].items())[:3]:
                margin = (perf['profit'] / perf['revenue'] * 100) if perf['revenue'] else 0
                text += f"• {category}: {perf['profit']:,.0f} руб (маржа {margin:.1f}%)\n"

        await callback.message.edit_text(
            text,
            reply_markup=get_analytics_menu()
        )
        await callback.answer()

    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)


# --------- Profile ----------
@router.callback_query(F.data == "profile:history")
async def profile_history(
        call: CallbackQuery,
        conversation_service: ConversationService = Depends(get_conversation_service)
):
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
async def profile_analytics(
        call: CallbackQuery,
        analytic_service: AnalyticService = Depends(get_analytic_service)
):
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
async def profile_settings(
        call: CallbackQuery,
        user_service: UserService = Depends(get_user_service)
):
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


# --------- Profile Editing ----------
@router.callback_query(F.data == "profile:edit_personal")
async def edit_personal_profile(
        call: CallbackQuery,
        state: FSMContext,
        user_service: UserService = Depends(get_user_service)
):
    """Редактирование личных данных"""
    user = await user_service.get_or_create_user(call.from_user.id)

    await call.message.answer(
        "✏️ <b>Редактирование личных данных</b>\n\n"
        f"Текущие данные: {user.first_name or '—'} {user.last_name or '—'}\n\n"
        "Отправьте информацию в формате:\n"
        "<code>Имя Фамилия</code>\n\n"
        "Пример: <code>Иван Иванов</code>",
        parse_mode="HTML"
    )
    await state.set_state("waiting_personal_data")
    await call.answer()


@router.callback_query(F.data == "profile:edit_notifications")
async def edit_notifications(call: CallbackQuery, user_service: UserService = Depends(get_user_service)):
    """Переключение уведомлений"""
    user = await user_service.get_or_create_user(call.from_user.id)

    # Переключаем уведомления
    new_status = not user.notifications_enabled
    await user_service.update_user_profile(
        call.from_user.id,
        notifications_enabled=new_status
    )

    status_text = "включены ✅" if new_status else "выключены ❌"
    await call.message.answer(f"🔔 Уведомления {status_text}")
    await call.answer(f"Уведомления {status_text}")


@router.callback_query(F.data == "profile:edit_business")
async def edit_business_profile(call: CallbackQuery, state: FSMContext):
    """Редактирование бизнес-профиля"""
    await call.message.answer(
        "💼 <b>Редактирование бизнес-профиля</b>\n\n"
        "Выберите что хотите изменить:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏢 Тип бизнеса", callback_data="business:edit_type")],
                [InlineKeyboardButton(text="📊 Отрасль", callback_data="business:edit_industry")],
                [InlineKeyboardButton(text="👥 Размер бизнеса", callback_data="business:edit_size")],
                [InlineKeyboardButton(text="💰 Месячный доход", callback_data="business:edit_revenue")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile:settings")]
            ]
        )
    )
    await call.answer()


@router.callback_query(F.data == "profile:edit_notifications")
async def edit_notifications(call: CallbackQuery, user_service: UserService = Depends(get_user_service)):
    """Переключение уведомлений"""
    user = await user_service.get_or_create_user(call.from_user.id)

    # Переключаем уведомления
    new_status = not user.notifications_enabled
    await user_service.update_user_profile(
        call.from_user.id,
        notifications_enabled=new_status
    )

    status_text = "включены ✅" if new_status else "выключены ❌"
    await call.message.answer(f"🔔 Уведомления {status_text}")
    await call.answer(f"Уведомления {status_text}")


@router.callback_query(F.data == "profile:back")
async def back_to_profile(call: CallbackQuery, user_service: UserService = Depends(get_user_service)):
    """Возврат к просмотру профиля"""
    user_id = call.from_user.id
    user = await user_service.get_or_create_user(user_id)

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

    await call.message.edit_text(
        text,
        reply_markup=get_profile_settings_buttons()
    )
    await call.answer()


@router.callback_query(F.data == "profile:edit_business")
async def edit_business_profile(
        call: CallbackQuery,
        user_service: UserService = Depends(get_user_service)
):
    """Редактирование бизнес-профиля"""
    # Получаем текущие данные пользователя
    user = await user_service.get_or_create_user(call.from_user.id)

    current_profile = (
        f"💼 <b>Текущий бизнес-профиль:</b>\n\n"
        f"🏢 Тип: {user.business_type or '—'}\n"
        f"📊 Отрасль: {user.industry or '—'}\n"
        f"👥 Размер: {user.business_size or '—'}\n"
        f"💰 Доход: {user.monthly_revenue or 0:,} ₽\n\n"
        f"<b>Что хотите изменить?</b>"
    )

    await call.message.edit_text(
        current_profile,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🏢 Тип бизнеса", callback_data="business:edit_type")],
                [InlineKeyboardButton(text="📊 Отрасль", callback_data="business:edit_industry")],
                [InlineKeyboardButton(text="👥 Размер бизнеса", callback_data="business:edit_size")],
                [InlineKeyboardButton(text="💰 Месячный доход", callback_data="business:edit_revenue")],
                [InlineKeyboardButton(text="⬅️ Назад в профиль", callback_data="profile:settings")]
            ]
        )
    )
    await call.answer()


@router.callback_query(F.data == "business:edit_type")
async def edit_business_type(call: CallbackQuery):
    """Редактирование типа бизнеса"""
    await call.message.edit_text(
        "🏢 <b>Выберите тип бизнеса:</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="ИП", callback_data="bus_type:ИП")],
                [InlineKeyboardButton(text="ООО", callback_data="bus_type:ООО")],
                [InlineKeyboardButton(text="Самозанятый", callback_data="bus_type:Самозанятый")],
                [InlineKeyboardButton(text="Фрилансер", callback_data="bus_type:Фрилансер")],
                [InlineKeyboardButton(text="АО", callback_data="bus_type:АО")],
                [InlineKeyboardButton(text="НКО", callback_data="bus_type:НКО")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile:edit_business")]
            ]
        )
    )
    await call.answer()


@router.callback_query(F.data == "profile:view_business")
async def view_business_profile(
        call: CallbackQuery,
        user_service: UserService = Depends(get_user_service)
):
    """Просмотр бизнес-профиля"""
    user = await user_service.get_or_create_user(call.from_user.id)

    profile_text = (
        f"💼 Ваш бизнес-профиль:\n\n"
        f"🏢 Тип: {user.business_type or '—'}\n"
        f"📊 Отрасль: {user.industry or '—'}\n"
        f"👥 Размер: {user.business_size or '—'}\n"
        f"💰 Доход: {user.monthly_revenue or 0:,} ₽\n\n"
        f"<i>Обновлено: {user.last_active.strftime('%d.%m.%Y %H:%M')}</i>"
    )

    await call.message.edit_text(
        profile_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✏️ Редактировать", callback_data="profile:edit_business")],
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="profile:settings")]
            ]
        )
    )
    await call.answer()


@router.callback_query(F.data.startswith("open_dialog:"))
async def open_dialog(
        callback: CallbackQuery,
        conversation_service: ConversationService = Depends(get_conversation_service)
):
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
