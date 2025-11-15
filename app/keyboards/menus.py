from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=" Интеллект"),
                KeyboardButton(text=" Аналитика")
            ],
            [
                KeyboardButton(text=" Документы"),
                KeyboardButton(text=" Маркетинг")
            ],
            [
                KeyboardButton(text=" Быстрое"),
                KeyboardButton(text=" Поддержка")
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите раздел…"
    )



def get_intelligence_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Ответы клиентам", callback_data="ai:clients"),
                InlineKeyboardButton(text="Юр. консультации", callback_data="ai:legal")
            ],
            [
                InlineKeyboardButton(text="Общая консультация", callback_data="ai:general"),
            ]
        ]
    )

def get_marketing_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Генератор маркет. идей", callback_data="mkt:ideas"),
            ],
            [
                InlineKeyboardButton(text="Генератор постов", callback_data="mkt:posts"),
                InlineKeyboardButton(text="Контент-план 30 дней", callback_data="mkt:plan"),
            ],
            [
                InlineKeyboardButton(text="Бизнес-идеи", callback_data="biz:ideas")
            ]
        ]
    )


def get_documents_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Создать договор", callback_data="doc:contract"),
                InlineKeyboardButton(text="Создать акт", callback_data="doc:act"),
            ],
            [
                InlineKeyboardButton(text="Анализ PDF/DOCX", callback_data="doc:analyze"),
                InlineKeyboardButton(text="Проверка документа", callback_data="doc:check"),
            ]
        ]
    )


def get_analytics_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Отчет по продажам", callback_data="an:sales"),
                InlineKeyboardButton(text="Остатки товара", callback_data="an:stock"),
            ],
            [
                InlineKeyboardButton(text="Финансовый обзор", callback_data="an:finance")
            ]
        ]
    )

def get_quick_actions_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Продажи", callback_data="quick:sales"),
                InlineKeyboardButton(text="Остатки", callback_data="quick:stock"),
            ],
            [
                InlineKeyboardButton(text="Платежи", callback_data="quick:payments"),
                InlineKeyboardButton(text="Персонал", callback_data="quick:staff"),
            ]
        ]
    )


