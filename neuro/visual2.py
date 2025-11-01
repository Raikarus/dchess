import re
import tkinter as tk
from itertools import chain
from tkinter import messagebox

import requests

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

API_URL = "http://127.0.0.1:8000/api/game"


class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        return isinstance(other, Position) and (self.x, self.y, self.z) == (other.x, other.y, other.z)


class Move:
    def __init__(self, from_position: Position, to_position: Position, attack_position=None):
        self.from_position = from_position
        self.to_position = to_position
        self.attack_position = attack_position


class TkChessView(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.selected_pos = None
        self.current_layer = 0
        self.possible_moves = []
        self.white_on_top = True

        self.board_width = 12  # предполагается, размеры 8x8x N, можно получить из состояния API
        self.board_height = 8
        self.board_depth = 3

        self.current_turn = None
        self.game_state = None
        self.board_state = {}  # хранение фигур в формате (x,y,z): (piece_type, color)

        self.canvas = tk.Canvas(self, width=self.board_width * CELL_SIZE,
                                height=self.board_height * CELL_SIZE)
        self.canvas.pack(side=tk.LEFT)

        self.move_history_box = tk.Listbox(self, width=30)
        self.move_history_box.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(self, text="Move History").pack(side=tk.RIGHT)

        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(btn_frame, text="Layer / Depth").pack()
        self.layer_label = tk.Label(btn_frame, text=str(self.current_layer))
        self.layer_label.pack()
        tk.Button(btn_frame, text="Up", command=self.layer_up).pack()
        tk.Button(btn_frame, text="Down", command=self.layer_down).pack()
        tk.Button(btn_frame, text="Rotate Board", command=self.rotate_board).pack(pady=20)
        tk.Button(btn_frame, text="Reset Game", command=self.reset_game).pack(pady=10)

        self.hovered_pos = None
        self.hover_possible_moves = []
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Leave>", self.on_mouse_leave)

        # Метка для отображения текущего хода
        self.turn_label = tk.Label(self, text="Current turn: UNKNOWN", font=("Arial", 14))
        self.turn_label.pack(pady=5)

        # Кнопка обновления состояния
        update_button = tk.Button(self, text="Update", command=self.update_board_state)
        update_button.pack(pady=5)

        self.load_state()
        self.draw_board()
        self.update_move_history()

        self.schedule_update()

    def schedule_update(self):
        self.update_board_state()
        self.after(1000, self.schedule_update)  # запланировать повторно через 1 секунду

    # Словари сопоставления для enum PieceType и Color (значения взять из вашего кода)
    PIECE_TYPE_MAP = {
        'PieceType.KING': 'KING',
        'PieceType.SYLPH': 'SYLPH',
        'PieceType.GRYPHON': 'GRYPHON',
        'PieceType.DRAGON': 'DRAGON',
        'PieceType.WARRIOR': 'WARRIOR',
        'PieceType.HERO': 'HERO',
        'PieceType.OLIPHANT': 'OLIPHANT',
        'PieceType.UNICORN': 'UNICORN',
        'PieceType.THIEF': 'THIEF',
        'PieceType.CLERIC': 'CLERIC',
        'PieceType.MAGE': 'MAGE',
        'PieceType.PALADIN': 'PALADIN',
        'PieceType.DWARF': 'DWARF',
        'PieceType.BASILISK': 'BASILISK',
        'PieceType.ELEMENTAL': 'ELEMENTAL',
    }

    COLOR_MAP = {
        'Color.WHITE': 'WHITE',
        'Color.BLACK': 'BLACK'
    }

    def update_board_state(self):
        prev_state = self.game_state
        self.load_state()
        self.draw_board()
        self.update_move_history()
        self.update_current_turn()
        print(self.game_state)
        # Проверяем состояние игры и предупреждаем один раз при смене
        if self.game_state != "ONGOING":
            if self.game_state == "CHECKMATE":
                messagebox.showinfo("Game Over", "CHECKMATE")
            elif self.game_state == "STALEMATE":
                messagebox.showinfo("Game Over", "STALEMATE!")
            elif self.game_state == "DRAW":
                messagebox.showinfo("Game Over", "Draw!")

    def update_current_turn(self):
        self.turn_label.config(text=f"Current turn: {self.current_turn}")

    def parse_position(self, pos_str):
        # Пример: Position(x=0, y=1, z=2)
        m = re.match(r'Position\(x=(\d+), y=(\d+), z=(\d+)\)', pos_str)
        if m:
            return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        else:
            return None

    def parse_board(self, board_str):
        # Извлечь geometry
        geometry_match = re.search(r'BoardGeometry\(width=(\d+), height=(\d+), depth=(\d+)\)', board_str)
        width, height, depth = (8, 8, 1)  # дефолт
        if geometry_match:
            width = int(geometry_match.group(1))
            height = int(geometry_match.group(2))
            depth = int(geometry_match.group(3))

        # Извлечь pieces — это словарь Position -> (PieceType, Color)
        pieces_section = re.search(r'pieces={(.+)}\)$', board_str, re.DOTALL)
        board_state = {}
        if pieces_section:
            pieces_str = pieces_section.group(1)
            # Разбиваем на ключ-значение по шаблону: Position(...): (<PieceType.X: n>, <Color.Y: 'color'>)
            # Пример ключа: Position(x=0, y=1, z=2)
            # Пример значения: (<PieceType.SYLPH: 1>, <Color.WHITE: 'white'>)
            pair_pattern = re.compile(
                r'Position\(x=(\d+), y=(\d+), z=(\d+)\): \(<PieceType\.(\w+): \d+>, <Color\.(\w+): .+?>\)'
            )
            for match in pair_pattern.finditer(pieces_str):
                x, y, z, ptype, color = match.groups()
                x, y, z = int(x), int(y), int(z)
                ptype = ptype.upper()
                color = color.upper()
                board_state[(x, y, z)] = (ptype, color)

        return {
            "width": width,
            "height": height,
            "depth": depth,
            "board_state": board_state
        }

    def load_state(self):
        try:
            resp = requests.get(f"{API_URL}/state")
            resp.raise_for_status()
            state = resp.json()
            self.current_turn = state["current_turn"]
            self.game_state = state["game_state"]
            parsed = self.parse_board(state["board"])
            self.board_width = parsed["width"]
            self.board_height = parsed["height"]
            self.board_depth = parsed["depth"]
            self.board_state = parsed["board_state"]
            self.canvas.config(width=self.board_width * CELL_SIZE, height=self.board_height * CELL_SIZE)
            self.layer_label.config(text=str(self.current_layer))
            self.turn_label.config(text=f"Current turn: {self.current_turn}")
            self.move_history = state["move_history"] or []
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load state: {e}")

    def get_moves_from(self, pos):
        try:
            resp = requests.get(f"{API_URL}/moves")
            resp.raise_for_status()
            moves = resp.json()
            result = []
            for m in moves:
                # Отфильтровать ходы от pos
                from_pos = m["from_position"]
                if (from_pos["x"], from_pos["y"], from_pos["z"]) == (pos.x, pos.y, pos.z):
                    to_pos = m["to_position"]
                    attack_pos = m.get("attack_position")
                    if attack_pos is not None:
                        attack = Position(attack_pos["x"], attack_pos["y"], attack_pos["z"])
                    else:
                        attack = None
                    move_obj = Move(
                        from_position=Position(from_pos["x"], from_pos["y"], from_pos["z"]),
                        to_position=Position(to_pos["x"], to_pos["y"], to_pos["z"]),
                        attack_position=attack,
                    )
                    result.append(move_obj)
            return result
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get moves: {e}")
            return []

    def move_piece_api(self, move: Move):
        try:
            payload = {
                "from_position": {"x": move.from_position.x, "y": move.from_position.y, "z": move.from_position.z},
                "to_position": {"x": move.to_position.x, "y": move.to_position.y, "z": move.to_position.z}
            }
            resp = requests.post(f"{API_URL}/make_move", json=payload)
            if resp.status_code != 200:
                messagebox.showerror("Invalid Move", resp.json().get("detail", "Unknown error"))
                return False
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to make move: {e}")
            return False

    def on_mouse_move(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        board_y = y if self.white_on_top else self.board_height - 1 - y
        pos = Position(x, board_y, self.current_layer)

        if pos != self.hovered_pos:
            self.hovered_pos = pos
            piece = self.board_state.get((pos.x, pos.y, pos.z))
            if piece and piece[1].upper() == self.current_turn:
                self.hover_possible_moves = self.get_moves_from(pos)
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
        if self.current_layer < self.board_depth - 1:
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
            offset = 1
            for dx, dy in [(-offset, 0), (offset, 0), (0, -offset), (0, offset),
                           (-offset, -offset), (-offset, offset), (offset, -offset), (offset, offset)]:
                canvas.create_text(x + dx, y + dy, text=text, font=font, fill=outline_color)
            canvas.create_text(x, y, text=text, font=font, fill=fill_color)

        self.canvas.delete("all")
        width = self.board_width
        height = self.board_height

        y_range = range(height) if self.white_on_top else range(height - 1, -1, -1)
        for vis_y, board_y in enumerate(y_range):
            for x in range(width):
                x1, y1 = x * CELL_SIZE, vis_y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                fill = Config.COLOR_LIGHT_CELL if (x + board_y) % 2 == 0 else Config.COLOR_DARK_CELL
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)

                piece_info = self.board_state.get((x, board_y, self.current_layer))
                if piece_info:
                    piece_type, color = piece_info
                    key = f"{piece_type}_{color}"
                    symbol = PIECE_SYMBOLS.get(key, "?")
                    piece_color = Config.COLOR_PIECE_BLACK if color == "BLACK" else Config.COLOR_PIECE_WHITE
                    create_text_with_outline(
                        self.canvas,
                        x1 + CELL_SIZE / 2,
                        y1 + CELL_SIZE / 2,
                        text=symbol,
                        font=("Segoe UI Emoji", CELL_SIZE // 2),
                        fill_color=piece_color,
                        outline_color="black"
                    )
        if self.selected_pos and self.selected_pos.z == self.current_layer:
            vis_sel_y = self.selected_pos.y if self.white_on_top else height - 1 - self.selected_pos.y
            x1 = self.selected_pos.x * CELL_SIZE
            y1 = vis_sel_y * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2,
                                         outline=Config.COLOR_SELECTED_OUTLINE,
                                         width=Config.LINE_WIDTH_OUTLINE)

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
        board_y = y if self.white_on_top else self.board_height - 1 - y
        pos = Position(x, board_y, self.current_layer)

        if self.selected_pos is None:
            piece = self.board_state.get((pos.x, pos.y, pos.z))
            if piece and piece[1].upper() == self.current_turn:
                self.selected_pos = pos
                self.possible_moves = self.get_moves_from(pos)
                self.draw_board()
        else:
            move = Move(self.selected_pos, pos)
            if self.move_piece_api(move):
                self.load_state()
                self.update_move_history()
            self.selected_pos = None
            self.possible_moves = []
            self.draw_board()

    def update_move_history(self):
        self.move_history_box.delete(0, tk.END)
        for i, move_str in enumerate(self.move_history, 1):
            self.move_history_box.insert(tk.END, f"{i}. {move_str}")

    def reset_game(self):
        try:
            resp = requests.post(f"{API_URL}/new")
            resp.raise_for_status()
            self.load_state()
            self.update_move_history()
            self.draw_board()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reset game: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("DragonChess - API Client")

    view = TkChessView(root)
    view.rotate_board()
    view.pack()

    root.mainloop()
