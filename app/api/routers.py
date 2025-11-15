from fastapi import APIRouter, Request

from app.service import UserService

chat_router = APIRouter(prefix="/chat", tags=["chat"])

telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])

health_router = APIRouter(tags=["health"])


@health_router.get("/health")
async def health():
    return {"status": "ok"}


@telegram_router.post("/webhook")
async def telegram_webhook(update: dict, request: Request):
    chat_id = update["message"]["chat"]["id"]
    text = update["message"].get("text")

    # ищем / создаём пользователя
    user_service = request.app.state.user_service
    user = await user_service.get_or_create_user(chat_id)

    # прокидываем в обработчик сообщений
    reply, scenario = await process_message(user.id, text)

    return {"status": "ok"}


@chat_router.post("")
async def chat_api(body: dict):
    user_id = body["user_id"]
    message = body["message"]

    reply, scenario = await process_message(user_id, message)

    return {
        "reply": reply,
        "scenario": scenario
    }
