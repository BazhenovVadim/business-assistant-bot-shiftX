from aiogram import Router, F
from aiogram.types import CallbackQuery

router = Router()


@router.callback_query(F.data.startswith("quick:"))
async def quick_actions(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    await callback.answer()

    await callback.message.answer(f"Выполняю действие: {action}")


@router.callback_query(F.data == "ai:clients")
async def ai_clients(call: CallbackQuery):
    await call.message.answer("🧠 Режим: Ответы клиентам. Напишите вопрос клиента.")
    await call.answer()


@router.callback_query(F.data == "ai:legal")
async def ai_legal(call: CallbackQuery):
    await call.message.answer("⚖️ Юридическая консультация. Напишите вопрос.")
    await call.answer()


@router.callback_query(F.data == "ai:general")
async def ai_general(call: CallbackQuery):
    await call.message.answer("💬 Общая AI-консультация. Опишите, что нужно.")
    await call.answer()


@router.callback_query(F.data == "mkt:ideas")
async def marketing_ideas(call: CallbackQuery):
    await call.message.answer("📣 Генератор маркетинговых идей. Введите нишу.")
    await call.answer()


@router.callback_query(F.data == "mkt:posts")
async def marketing_posts(call: CallbackQuery):
    await call.message.answer("✍️ Генератор постов. Что за тема поста?")
    await call.answer()


@router.callback_query(F.data == "mkt:plan")
async def marketing_plan(call: CallbackQuery):
    await call.message.answer("🗓 Создаю контент-план. Опишите ваш бизнес.")
    await call.answer()


@router.callback_query(F.data == "biz:ideas")
async def business_ideas(call: CallbackQuery):
    await call.message.answer("🚀 Генератор бизнес-идей. Введите ваш запрос.")
    await call.answer()


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
    await call.message.answer("🔍 Отправьте PDF/DOCX для анализа.")
    await call.answer()


@router.callback_query(F.data == "doc:check")
async def doc_check(call: CallbackQuery):
    await call.message.answer("📑 Загрузите документ для проверки.")
    await call.answer()


@router.callback_query(F.data == "an:sales")
async def analytics_sales(call: CallbackQuery):
    await call.message.answer("📊 Отчет по продажам. За какой период?")
    await call.answer()


@router.callback_query(F.data == "an:stock")
async def analytics_stock(call: CallbackQuery):
    await call.message.answer("📦 Остатки товара. Уточните склад или группу.")
    await call.answer()


@router.callback_query(F.data == "an:finance")
async def analytics_finance(call: CallbackQuery):
    await call.message.answer("💰 Финансовый обзор. Какой период рассчитать?")
    await call.answer()


@router.callback_query(F.data == "quick:sales")
async def quick_sales(call: CallbackQuery):
    await call.message.answer("⚡ Быстрые продажи. Что нужно найти?")
    await call.answer()


@router.callback_query(F.data == "quick:stock")
async def quick_stock(call: CallbackQuery):
    await call.message.answer("⚡ Быстрые остатки. Введите SKU или название.")
    await call.answer()


@router.callback_query(F.data == "quick:payments")
async def quick_payments(call: CallbackQuery):
    await call.message.answer("⚡ Платежи. Введите дату или контрагента.")
    await call.answer()


@router.callback_query(F.data == "quick:staff")
async def quick_staff(call: CallbackQuery):
    await call.message.answer("⚡ Персонал. Какой сотрудник вас интересует?")
    await call.answer()
