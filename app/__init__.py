# app/__init__.py
"""
Business Assistant Bot
"""

__version__ = "0.1.0"


# Инициализация приложения
async def initialize():
    """Инициализация всего приложения"""
    from .database import db
    await db.init()
    print("✅ Приложение инициализировано")
