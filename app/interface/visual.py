import tkinter as tk
from tkinter import messagebox

from dependency_injector.wiring import Provide, inject

from app.core import Container

CELL_SIZE = 40


class Config:
    COLOR_LIGHT_CELL = "#f0d9b5"
    COLOR_DARK_CELL = "#b58863"
    COLOR_SELECTED_OUTLINE = "red"
    COLOR_MOVE_HIGHLIGHT = "green"
    COLOR_PIECE_WHITE = "blue"
    COLOR_PIECE_BLACK = "black"
    LINE_WIDTH_OUTLINE = 3
    LINE_WIDTH_HIGHLIGHT = 3


PIECE_SYMBOLS = {
    'KING_WHITE': '♔',
    'KING_BLACK': '♚',
    'SYLPH_WHITE': 'S',
    'SYLPH_BLACK': 'S',
    'GRYPHON_WHITE': 'G',
    'GRYPHON_BLACK': 'G',
    'DRAGON_WHITE': 'Dr',
    'DRAGON_BLACK': 'Dr',
    'WARRIOR_WHITE': 'W',
    'WARRIOR_BLACK': "W",
    'HERO_WHITE': 'H',
    'HERO_BLACK': 'H',
    'OLIPHANT_WHITE': 'O',
    'OLIPHANT_BLACK': 'O',
    'UNICORN_WHITE': 'U',
    'UNICORN_BLACK': 'U',
    'THIEF_WHITE': 'T',
    'THIEF_BLACK': 'T',
    'CLERIC_WHITE': 'C',
    'CLERIC_BLACK': 'C',
    'MAGE_WHITE': 'M',
    'MAGE_BLACK': 'M',
    'PALADIN_WHITE': 'P',
    'PALADIN_BLACK': 'P',
    'DWARF_WHITE': 'D',
    'DWARF_BLACK': 'D',
    'BASILISK_WHITE': 'B',
    'BASILISK_BLACK': 'B',
    'ELEMENTAL_WHITE': 'E',
    'ELEMENTAL_BLACK': 'E',
}


class TkChessView(tk.Frame):
    @inject
    def __init__(self, master, game: "Game" = Provide[Container.game_manager]):
        super().__init__(master)
        self.game = game
        self.selected_pos = None
        self.current_layer = 0
        self.possible_moves = []
        self.white_on_top = True  # белые сверху по умолчанию

        self.canvas = tk.Canvas(self, width=self.game.board.geometry.width * CELL_SIZE,
                                height=self.game.board.geometry.height * CELL_SIZE)
        self.canvas.pack(side=tk.LEFT)

        # Панель истории ходов
        self.move_history_box = tk.Listbox(self, width=30)
        self.move_history_box.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self, text="Move History").pack(side=tk.RIGHT)

        # Кнопки управления слоями и поворотом
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(btn_frame, text="Layer / Depth").pack()
        self.layer_label = tk.Label(btn_frame, text=str(self.current_layer))
        self.layer_label.pack()
        tk.Button(btn_frame, text="Up", command=self.layer_up).pack()
        tk.Button(btn_frame, text="Down", command=self.layer_down).pack()
        tk.Button(btn_frame, text="Rotate Board", command=self.rotate_board).pack(pady=20)

        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_board()
        self.update_move_history()

    def rotate_board(self):
        self.white_on_top = not self.white_on_top
        self.draw_board()

    def layer_up(self):
        if self.current_layer < self.game.board.geometry.depth - 1:
            self.current_layer += 1
            self.layer_label.config(text=str(self.current_layer))
            self.draw_board()

    def layer_down(self):
        if self.current_layer > 0:
            self.current_layer -= 1
            self.layer_label.config(text=str(self.current_layer))
            self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        width = self.game.board.geometry.width
        height = self.game.board.geometry.height

        # Определяем порядок рисования по вертикали в зависимости от ориентации
        y_range = range(height) if self.white_on_top else range(height - 1, -1, -1)

        for vis_y, board_y in enumerate(y_range):
            for x in range(width):
                x1, y1 = x * CELL_SIZE, vis_y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                fill = Config.COLOR_LIGHT_CELL if (x + board_y) % 2 == 0 else Config.COLOR_DARK_CELL
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

                pos = Position(x, board_y, self.current_layer)
                piece_info = self.game.board.get_piece_at(pos)
                if piece_info:
                    piece_type, color = piece_info
                    key = f"{piece_type.name}_{color.name}"
                    symbol = PIECE_SYMBOLS.get(key, "?")
                    piece_color = Config.COLOR_PIECE_BLACK if color == Color.BLACK else Config.COLOR_PIECE_WHITE
                    self.canvas.create_text(
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=symbol,
                        font=("Arial", 20),
                        fill=piece_color
                    )

        # Выделение выбранной фигуры
        if self.selected_pos and self.selected_pos.z == self.current_layer:
            sel_x = self.selected_pos.x
            sel_y = self.selected_pos.y
            # Корректируем Y для визуального отображения
            vis_sel_y = sel_y if self.white_on_top else height - 1 - sel_y
            x1 = sel_x * CELL_SIZE
            y1 = vis_sel_y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         outline=Config.COLOR_SELECTED_OUTLINE,
                                         width=Config.LINE_WIDTH_OUTLINE)

        # Выделение возможных ходов
        for move in self.possible_moves:
            if move.to_position.z == self.current_layer:
                tx = move.to_position.x
                ty = move.to_position.y
                vis_ty = ty if self.white_on_top else height - 1 - ty
                x = tx * CELL_SIZE
                y = vis_ty * CELL_SIZE
                self.canvas.create_rectangle(
                    x, y, x + CELL_SIZE, y + CELL_SIZE,
                    outline=Config.COLOR_MOVE_HIGHLIGHT,
                    width=Config.LINE_WIDTH_HIGHLIGHT
                )

    def on_click(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        height = self.game.board.geometry.height
        # Преобразуем координаты клика в координаты доски с учётом ориентации
        board_y = y if self.white_on_top else height - 1 - y
        pos = Position(x, board_y, self.current_layer)

        if self.selected_pos is None:
            piece = self.game.board.get_piece_at(pos)
            if piece and piece[1] == self.game.current_turn:
                self.selected_pos = pos
                self.possible_moves = self.game.get_moves_from(self.game.board, pos)
                self.draw_board()
        else:
            try:
                move = Move(self.selected_pos, pos)
                self.game.move_piece(move)
                self.update_move_history()
            except ValueError as e:
                messagebox.showerror("Invalid Move", str(e))
            self.selected_pos = None
            self.possible_moves = []
            self.draw_board()

    def update_move_history(self):
        self.move_history_box.delete(0, tk.END)
        for i, move in enumerate(self.game.move_history, 1):
            from_pos = f"({move.from_position.x},{move.from_position.y},{move.from_position.z})"
            to_pos = f"({move.to_position.x},{move.to_position.y},{move.to_position.z})"
            attack_position = ""
            if move.attack_position is not None:
                p = move.attack_position
                attack_position = f"({p.x}, {p.y}, {p.z})"
            self.move_history_box.insert(tk.END,
                                         f"{i}. {from_pos} -> {to_pos}: {attack_position}")


if __name__ == "__main__":
    from app.domain.value_objects import Position, Move
    from app.domain import Color
    import tkinter as tk

    container = Container()
    container.wire(modules=[__name__])
    root = tk.Tk()
    root.title("DragonChess")

    view = TkChessView(root)
    view.rotate_board()
    view.pack()

    root.mainloop()
