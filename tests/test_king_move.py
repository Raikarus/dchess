import pytest
from app.domain.value_objects import Position, PieceType, Move
from app.domain import Board, Color
from app.domain.piece_behaviours import King, Sylph, Gryphon  # Импорт всех классов поведения фигур
from app.domain.services import PieceStrategyService


@pytest.fixture
def board():
    board = Board()
    # Позиции для всех фигур на доске с разными типами
    start_positions = {
        PieceType.KING: Position(4, 4, 1),
    }
    for piece_type, pos in start_positions.items():
        board.place_piece(piece_type, Color.WHITE, pos)
    return board


@pytest.fixture(params=[
    (PieceType.KING, King),
])
def piece_strategy_service_and_position(request, board):
    piece_type, strategy_class = request.param
    piece_behavior_map = {
        PieceType.KING: King(),
    }
    class DummyGame:
        def __init__(self, board):
            self.board = board

    game = DummyGame(board)
    service = PieceStrategyService(game=game, piece_behavior_map=piece_behavior_map)
    position = Position(4, 4, 1)
    return service, position, piece_type


def test_piece_strategy_moves(piece_strategy_service_and_position):
    service, position, piece_type = piece_strategy_service_and_position
    moves = service.get_moves_from(position)
    # Все ходы в пределах доски
    for move in moves:
        assert service.board.is_within_bounds(move.to_position)
        assert move.from_position == position
    # Проверим, что ходов больше нуля (или другое условие для каждой фигуры)
    assert len(moves) > 0

