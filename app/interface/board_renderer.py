import tkinter as tk
from tkinter import Canvas
from app.domain import Board, Color, Position, GameManager
from itertools import product
from .renderer import Renderer


class BoardRenderer(Renderer):

    def __init__(self, master, board: "Board", cell_size=30):
        """
        board: объект доски, который знает фигуры и координаты
        cell_size: размер ячейки в пикселях
        """
        self.master = master
        self.board = board
        self.cell_size = cell_size

        # высчитываем ширину и высоту Canvas из размеров доски (по 2D координатам)
        self.width = board.width * cell_size
        self.height = board.height * cell_size
        self.depth = board.depth
        self.gap = 50

        self.canvas = Canvas(master, width=self.width, height=self.height * self.depth + (self.depth - 1) * self.gap)
        self.canvas.pack()

        self.draw_board()
        self.draw_pieces()

    def draw_board(self):
        for x, y, z in product(range(self.board.width), range(self.board.height), range(self.board.depth)):
            color = 'white' if (x + y) % 2 == 0 else 'gray'
            x1 = x * self.cell_size
            y1 = y * self.cell_size + (self.height + self.gap) * z
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

    def draw_pieces(self):
        for x, y, z in product(range(self.board.width), range(self.board.height), range(self.board.depth)):
            piece = self.board.get_piece_at(Position(x, y, z))
            if piece:
                x_center = x * self.cell_size + self.cell_size // 2
                y_center = (self.height * self.depth + (self.depth - 1) * self.gap
                            - (y * self.cell_size + self.cell_size // 2 + z * (self.height + self.gap)))
                self.canvas.create_text(x_center, y_center, text=piece.symbol,
                                        font=('Arial', self.cell_size // 2),
                                        fill='#f5496c' if piece.color == Color.BLACK else '#FFD700')

    def refresh(self):
        self.canvas.delete('all')
        self.draw_board()
        self.draw_pieces()


root = tk.Tk()
gameManager = GameManager(["p1", "p2"])
board = gameManager.board
renderer = BoardRenderer(root, board)
root.mainloop()
