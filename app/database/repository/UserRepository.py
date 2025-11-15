from typing import Optional

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, user_id: int) -> Optional[User]:
        """Найти пользователя по ID """
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def save(self, user: User) -> User:
        """Сохранить пользователя (аналог JPA save)"""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_profile(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновить профиль пользователя"""
        user = await self.find_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await self.session.commit()
        return user

    async def update_last_active(self, user_id: int) -> None:
        """Обновить время последней активности"""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(last_active=func.now())
        )
        await self.session.commit()