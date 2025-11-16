from aiogram.fsm.state import State, StatesGroup
class States(StatesGroup):
    waiting_niche = State()
    waiting_goal = State()
    waiting_platform = State()
    waiting_custom_request = State()

    # Для постов
    waiting_post_topic = State()
    waiting_post_style = State()

    # Для контент-плана
    waiting_business_description = State()
    waiting_content_theme = State()

    # Для бизнес-идей
    waiting_business_interests = State()

    waiting_contract_details = State()

    # Для создания акта
    waiting_act_data = State()

    # Для проверки документа
    waiting_document_text = State()

    # Для анализа документа (файл)
    waiting_document_file = State()