import pytest
from app.domain.aggregates.game_manager import GameManager, GameState
from app.domain.color import Color
from app.domain.position import Position
from app.domain.move import Move


@pytest.fixture
def game_manager():
    players = ["Alice", "Bob"]
    gm = GameManager(players)
    return gm


def test_initialize_board_has_starting_pieces(game_manager):
    # Проверяем, что доска инициализирована и фигуры расставлены
    board = game_manager.board
    # Например, в стартовых позициях есть фигуры sylf и gryphon
    start_positions_white = board.get_start_positions_for_piece("sylf", Color.WHITE)
    assert len(start_positions_white) > 0
    start_positions_black = board.get_start_positions_for_piece("sylf", Color.BLACK)
    assert len(start_positions_black) > 0


def test_switch_turn_changes_current_turn(game_manager):
    initial_turn = game_manager.current_turn
    game_manager.switch_turn()
    assert game_manager.current_turn != initial_turn
    game_manager.switch_turn()
    assert game_manager.current_turn == initial_turn


def test_make_move_invalid_piece_returns_false(game_manager):
    # Попытка сделать ход с пустой позиции
    invalid_move = Move(from_position=Position(0,0,0), to_position=Position(1,1,1))
    result = game_manager.make_move(invalid_move)
    assert result is False


def test_make_move_wrong_color_returns_false(game_manager):
    # Сделаем ход, когда на from_position есть фигура, но другого цвета
    # Изначально ход белых — попытаемся ходить чёрными
    pos = game_manager.board.get_start_positions_for_piece("sylf", Color.WHITE)[0]
    move = Move(from_position=pos, to_position=Position(pos.x, pos.y+1, pos.z))
    game_manager.current_turn = Color.BLACK  # сменим цвет текущего игрока, чтобы ход попытался выполнить чёрный
    result = game_manager.make_move(move)
    assert result is False


def test_make_move_valid_moves_and_undo(game_manager):
    # Выберем фигуру белых с доступными ходами
    pos = game_manager.board.get_start_positions_for_piece("sylf", Color.WHITE)[0]
    valid_moves = game_manager.get_valid_moves(pos)
    assert len(valid_moves) > 0

    move = valid_moves[0]
    result = game_manager.make_move(move)
    assert result is True
    assert game_manager.move_history[-1] == move

    # Проверка смены хода
    assert game_manager.current_turn == Color.BLACK

    # Отмена хода
    game_manager.undo_move()
    assert game_manager.current_turn == Color.WHITE
    assert len(game_manager.move_history) == 0
    # Фигура должна быть на месте
    piece_after_undo = game_manager.board.get_piece_at(pos)
    assert piece_after_undo is not None


def test_get_valid_moves_returns_only_legal_moves(game_manager):
    pos = game_manager.board.get_start_positions_for_piece("sylf", Color.WHITE)[0]
    valid_moves = game_manager.get_valid_moves(pos)
    for move in valid_moves:
        assert move.from_position == pos
        # Проверяем, что ход не оставляет под шахом (возможно, через вызов is_check)
        assert not game_manager.is_check(game_manager.current_turn)


def test_str_representation_contains_status(game_manager):
    board_str = str(game_manager)
    assert "Ход:" in board_str
    assert "Состояние:" in board_str


def test_game_state_transitions(game_manager, monkeypatch):
    # Этот тест проверит, что разные методы определяют состояние игры
    monkeypatch.setattr(game_manager, "is_checkmate", lambda: False)
    monkeypatch.setattr(game_manager, "is_stalemate", lambda: False)
    monkeypatch.setattr(game_manager, "is_check", lambda color: True)
    state = game_manager.get_game_state()
    assert state == GameState.CHECK

    monkeypatch.setattr(game_manager, "is_checkmate", lambda: True)
    monkeypatch.setattr(game_manager, "is_stalemate", lambda: False)
    state = game_manager.get_game_state()
    assert state == GameState.CHECKMATE

    monkeypatch.setattr(game_manager, "is_checkmate", lambda: False)
    monkeypatch.setattr(game_manager, "is_stalemate", lambda: True)
    monkeypatch.setattr(game_manager, "is_check", lambda color: False)
    state = game_manager.get_game_state()
    assert state == GameState.STALEMATE

    monkeypatch.setattr(game_manager, "is_checkmate", lambda: False)
    monkeypatch.setattr(game_manager, "is_stalemate", lambda: False)
    monkeypatch.setattr(game_manager, "is_check", lambda color: False)
    state = game_manager.get_game_state()
    assert state == GameState.ONGOING
