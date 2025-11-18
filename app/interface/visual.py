import tkinter as tk
from tkinter import messagebox
from itertools import chain
from dependency_injector.wiring import Provide, inject

from app.core import Container

CELL_SIZE = 40


class Config:
    COLOR_LIGHT_CELL = "#f0d9b5"
    COLOR_DARK_CELL = "#b58863"
    COLOR_SELECTED_OUTLINE = "red"
    COLOR_MOVE_HIGHLIGHT = "green"
    COLOR_PIECE_WHITE = "gold"
    COLOR_PIECE_BLACK = "deep pink"
    LINE_WIDTH_OUTLINE = 5
    LINE_WIDTH_HIGHLIGHT = 5


PIECE_SYMBOLS = {
    'KING_WHITE': '♔',
    'KING_BLACK': '♚',
    'SYLPH_WHITE': '🌬️',
    'SYLPH_BLACK': '🌬️',
    'GRYPHON_WHITE': '🦅',
    'GRYPHON_BLACK': '🦅',
    'DRAGON_WHITE': '🐲',
    'DRAGON_BLACK': '🐲',
    'WARRIOR_WHITE': '🛡️',
    'WARRIOR_BLACK': '🛡️',
    'HERO_WHITE': '🗡️',
    'HERO_BLACK': '🗡️',
    'OLIPHANT_WHITE': '🐘',
    'OLIPHANT_BLACK': '🐘',
    'UNICORN_WHITE': '🦄',
    'UNICORN_BLACK': '🦄',
    'THIEF_WHITE': '🔪',
    'THIEF_BLACK': '🔪',
    'CLERIC_WHITE': '🙏',
    'CLERIC_BLACK': '🙏',
    'MAGE_WHITE': '🔮',
    'MAGE_BLACK': '🔮',
    'PALADIN_WHITE': '⚔️',
    'PALADIN_BLACK': '⚔️',
    'DWARF_WHITE': '⛏️',
    'DWARF_BLACK': '⛏️',
    'BASILISK_WHITE': '🐍',
    'BASILISK_BLACK': '🐍',
    'ELEMENTAL_WHITE': '🌪️',
    'ELEMENTAL_BLACK': '🌪️',
}


class TkChessView(tk.Frame):
    @inject
    def __init__(self, master, game: "Game" = Provide[Container.game_factory]):
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

        self.hovered_pos = None
        self.hover_possible_moves = []
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)
        self.draw_board()
        self.update_move_history()

    def on_mouse_move(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        height = self.game.board.geometry.height
        board_y = y if self.white_on_top else height - 1 - y
        pos = Position(x, board_y, self.current_layer)

        if pos != self.hovered_pos:
            self.hovered_pos = pos
            piece = self.game.board.get_piece_at(pos)
            if piece and piece[1] == self.game.current_turn:
                self.hover_possible_moves = self.game.get_moves_from(self.game.board, pos)
            else:
                self.hover_possible_moves = []
            self.draw_board()

    def on_mouse_leave(self, event):
        self.hovered_pos = None
        self.hover_possible_moves = []
        self.draw_board()

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
        def create_text_with_outline(canvas, x, y, text, font, fill_color, outline_color):
            # Нарисовать текст сдвинутый в 4 направления для имитации контура
            offset = 1
            for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset),
                           (-offset, -offset), (-offset, offset), (offset, -offset), (offset, offset)]:
                canvas.create_text(x + dx, y + dy, text=text, font=font, fill=outline_color)
            # Нарисовать основной текст поверх
            canvas.create_text(x, y, text=text, font=font, fill=fill_color)

        self.canvas.delete("all")
        width = self.game.board.geometry.width
        height = self.game.board.geometry.height

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
                    create_text_with_outline(
                        self.canvas,
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=symbol,
                        font=("Segoe UI Emoji", CELL_SIZE // 2),
                        fill_color=piece_color,
                        outline_color="black"  # или другой цвет контура
                    )
        # Выделение выбранной фигуры
        if self.selected_pos and self.selected_pos.z == self.current_layer:
            vis_sel_y = self.selected_pos.y if self.white_on_top else height - 1 - self.selected_pos.y
            x1 = self.selected_pos.x * CELL_SIZE
            y1 = vis_sel_y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         outline=Config.COLOR_SELECTED_OUTLINE,
                                         width=Config.LINE_WIDTH_OUTLINE)
        # Выделение возможных ходов выбранной фигуры (и при наведении)
        for move in chain(self.possible_moves, self.hover_possible_moves):
            if move.to_position.z == self.current_layer:
                vis_ty = move.to_position.y if self.white_on_top else height - 1 - move.to_position.y
                x = move.to_position.x * CELL_SIZE
                y = vis_ty * CELL_SIZE
                box_offset = 5
                outline_color = "red" if move.attack_position is not None else "green"
                self.canvas.create_rectangle(
                    (x + box_offset), (y + box_offset), x + CELL_SIZE - box_offset, y + CELL_SIZE - box_offset,
                    outline=outline_color,
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
