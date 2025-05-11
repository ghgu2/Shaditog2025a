from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from .books import ReturnedBook


__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedSellerwoBooks", "ReturnedAllsellers"]


# Базовый класс "Селлер", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для валидации входящих данных. Не содержит seller_id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str


# Класс, валидирующий исходящие данные. Он уже содержит id и список книг селлера
class ReturnedSeller(BaseSeller):
    seller_id: int
    books: list[ReturnedBook]

# Класс, валидирующий исходящие данные. Он уже содержит id, но не содержит сниги селлераэто сделано ReturnedAllsellers
class ReturnedSellerwoBooks(BaseSeller):
    seller_id: int

# Класс для возврата массива объектов "Селлеров"
class ReturnedAllsellers(BaseModel):
    sellers: list[ReturnedSellerwoBooks]
