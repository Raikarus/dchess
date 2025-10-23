from app.domain.value_objects import Move


class PieceMoveService:
    @staticmethod
    def move(board: "Board", move: Move) -> bool:
        if not board.is_empty(move.from_position) and board.is_within_bounds(move.to_position):
            piece = board.pieces.pop(move.from_position)
            piece.position = move.to_position
            board.pieces[move.to_position] = piece
            return True
        return False
