from pydantic import BaseModel


# Модель для запроса хода
class MoveRequest(BaseModel):
    from_x: int
    from_y: int
    from_z: int
    to_x: int
    to_y: int
    to_z: int


# Модель ответа с результатом
class MoveResponse(BaseModel):
    success: bool
    message: str
