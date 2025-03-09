# Для импорта из корневого модуля
# import sys
# sys.path.append("..")
# from main import app

from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedSeller, ReturnedSellerwoBooks, ReturnedAllsellers
from icecream import ic
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session

sellers_router = APIRouter(tags=["selller"], prefix="/seller")

# CRUD - Create, Read, Update, Delete

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи селлера в БД. Возвращает созданного селера.
# @books_router.post("/books/", status_code=status.HTTP_201_CREATED)
@sellers_router.post(
    "/", response_model=ReturnedSellerwoBooks, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):  # прописываем модель валидирующую входные данные
    # session = get_async_session() вместо этого мы используем иньекцию зависимостей DBSession
    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        **{

            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "e_mail": seller.e_mail,
            "password": seller.password
        }
    )

    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех селлеров
@sellers_router.get("/", response_model=ReturnedAllsellers)
async def get_all_sellers(session: DBSession):
    # Хотим видеть формат
    # books: [{"id": 1, "title": "blabla", ...., "year": 2023},{...}]
    query = select(Seller)  # SELECT * FROM book
    result = await session.execute(query)
    sellers = result.scalars().all()
    return {"sellers": sellers}


# Ручка для получения селлеров по его ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    if await session.get(Seller, seller_id):
        if result := await session.execute(select(Seller).where(Seller.seller_id == seller_id).options(selectinload(Seller.books))):
            return result.scalar_one_or_none()

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для удаления селлера
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    if deleted_seller:
        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о селлере
@sellers_router.put("/{seller_id}", response_model=ReturnedSellerwoBooks)
async def update_seller(seller_id: int, new_seller_data: ReturnedSellerwoBooks, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его. Заменяет то, что закомментировано выше.
    if update_seller := await session.get(Seller, seller_id):
        update_seller.first_name = new_seller_data.first_name
        update_seller.last_name = new_seller_data.last_name
        update_seller.e_mail = new_seller_data.e_mail

        await session.flush()

        return update_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
