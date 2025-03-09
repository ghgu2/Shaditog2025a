import pytest
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from fastapi import status
from icecream import ic

# Тест на ручку создания селлера
@pytest.mark.asyncio
async def test_create_seller(async_client):
    new_seller = {
        "first_name": "Джордж",
        "last_name": "Мартин",
        "e_mail": "martin200@gmail.com",
        "password": "never6"
        }
    response1 = await async_client.post("/api/v1/seller/", json=new_seller)
    assert response1.status_code == status.HTTP_201_CREATED

    result_data1 = response1.json()

    resp_seller_id = result_data1.pop("seller_id", None)

    assert ("password" in result_data1.keys()) == False, "Password is returned from endpoint"
    assert resp_seller_id, "Seller id not returned from endpoint"

    assert result_data1 ==  {
        "first_name": "Джордж",
        "last_name": "Мартин",
        "e_mail": "martin200@gmail.com",
    }

# Ручка, возвращающая всех селлеров
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    # Создаем селлеров вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    new_seller1 = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )
    new_seller2 = Seller(
        first_name="Марк",
        last_name="Аврелий",
        e_mail="Mark2003@mail.ru",
        password="1234asd"
    )

    db_session.add_all([new_seller1, new_seller2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["sellers"]) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {
                "first_name": "Джордж",
                "last_name": "Андерсон",
                "e_mail": "ander2002@mail.ru",
                "seller_id": new_seller1.seller_id,
            },
            {
                "first_name": "Марк",
                "last_name": "Аврелий",
                "e_mail": "Mark2003@mail.ru",
                "seller_id": new_seller2.seller_id,
            },
        ]
    }

# Ручка для получения селлера по его ИД
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    new_seller1 = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )
    new_seller2 = Seller(
        first_name="Марк",
        last_name="Аврелий",
        e_mail="Mark2003@mail.ru",
        password="1234asd"
    )

    db_session.add_all([new_seller1, new_seller2])
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller1.seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2025, pages=104, seller_id = new_seller1.seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{new_seller1.seller_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "seller_id": new_seller1.seller_id,
        "first_name": "Джордж",
        "last_name": "Андерсон",
        "e_mail": "ander2002@mail.ru",
        "books": [
            {   "id": book.id,
                "author": "Pushkin",
                "title": "Eugeny Onegin",
                "year": 2024,
                "pages": 104,
                "seller_id": new_seller1.seller_id
            },
                       {   "id": book_2.id,
                "author": "Lermontov",
                "title": "Mziri",
                "year": 2025,
                "pages": 104,
                "seller_id": new_seller1.seller_id
            },
        ]
    }

# Ручка для получения селлера по его ИД с неправильным номером
@pytest.mark.asyncio
async def test_get_single_seller_with_invalid_seller_id(db_session, async_client):
    new_seller1 = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )
    new_seller2 = Seller(
        first_name="Марк",
        last_name="Аврелий",
        e_mail="Mark2003@mail.ru",
        password="1234asd"
    )

    db_session.add_all([new_seller1, new_seller2])
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller1.seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2025, pages=104, seller_id = new_seller1.seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{-1}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

# Ручка для обвнолвения информации о селлера
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{new_seller.seller_id}",
        json={
            "first_name":"Джорд",
            "last_name":"Андерсо",
            "e_mail":"ander2002@mail.r",
            "password":"123",
            "seller_id":new_seller.seller_id + 1
            
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, new_seller.seller_id)
    assert res.first_name == "Джорд"
    assert res.last_name == "Андерсо"
    assert res.e_mail == "ander2002@mail.r"
    assert res.seller_id == new_seller.seller_id

# Ручка для обвнолвения информации о селлере с неправильным номером
@pytest.mark.asyncio
async def test_update_seller_with_invalid_seller_id(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{new_seller.seller_id + 1}",
        json={
            "first_name":"Джорд",
            "last_name":"Андерсо",
            "e_mail":"ander2002@mail.r",
            "password":"123",
            "seller_id":new_seller.seller_id + 1
            
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку удаления селлера
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{new_seller.seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_books = await db_session.execute(select(Seller))
    res = all_books.scalars().all()

    assert len(res) == 0

# # Тест на ручку удаления селлера, которого не существует
@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{new_seller.seller_id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND