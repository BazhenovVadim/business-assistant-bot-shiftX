from collections import defaultdict
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.database.unit_of_work import UnitOfWork
from app.database.models import Product, Sale


class WarehouseService:
    def __init__(self, db):
        self.db = db

    async def create_product(self, user_id: int, product_data: dict) -> Dict[str, Any]:
        async with self.db.get_uow() as uow:
            product_data["user_id"] = user_id
            product = await uow.products.create(product_data)
            return {
                "success": True,
                "data": product,
                "message": f"✅ Товар добавлен: {product.name}"
            }

    async def create_sale(self, user_id: int, sale_data: dict) -> Dict[str, Any]:
        async with self.db.get_uow() as uow:
            # Получаем товар с проверкой user_id
            product = await uow.products.get_by_id(sale_data["product_id"], user_id)
            if not product:
                return {
                    "success": False,
                    "message": "❌ Товар не найден"
                }

            if product.stock_quantity < sale_data["quantity"]:
                return {
                    "success": False,
                    "message": f"❌ Недостаточно товара. В наличии: {product.stock_quantity} шт"
                }

            sale_data["total_amount"] = sale_data["quantity"] * sale_data["unit_price"]
            sale_data["user_id"] = user_id
            sale = await uow.sales.create(sale_data)  # await

            new_stock = product.stock_quantity - sale_data["quantity"]
            await uow.products.update_stock(product.id, user_id, new_stock)

            return {
                "success": True,
                "data": sale,
                "message": f"✅ Продажа зафиксирована: {sale.quantity} шт на сумму {sale.total_amount} руб"
            }

    async def create_stock_movement(self, user_id: int, movement_data: dict) -> Dict[str, Any]:
        async with self.db.get_uow() as uow:
            product = await uow.products.get_by_id(movement_data["product_id"], user_id)
            if not product:
                return {
                    "success": False,
                    "message": "❌ Товар не найден"
                }

            movement_data["user_id"] = user_id
            movement = await uow.stock_movements.create(movement_data)

            if movement.type == "incoming":
                new_stock = product.stock_quantity + movement.quantity
            else:
                new_stock = product.stock_quantity - movement.quantity

            await uow.products.update_stock(product.id, user_id, new_stock)

            return {
                "success": True,
                "data": movement,
                "message": f"✅ Остатки обновлены: {product.name} {movement.type} {movement.quantity} шт"
            }

    async def get_warehouse_report(self, user_id: int) -> Dict[str, Any]:
        async with self.db.get_uow() as uow:
            products = await uow.products.get_all(user_id)
            low_stock = await uow.products.get_low_stock(user_id)
            week_ago = datetime.now() - timedelta(days=7)
            recent_sales = await uow.sales.get_by_period(user_id, week_ago, datetime.now())
            total_revenue = sum(sale.total_amount for sale in recent_sales)

            return {
                "total_products": len(products),
                "low_stock_count": len(low_stock),
                "low_stock_items": low_stock,
                "weekly_revenue": total_revenue,
                "total_sales_week": len(recent_sales)
            }

    async def get_sales_report(self, user_id: int, period_days: int = 30) -> Dict[str, Any]:
        """Отчет по продажам за период для конкретного пользователя"""
        async with self.db.get_uow() as uow:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            sales = await uow.sales.get_by_period(user_id, start_date, end_date)
            products = await uow.products.get_all(user_id)

            # Статистика по продажам
            total_revenue = sum(sale.total_amount for sale in sales)
            total_quantity = sum(sale.quantity for sale in sales)
            total_sales = len(sales)
            avg_sale_amount = total_revenue / total_sales if sales else 0

            # Топ товаров
            product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0, "product": None})
            for sale in sales:
                product_sales[sale.product_id]["quantity"] += sale.quantity
                product_sales[sale.product_id]["revenue"] += sale.total_amount
                product_sales[sale.product_id]["product"] = sale.product

            top_products = sorted(
                product_sales.values(),
                key=lambda x: x["revenue"],
                reverse=True
            )[:5]

            # Динамика по дням
            daily_sales = defaultdict(float)
            for sale in sales:
                date_str = sale.sale_date.strftime("%Y-%m-%d")
                daily_sales[date_str] += sale.total_amount

            return {
                "period": f"Последние {period_days} дней",
                "total_revenue": total_revenue,
                "total_quantity": total_quantity,
                "total_sales": total_sales,
                "avg_sale_amount": avg_sale_amount,
                "top_products": top_products,
                "daily_sales": dict(daily_sales),
                "sales_data": [
                    {
                        "date": sale.sale_date.strftime("%Y-%m-%d %H:%M"),
                        "product": sale.product.name,
                        "quantity": sale.quantity,
                        "amount": sale.total_amount
                    } for sale in sales[-10:]  # Последние 10 продаж
                ] if sales else []
            }

    async def get_stock_report(self, user_id: int) -> Dict[str, Any]:
        """Отчет по остаткам товара для конкретного пользователя"""
        async with self.db.get_uow() as uow:
            products = await uow.products.get_all(user_id)
            low_stock = await uow.products.get_low_stock(user_id)

            # Общая статистика
            total_products = len(products)
            total_stock_value = sum(p.stock_quantity * p.purchase_price for p in products)
            total_potential_revenue = sum(p.stock_quantity * p.selling_price for p in products)

            # Товары по категориям
            categories = defaultdict(list)
            for product in products:
                categories[product.category].append(product)

            # Товары для пополнения
            need_restock = [
                {
                    "name": p.name,
                    "current_stock": p.stock_quantity,
                    "min_stock": p.min_stock,
                    "need_quantity": max(0, p.min_stock - p.stock_quantity),
                    "category": p.category
                } for p in low_stock
            ]

            return {
                "total_products": total_products,
                "total_stock_value": total_stock_value,
                "total_potential_revenue": total_potential_revenue,
                "low_stock_count": len(low_stock),
                "categories_summary": {
                    category: {
                        "count": len(products),
                        "total_stock": sum(p.stock_quantity for p in products),
                        "total_value": sum(p.stock_quantity * p.purchase_price for p in products)
                    } for category, products in categories.items()
                },
                "need_restock": sorted(need_restock, key=lambda x: x["need_quantity"], reverse=True),
                "stock_details": [
                    {
                        "name": p.name,
                        "category": p.category,
                        "current_stock": p.stock_quantity,
                        "min_stock": p.min_stock,
                        "purchase_price": p.purchase_price,
                        "selling_price": p.selling_price,
                        "stock_value": p.stock_quantity * p.purchase_price,
                        "potential_revenue": p.stock_quantity * p.selling_price,
                        "status": "low" if p.stock_quantity <= p.min_stock else "normal"
                    } for p in products
                ]
            }

    async def get_financial_overview(self, user_id: int, period_days: int = 30) -> Dict[str, Any]:
        """Финансовый обзор для конкретного пользователя"""
        async with self.db.get_uow() as uow:
            # Период для анализа
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            # Данные о продажах
            sales = await uow.sales.get_by_period(user_id, start_date, end_date)
            products = await uow.products.get_all(user_id)

            # Расчеты
            total_revenue = sum(sale.total_amount for sale in sales)
            total_cost = sum(sale.quantity * sale.product.purchase_price for sale in sales)
            total_profit = total_revenue - total_cost
            profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

            # Текущие активы
            current_stock_value = sum(p.stock_quantity * p.purchase_price for p in products)
            potential_revenue = sum(p.stock_quantity * p.selling_price for p in products)
            potential_profit = potential_revenue - current_stock_value

            # Прогноз на следующий период (простой)
            avg_daily_revenue = total_revenue / period_days if period_days > 0 else 0
            forecast_next_period = avg_daily_revenue * period_days

            # Эффективность по категориям
            category_performance = defaultdict(lambda: {"revenue": 0, "cost": 0, "profit": 0})
            for sale in sales:
                category = sale.product.category
                cost = sale.quantity * sale.product.purchase_price
                category_performance[category]["revenue"] += sale.total_amount
                category_performance[category]["cost"] += cost
                category_performance[category]["profit"] += (sale.total_amount - cost)

            return {
                "period": f"Последние {period_days} дней",
                "revenue": {
                    "total": total_revenue,
                    "daily_avg": avg_daily_revenue,
                    "forecast": forecast_next_period
                },
                "profit": {
                    "total": total_profit,
                    "margin": profit_margin,
                    "daily_avg": total_profit / period_days if period_days > 0 else 0
                },
                "assets": {
                    "stock_value": current_stock_value,
                    "potential_revenue": potential_revenue,
                    "potential_profit": potential_profit
                },
                "efficiency": {
                    "total_sales": len(sales),
                    "avg_sale_amount": total_revenue / len(sales) if sales else 0,
                    "stock_turnover": total_revenue / current_stock_value if current_stock_value else 0
                },
                "category_performance": dict(category_performance),
                "key_metrics": [
                    {"name": "Выручка", "value": total_revenue, "format": "currency"},
                    {"name": "Прибыль", "value": total_profit, "format": "currency"},
                    {"name": "Маржа", "value": profit_margin, "format": "percent"},
                    {"name": "ROI", "value": (total_profit / current_stock_value * 100) if current_stock_value else 0,
                     "format": "percent"},
                    {"name": "Оборот склада",
                     "value": total_revenue / current_stock_value if current_stock_value else 0, "format": "number"}
                ]
            }

    # Дополнительные методы
    async def get_product_by_name(self, user_id: int, product_name: str) -> Optional[Product]:
        """Получить товар по имени для конкретного пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.products.get_by_name(product_name, user_id)

    async def get_all_products(self, user_id: int) -> List[Product]:
        """Получить все товары пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.products.get_all(user_id)

    async def get_low_stock_products(self, user_id: int) -> List[Product]:
        """Получить товары с низким запасом для пользователя"""
        async with self.db.get_uow() as uow:
            return await uow.products.get_low_stock(user_id)