import pytest
from app.domain.color import Color
from app.domain.position import Position
from app.domain.value_objects import PieceType
from app.domain.board import Board
from app.domain.aggregates import Game, GameState


def test_game_initialization():
    players = ["Alice", "Bob"]
    game = Game(players)

    assert game.players == players
    assert game.current_turn == Color.WHITE
    assert game.state == GameState.ONGOING
    assert game.current_player == players[0]
    assert isinstance(game.board, Board)
    assert len(game.move_history) == 0


def test_board_initialization_and_placement():
    players = ["Alice", "Bob"]
    game = Game(players)
    board = game.board

    # Проверка габаритов доски
    geometry = board.geometry
    assert geometry.width == 12
    assert geometry.height == 8
    assert geometry.depth == 3

    # Проверка, что фигуры размещены в стартовых позициях
    for (piece_type, color), positions in board.start_positions.items():
        for pos in positions:
            piece = board.get_piece_at(pos)
            assert piece is not None
            assert piece[0] == piece_type
            assert piece[1] == color


def test_board_is_empty_and_within_bounds():
    board = Board()
    pos_inside = Position(0, 0, 0)
    pos_outside = Position(-1, 0, 0)

    assert board.is_within_bounds(pos_inside)
    assert not board.is_within_bounds(pos_outside)
    assert board.is_empty(pos_inside)


def test_place_and_get_piece():
    board = Board()
    pos = Position(1, 1, 1)
    piece_type = PieceType.KING
    color = Color.WHITE

    assert board.is_empty(pos)
    board.place_piece(piece_type, color, pos)

    piece = board.get_piece_at(pos)
    assert piece == (piece_type, color)
    assert not board.is_empty(pos)


def test_game_turn_switch():
    players = ["Alice", "Bob"]
    game = Game(players)

    assert game.current_turn == Color.WHITE
    # ДОБАВИТЬ
    # game.switch_turn()
    # assert game.current_turn == Color.BLACK
