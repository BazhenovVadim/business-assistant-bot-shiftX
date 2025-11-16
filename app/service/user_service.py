from typing import Optional, Dict, Any, List
from app.database.unit_of_work import UnitOfWork
from app.database.models import User


class UserService:
    def __init__(self, db):
        self.db = db

    async def get_or_create_user(self, user_id: int, username: str = None, first_name: str = None,
                                 last_name: str = None) -> User:
        """Получить или создать пользователя"""
        async with self.db.get_uow() as uow:
            user = await uow.users.find_by_id(user_id)

            if not user:
                user = User(
                    id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                user = await uow.users.save(user)
            else:
                await uow.users.update_last_active(user_id)

            return user

    async def update_user_profile(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновить профиль пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.users.update_profile(user_id, **kwargs)

