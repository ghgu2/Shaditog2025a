import pytest
from sqlalchemy import select
from src.models.books import Book
from src.models.sellers import Seller
from fastapi import status
from icecream import ic

# Тест на ручку создания книги
@pytest.mark.asyncio
async def test_create_book(async_client):
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


    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": resp_seller_id
    }

    response = await async_client.post("/api/v1/books/", json=data)
    result_data = response.json()
    resp_book_id = result_data.pop("id", None)
    assert resp_book_id, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "seller_id": resp_seller_id,
        "year": 2025,
    }


    assert response.status_code == status.HTTP_201_CREATED

# Тест на ручку создания книги с неправильной датой
@pytest.mark.asyncio
async def test_create_book_with_old_year(async_client):
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


    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
        "seller_id": resp_seller_id
    }

    response = await async_client.post("/api/v1/books/", json=data)


    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Тест на ручку создания книги с seller_id, которого нет.
@pytest.mark.asyncio
async def test_create_book_wo_seller(async_client):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
        "seller_id": 99
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

# Тест на ручку получения всех книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2025, pages=104, seller_id = new_seller.seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["books"]) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2024,
                "id": book.id,
                "seller_id": new_seller.seller_id, 
                "pages": 104,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 2025,
                "id": book_2.id,
                "seller_id": new_seller.seller_id, 
                "pages": 104,
            },
        ]
    }
    
# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2025, pages=104, seller_id = new_seller.seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2024,
        "pages": 104,
        "id": book.id,
        "seller_id": new_seller.seller_id
    }

# Тест на ручку получения одной книги c неправильным номером
@pytest.mark.asyncio
async def test_get_single_book_with_invalid_book_id(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=2025, pages=104, seller_id = new_seller.seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id + 99}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "pages": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": new_seller.seller_id
            
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages == 100
    assert res.year == 2007
    assert res.id == book.id

# Тест на ручку обновления книги c неправильным номером
@pytest.mark.asyncio
async def test_update_book_with_invalid_book_id(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id + 10}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "pages": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": new_seller.seller_id
            
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


# Тест на ручку удаления книги
@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    new_seller = Seller(
        first_name="Джордж",
        last_name="Андерсон",
        e_mail="ander2002@mail.ru",
        password="1234"
    )

    db_session.add(new_seller)
    await db_session.flush()

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0

# Тест на ручку удаления книги, которой не существует
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

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2024, pages=104, seller_id = new_seller.seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

