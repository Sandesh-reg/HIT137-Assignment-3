"""
Tkinter GUI for HIT137 Assignment 3.
"""

import os
import tkinter as tk

import numpy as np
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from image_processing import ImageProcessor
from puzzle import Puzzle


class PuzzleApp:
    """Desktop interface for the image scramble puzzle."""

    DISPLAY_SIZE = 620

    def __init__(self, root=None):
        self.root = root or tk.Tk()
        self.root.title("HIT137 Assignment 3 - Image Scramble Puzzle")
        self.root.resizable(False, False)

        self.processor = ImageProcessor()
        self.puzzle = Puzzle(3)

        self.selected_index = None
        self.original_photo = None
        self.puzzle_photo = None
        self.original_bounds = None
        self.puzzle_bounds = None
        self.processor_image = None
        self.current_image_path = None

        self._build_gui()
        self._update_controls()

    def _build_gui(self):
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="HIT137 Image Scramble Puzzle",
            font=("Segoe UI", 18, "bold"),
        ).pack()

        ttk.Label(
            header,
            text="Choose a grid size, load an image, then restore the scrambled tiles.",
        ).pack(pady=(4, 8))

        controls = ttk.Frame(self.root, padding=(10, 0, 10, 8))
        controls.pack(fill="x")

        ttk.Label(controls, text="Grid size:").pack(side="left")
        self.grid_var = tk.IntVar(value=3)
        self.grid_box = ttk.Combobox(
            controls,
            textvariable=self.grid_var,
            values=(3, 4, 5),
            width=5,
            state="readonly",
        )
        self.grid_box.pack(side="left", padx=5)

        self.load_button = ttk.Button(
            controls,
            text="Load Image",
            command=self.load_image,
        )
        self.load_button.pack(side="left", padx=5)

        self.hint_button = ttk.Button(
            controls,
            text="Hint",
            command=self.use_hint,
        )
        self.hint_button.pack(side="left", padx=5)

        self.solve_button = ttk.Button(
            controls,
            text="Solve",
            command=self.solve_puzzle,
        )
        self.solve_button.pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="Load an image to begin.")
        ttk.Label(
            self.root,
            textvariable=self.status_var,
            padding=(10, 0, 10, 8),
        ).pack()

        self.stats_var = tk.StringVar(
            value="Moves: 0    Tiles left: 0    Hints: 0/3"
        )
        ttk.Label(
            self.root,
            textvariable=self.stats_var,
            font=("Segoe UI", 11, "bold"),
            padding=(10, 0, 10, 8),
        ).pack()

        images = ttk.Frame(self.root, padding=10)
        images.pack()

        left = ttk.Frame(images)
        left.pack(side="left", padx=8)
        right = ttk.Frame(images)
        right.pack(side="left", padx=8)

        ttk.Label(
            left,
            text="Original",
            font=("Segoe UI", 12, "bold"),
        ).pack()
        ttk.Label(
            right,
            text="Puzzle (click here)",
            font=("Segoe UI", 12, "bold"),
        ).pack()

        self.original_canvas = tk.Canvas(
            left,
            width=self.DISPLAY_SIZE,
            height=self.DISPLAY_SIZE,
            bg="#eeeeee",
            highlightthickness=1,
        )
        self.original_canvas.pack()

        self.puzzle_canvas = tk.Canvas(
            right,
            width=self.DISPLAY_SIZE,
            height=self.DISPLAY_SIZE,
            bg="#eeeeee",
            highlightthickness=1,
        )
        self.puzzle_canvas.pack()

        self.puzzle_canvas.bind("<Button-1>", self.left_click)
        self.puzzle_canvas.bind("<Button-3>", self.right_click)

        ttk.Label(
            self.root,
            text=(
                "Left click: select/swap   |   Right click: rotate   |   "
                "Shift + left click: flip"
            ),
            padding=(10, 0, 10, 12),
        ).pack()

    def load_image(self):
        """Open a file dialog and start a fresh round."""
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("Bitmap", "*.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            grid_size = self.grid_var.get()
            image, tiles = self.processor.process(path, grid_size)

            self.processor_image = image
            self.puzzle = Puzzle(grid_size)
            self.puzzle.set_tiles(tiles)
            self.puzzle.scramble()

            self.current_image_path = path
            self.selected_index = None
            self.original_bounds = None
            self.puzzle_bounds = None

            self.status_var.set(
                f"Loaded: {os.path.basename(path)} | "
                f"{grid_size} × {grid_size}"
            )
            self._render()

        except (ValueError, RuntimeError, OSError) as exc:
            messagebox.showerror("Unable to load image", str(exc))

    def _display_image(self, canvas, rgb_image):
        """Display an image centered on a fixed canvas and return its bounds."""
        pil = Image.fromarray(rgb_image)
        pil.thumbnail(
            (self.DISPLAY_SIZE - 10, self.DISPLAY_SIZE - 10),
            Image.LANCZOS,
        )

        x = (self.DISPLAY_SIZE - pil.width) / 2
        y = (self.DISPLAY_SIZE - pil.height) / 2

        photo = ImageTk.PhotoImage(pil)
        canvas.delete("all")
        canvas.create_image(
            x + pil.width / 2,
            y + pil.height / 2,
            image=photo,
        )

        bounds = (x, y, pil.width, pil.height)

        if canvas == self.original_canvas:
            self.original_photo = photo
        else:
            self.puzzle_photo = photo

        return bounds

    def _reassemble(self):
        """Reassemble the current tiles into one RGB image."""
        if not self.puzzle.tiles:
            return None

        rows = []
        n = self.puzzle.grid_size

        for row in range(n):
            start = row * n
            rows.append(
                np.hstack(
                    [
                        self.puzzle.tiles[start + column].image
                        for column in range(n)
                    ]
                )
            )

        return np.vstack(rows)

    def _render(self):
        """Render images, grid, selection, hints and correct-tile ticks."""
        if not self.puzzle.tiles:
            return

        self.original_bounds = self._display_image(
            self.original_canvas,
            self.processor_image,
        )
        puzzle_image = self._reassemble()
        self.puzzle_bounds = self._display_image(
            self.puzzle_canvas,
            puzzle_image,
        )

        n = self.puzzle.grid_size
        x0, y0, width, height = self.puzzle_bounds
        cell_width = width / n
        cell_height = height / n

        # Faint grid is drawn only over the actual puzzle image.
        for i in range(1, n):
            x = x0 + i * cell_width
            y = y0 + i * cell_height
            self.puzzle_canvas.create_line(
                x,
                y0,
                x,
                y0 + height,
                fill="#777777",
                width=1,
            )
            self.puzzle_canvas.create_line(
                x0,
                y,
                x0 + width,
                y,
                fill="#777777",
                width=1,
            )

        if self.selected_index is not None:
            row, column = divmod(self.selected_index, n)
            x1 = x0 + column * cell_width
            y1 = y0 + row * cell_height
            self.puzzle_canvas.create_rectangle(
                x1 + 2,
                y1 + 2,
                x1 + cell_width - 2,
                y1 + cell_height - 2,
                outline="red",
                width=4,
            )

        if self.puzzle.hint_positions:
            current, home = self.puzzle.hint_positions
            self._draw_hint_circle(
                self.puzzle_canvas,
                current,
                self.puzzle_bounds,
                n,
            )
            self._draw_hint_circle(
                self.original_canvas,
                home,
                self.original_bounds,
                n,
            )

        for index, tile in enumerate(self.puzzle.tiles):
            if tile.is_correct(index):
                row, column = divmod(index, n)
                x1 = x0 + column * cell_width
                y1 = y0 + row * cell_height
                self.puzzle_canvas.create_oval(
                    x1 + cell_width - 30,
                    y1 + 8,
                    x1 + cell_width - 8,
                    y1 + 30,
                    outline="green",
                    width=3,
                )
                self.puzzle_canvas.create_text(
                    x1 + cell_width - 19,
                    y1 + 19,
                    text="✓",
                    fill="green",
                    font=("Segoe UI", 12, "bold"),
                )

        self._update_controls()

    def _draw_hint_circle(self, canvas, index, bounds, grid_size):
        """Draw a blue circle around a tile using actual image bounds."""
        x0, y0, width, height = bounds
        cell_width = width / grid_size
        cell_height = height / grid_size
        row, column = divmod(index, grid_size)

        cx = x0 + column * cell_width + cell_width / 2
        cy = y0 + row * cell_height + cell_height / 2
        radius = min(cell_width, cell_height) * 0.25

        canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="blue",
            width=4,
        )

    def _tile_index_from_event(self, event):
        """Map a click to a tile and ignore clicks outside the image."""
        if not self.puzzle.tiles or self.puzzle_bounds is None:
            return None

        x0, y0, width, height = self.puzzle_bounds
        if not (x0 <= event.x < x0 + width and y0 <= event.y < y0 + height):
            return None

        n = self.puzzle.grid_size
        column = int((event.x - x0) / (width / n))
        row = int((event.y - y0) / (height / n))

        if 0 <= row < n and 0 <= column < n:
            return row * n + column
        return None

    def left_click(self, event):
        """Select/swap a tile, or flip it with Shift + left click."""
        if self.puzzle.finished or not self.puzzle.tiles:
            return

        index = self._tile_index_from_event(event)
        if index is None:
            return

        if event.state & 0x0001:
            self.selected_index = None
            self.puzzle.flip(index)
            self._after_action()
            return

        if self.selected_index is None:
            self.selected_index = index
        elif self.selected_index == index:
            self.selected_index = None
        else:
            self.puzzle.swap(self.selected_index, index)
            self.selected_index = None

        self._render()

    def right_click(self, event):
        """Rotate a tile 90 degrees clockwise."""
        if self.puzzle.finished or not self.puzzle.tiles:
            return

        index = self._tile_index_from_event(event)
        if index is None:
            return

        self.selected_index = None
        self.puzzle.rotate(index)
        self._after_action()

    def _after_action(self):
        """Render an action and lock the puzzle when solved."""
        self._render()

        if self.puzzle.is_solved() and not self.puzzle.finished:
            self.puzzle.finished = True
            self.status_var.set(
                "Puzzle completed! Input is now locked."
            )
            self._render()
            messagebox.showinfo(
                "Puzzle Complete",
                f"Congratulations! You solved the puzzle in "
                f"{self.puzzle.moves} moves.",
            )

    def use_hint(self):
        """Use one of the three available hints."""
        if self.puzzle.finished or not self.puzzle.tiles:
            return

        result = self.puzzle.get_hint()
        if result is None:
            if self.puzzle.hints_used >= self.puzzle.max_hints:
                messagebox.showinfo(
                    "Hints",
                    "You have used all 3 hints for this image.",
                )
            return

        self.status_var.set(
            f"Hint {self.puzzle.hints_used}/3: blue circles show "
            "a tile and its home position."
        )
        self._render()

    def solve_puzzle(self):
        """Instantly solve the puzzle and clear the move counter."""
        if self.puzzle.finished or not self.puzzle.tiles:
            return

        self.puzzle.solve()
        self.selected_index = None
        self.status_var.set(
            "Puzzle solved. Load another image to play again."
        )
        self._render()

    def _update_controls(self):
        """Update counters and button states."""
        tiles_left = self.puzzle.tiles_left if self.puzzle.tiles else 0

        self.stats_var.set(
            f"Moves: {self.puzzle.moves}    "
            f"Tiles left: {tiles_left}    "
            f"Hints: {self.puzzle.hints_used}/3"
        )

        has_image = bool(self.puzzle.tiles)
        self.hint_button.config(
            state=(
                "normal"
                if has_image
                and not self.puzzle.finished
                and self.puzzle.hints_used < self.puzzle.max_hints
                else "disabled"
            )
        )
        self.solve_button.config(
            state=(
                "normal"
                if has_image and not self.puzzle.finished
                else "disabled"
            )
        )

    def run(self):
        """Start the Tkinter event loop."""
        self.root.mainloop()
