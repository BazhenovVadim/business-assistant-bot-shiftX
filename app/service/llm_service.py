class LLMService:
    def __init__(self):
        pass

    async def generate(self, prompt: str) -> dict:
        # Заглушка — имитация работы LLM
        return {
            "title": "Идея для продвижения",
            "description": "Создайте серию коротких видео о том, как работает ваш бизнес.",
            "examples": [
                "«Как мы готовим заказы за 60 секунд»",
                "«Топ-3 проблемы клиентов и как мы их решаем»"
            ]
        }

    async def generate_raw(self, prompt: str) -> str:
        return f"[LLM RAW ответ на запрос: {prompt[:60]}...]"

    async def generate_json(self, prompt: str) -> dict:
        # Метод специально для DocumentAnalyzer
        result = await self.generate(prompt)
        # В реальном LLM здесь может быть парсинг JSON
        return {
            "summary": result["title"],
            "risks": ["Нет явных рисков"],  # заглушка
            "recommendations": result["examples"]
        }
