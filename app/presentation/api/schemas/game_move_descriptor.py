from pydantic import BaseModel


class Position(BaseModel):
    x: int
    y: int
    z: int


class MoveRequest(BaseModel):
    from_position: Position
    to_position: Position


class MoveResponse(BaseModel):
    success: bool
    message: str


class Move(BaseModel):
    from_position: Position
    to_position: Position
    attack_position: Position | None = None
