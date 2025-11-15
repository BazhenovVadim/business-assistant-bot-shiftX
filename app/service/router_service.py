from app.service.llm_service import LLMService


class RouterService:
    def __init__(self, llm: LLMService):
        self.llm = llm

    async def classify(self, message: str) -> str:
        # заглушка
        if "договор" in message.lower() or "юрист" in message.lower():
            return "legal"
        if "реклама" in message.lower() or "маркет" in message.lower():
            return "marketing"
        if "отчёт" in message.lower() or "финанс" in message.lower():
            return "finance"

        return "general"
