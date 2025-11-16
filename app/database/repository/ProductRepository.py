from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from app.database.models import Product
from datetime import datetime


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int, user_id: int) -> Optional[Product]:
        """Найти товар по ID и пользователю"""
        result = await self.session.execute(
            select(Product).where(
                Product.id == product_id,
                Product.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, user_id: int) -> Optional[Product]:
        """Найти товар по имени и пользователю"""
        result = await self.session.execute(
            select(Product).where(
                Product.name == name,
                Product.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self, user_id: int) -> List[Product]:
        """Получить все товары пользователя"""
        result = await self.session.execute(
            select(Product).where(Product.user_id == user_id)
        )
        return result.scalars().all()

    async def create(self, product_data: dict) -> Product:
        """Создать товар"""
        product = Product(**product_data)
        self.session.add(product)
        await self.session.flush()
        await self.session.refresh(product)
        return product

    async def update_stock(self, product_id: int, user_id: int, new_quantity: int) -> Optional[Product]:
        """Обновить количество товара"""
        product = await self.get_by_id(product_id, user_id)
        if product:
            product.stock_quantity = new_quantity
            await self.session.commit()
        return product

    async def get_low_stock(self, user_id: int) -> List[Product]:
        """Получить товары с низким запасом"""
        result = await self.session.execute(
            select(Product).where(
                Product.user_id == user_id,
                Product.stock_quantity <= Product.min_stock
            )
        )
        return result.scalars().all()

    async def update(self, product_id: int, user_id: int, **kwargs) -> Optional[Product]:
        """Обновить данные товара"""
        product = await self.get_by_id(product_id, user_id)
        if not product:
            return None

        for key, value in kwargs.items():
            if hasattr(product, key) and value is not None:
                setattr(product, key, value)

        await self.session.commit()
        return product

    async def delete(self, product_id: int, user_id: int) -> bool:
        """Удалить товар"""
        product = await self.get_by_id(product_id, user_id)
        if product:
            await self.session.delete(product)
            await self.session.commit()
            return True
        return False

    async def search_by_name(self, search_term: str, user_id: int) -> List[Product]:
        """Поиск товаров по названию"""
        result = await self.session.execute(
            select(Product).where(
                Product.user_id == user_id,
                Product.name.ilike(f"%{search_term}%")
            )
        )
        return result.scalars().all()

    async def get_by_category(self, category: str, user_id: int) -> List[Product]:
        """Получить товары по категории"""
        result = await self.session.execute(
            select(Product).where(
                Product.user_id == user_id,
                Product.category == category
            )
        )
        return result.scalars().all()