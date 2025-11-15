from aiogram import Dispatcher
from app.handlers import command_router, messages_router, callbacks_router


class BotDispatcher:
    def __init__(self):
        self.dp = Dispatcher()
        self._register_handlers()

    def _register_handlers(self):
        self.dp.include_router(command_router)
        self.dp.include_router(messages_router)
        self.dp.include_router(callbacks_router)

    def get_dispatcher(self):
        return self.dp
