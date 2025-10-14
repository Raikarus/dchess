import pytest
from app.domain.pieces import Sylf, Gryphon
from app.domain import Board, Position, Color


@pytest.fixture
def board():
    b = Board(12, 8, 3)
    sylf_start = range(0, 12, 2)
    gryphon_start = [2, 10]
    b.register_start_positions("sylf", Color.WHITE, [Position(x, 1, 2) for x in sylf_start])
    b.register_start_positions("sylf", Color.BLACK, [Position(x, 6, 2) for x in sylf_start])
    b.register_start_positions("gryphon", Color.WHITE, [Position(x, 0, 2) for x in gryphon_start])
    b.register_start_positions("gryphon", Color.BLACK, [Position(x, 7, 2) for x in gryphon_start])
    return b


def make_piece(piece_cls, position, color):
    p = piece_cls()
    p.position = position
    p.color = color
    return p


@pytest.fixture
def piece(request):
    piece_cls = getattr(request, 'param')[0]
    position = getattr(request, 'param')[1]
    color = getattr(request, 'param')[2]
    return make_piece(piece_cls, position, color)

@pytest.mark.parametrize("piece", [
    (Sylf, Position(11, 7, 2), Color.WHITE),
    (Sylf, Position(0, 0, 2), Color.BLACK),
    (Gryphon, Position(0, 0, 2), Color.WHITE),
    (Gryphon, Position(0, 0, 1), Color.WHITE)
], indirect=True)
def test_no_moves_outside_board(board, piece):
    board.place_piece(piece)
    moves = piece.possible_moves(board)
    for move in moves:
        assert 0 <= move.to_position.x < board.width
        assert 0 <= move.to_position.y < board.height
        assert 0 <= move.to_position.z < board.depth


@pytest.mark.parametrize("piece, enemy_pos", [
    ((Sylf, Position(1, 1, 2), Color.WHITE), Position(1, 2, 2)),
    ((Sylf, Position(1, 1, 2), Color.WHITE), Position(1, 1, 1)),
    ((Sylf, Position(1, 1, 2), Color.BLACK), Position(1, 0, 2)),
    ((Sylf, Position(1, 1, 2), Color.BLACK), Position(1, 1, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(6, 7, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(7, 6, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(7, 2, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(6, 1, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(2, 1, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(1, 2, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(1, 6, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(2, 7, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(3, 3, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(5, 5, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(3, 5, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(5, 3, 1)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(3, 3, 2)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(5, 5, 2)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(3, 5, 2)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(5, 3, 2))
], indirect=["piece"])
def test_can_capture_opponent(board, piece, enemy_pos):
    enemy = make_piece(type(piece), enemy_pos, Color.BLACK if piece.color == Color.WHITE else Color.WHITE)
    board.place_piece(piece)
    board.place_piece(enemy)
    moves = piece.possible_moves(board)
    capture_moves = [m for m in moves if m.is_capture and m.to_position == enemy_pos]
    assert capture_moves, f"{type(piece).__name__} должен иметь возможность взять фигуру противника"


@pytest.mark.parametrize("piece, friendly_pos", [
    ((Sylf, Position(1, 1, 2), Color.WHITE), Position(1, 2, 2)),
    ((Sylf, Position(1, 1, 2), Color.WHITE), Position(1, 1, 1)),
    ((Sylf, Position(1, 1, 2), Color.BLACK), Position(1, 0, 2)),
    ((Sylf, Position(1, 1, 2), Color.BLACK), Position(1, 1, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(6, 7, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(7, 6, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(7, 2, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(6, 3, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(2, 1, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(1, 2, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(1, 6, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(2, 7, 2)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(3, 3, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(5, 5, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(3, 5, 1)),
    ((Gryphon, Position(4, 4, 2), Color.WHITE), Position(5, 3, 1)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(3, 3, 2)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(5, 5, 2)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(3, 5, 2)),
    ((Gryphon, Position(4, 4, 1), Color.WHITE), Position(5, 3, 2))
], indirect=["piece"])
def test_cannot_capture_own_piece(board, piece, friendly_pos):
    friend = make_piece(type(piece), friendly_pos, piece.color)
    board.place_piece(piece)
    board.place_piece(friend)
    moves = piece.possible_moves(board)
    capture_moves = [m for m in moves if m.is_capture and m.to_position == friendly_pos]
    assert not capture_moves, f"{type(piece).__name__} не должен иметь возможность взять своего"


# Тест: фигура может делать специфические ходы (передаём старт и ожидаемые позиции)
@pytest.mark.parametrize("piece, expected_positions", [
    ((Sylf, Position(1, 1, 1), Color.WHITE), [Position(0, 1, 2), Position(2, 1, 2), Position(1, 1, 2)]),
    ((Sylf, Position(1, 1, 1), Color.BLACK), [Position(0, 6, 2), Position(2, 6, 2), Position(1, 1, 2)])
], indirect=["piece"])
def test_specific_moves(board, piece, expected_positions):
    board.place_piece(piece)
    moves = piece.possible_moves(board)
    name = board.get_start_positions_for_piece("sylf", Color.BLACK)
    moves_positions = [m.to_position for m in moves]
    for pos in expected_positions:
        assert pos in moves_positions, f"Ожидался ход на {pos} для {type(piece).__name__}"


# Тест на возможность повышения фигуры
@pytest.mark.parametrize("piece, can_promote", [
    ((Sylf, Position(0, 0, 2), Color.BLACK), False),
])
def test_promotion_ability(piece, can_promote):
    p = make_piece(piece[0], piece[1], piece[2])
    assert p.can_promote() == can_promote, f"Проверка способности превращения для {type(p).__name__}"
