import copy
import os
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import cv2
import numpy as np
from PIL import Image, ImageTk



# OOP: Inheritance + Polymorphism

class TileTransformation:
    """Base class for a tile transformation."""

    name = "Transformation"

    def apply(self, tile):
        """Apply this transformation to a Tile."""
        raise NotImplementedError


class RotateTransformation(TileTransformation):
    """Rotate a tile clockwise by 90, 180 or 270 degrees."""

    name = "Rotate"

    def __init__(self, angle=None):
        self.angle = angle or random.choice((90, 180, 270))

    def apply(self, tile):
        turns = self.angle // 90
        tile.image = np.rot90(tile.image, k=-turns).copy()
        tile.history.append(f"rotate_{self.angle}")


class FlipTransformation(TileTransformation):
    """Flip a tile horizontally or vertically."""

    name = "Flip"

    def __init__(self, direction=None):
        self.direction = direction or random.choice(("horizontal", "vertical"))

    def apply(self, tile):
        if self.direction == "horizontal":
            tile.image = cv2.flip(tile.image, 1)
        else:
            tile.image = cv2.flip(tile.image, 0)
        tile.history.append(f"flip_{self.direction}")


class SwapTransformation(TileTransformation):
    """Swap the positions of two tiles."""

    name = "Swap"

    def __init__(self, first=None, second=None):
        self.first = first
        self.second = second

    def apply(self, tile):
        # Position swapping is handled by Puzzle.swap_positions().
        # This method is intentionally defined so all transformations
        # share the same polymorphic interface.
        tile.history.append("swap")


# Tile model

class Tile:
    """Represents one puzzle tile and its target position."""

    def __init__(self, tile_id, home_index, image):
        self.tile_id = tile_id
        self.home_index = home_index
        self.original_image = image.copy()
        self.image = image.copy()
        self.history = []

    def is_correct(self, current_index):
        """Return True when this tile is in its home position and orientation."""
        return (
            current_index == self.home_index
            and np.array_equal(self.image, self.original_image)
        )

    def reset(self):
        """Restore the tile to its original image."""
        self.image = self.original_image.copy()
        self.history.clear()


# Puzzle model


class Puzzle:
    """Stores puzzle state, transformations, moves and hint information."""

    GRID_TRANSFORMS = {3: 6, 4: 12, 5: 20}

    def __init__(self, grid_size=3):
        self.grid_size = grid_size
        self.tiles = []
        self.original_tiles = []
        self.moves = 0
        self.hints_used = 0
        self.max_hints = 3
        self.completed = False
        self.hint_positions = None
        self.image = None

    @property
    def tile_count(self):
        return self.grid_size * self.grid_size

    @property
    def tiles_left(self):
        return sum(
            not tile.is_correct(index)
            for index, tile in enumerate(self.tiles)
        )

    def load_image(self, image_path):
        """Load, resize and crop an image so it divides evenly into a grid."""
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("The selected file is not a valid JPG, PNG or BMP image.")

        # Convert BGR -> RGB for consistent PIL/OpenCV display.
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Keep the displayed puzzle compact while preserving aspect ratio.
        max_w, max_h = 620, 520
        h, w = image.shape[:2]
        scale = min(max_w / w, max_h / h, 1.0)
        new_w = max(self.grid_size, int(w * scale))
        new_h = max(self.grid_size, int(h * scale))
        image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Crop to dimensions divisible by the selected grid size.
        tile_w = image.shape[1] // self.grid_size
        tile_h = image.shape[0] // self.grid_size
        if tile_w < 1 or tile_h < 1:
            raise ValueError("Image is too small for the selected grid size.")

        crop_w = tile_w * self.grid_size
        crop_h = tile_h * self.grid_size
        image = image[:crop_h, :crop_w]

        self.image = image
        self._create_tiles()
        self._scramble()
        self.moves = 0
        self.hints_used = 0
        self.completed = False
        self.hint_positions = None

    def _create_tiles(self):
        """Split the image into equally sized OpenCV tiles."""
        h, w = self.image.shape[:2]
        tile_h = h // self.grid_size
        tile_w = w // self.grid_size

        self.tiles = []
        tile_id = 0
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                y1, y2 = row * tile_h, (row + 1) * tile_h
                x1, x2 = col * tile_w, (col + 1) * tile_w
                tile = Tile(tile_id, tile_id, self.image[y1:y2, x1:x2])
                self.tiles.append(tile)
                tile_id += 1

        self.original_tiles = [tile.original_image.copy() for tile in self.tiles]

    def _scramble(self):
        """Apply all required transformation types in random order."""
        count = self.GRID_TRANSFORMS[self.grid_size]

        # Generate all transformations at once.
        transformations = []
        for _ in range(count):
            choice = random.choice(("swap", "rotate", "flip"))
            if choice == "swap":
                transformations.append(SwapTransformation())
            elif choice == "rotate":
                transformations.append(RotateTransformation())
            else:
                transformations.append(FlipTransformation())

        # Guarantee that every required transformation type is represented.
        transformations[0] = SwapTransformation()
        transformations[1] = RotateTransformation()
        transformations[2] = FlipTransformation()
        random.shuffle(transformations)

        # Apply orientation transformations to random tiles.
        for transform in transformations:
            if isinstance(transform, SwapTransformation):
                a, b = random.sample(range(len(self.tiles)), 2)
                self.tiles[a], self.tiles[b] = self.tiles[b], self.tiles[a]
            else:
                index = random.randrange(len(self.tiles))
                transform.apply(self.tiles[index])

        # Avoid a completely solved state after scrambling.
        if self.tiles_left == 0:
            a, b = random.sample(range(len(self.tiles)), 2)
            self.tiles[a], self.tiles[b] = self.tiles[b], self.tiles[a]

    def swap_positions(self, first, second):
        """Swap two tile objects."""
        if first == second:
            return
        self.tiles[first], self.tiles[second] = self.tiles[second], self.tiles[first]
        self._count_move()

    def rotate(self, index):
        """Rotate a selected tile 90 degrees clockwise."""
        transform = RotateTransformation(90)
        transform.apply(self.tiles[index])
        self._count_move()

    def flip(self, index):
        """Flip a selected tile horizontally."""
        transform = FlipTransformation("horizontal")
        transform.apply(self.tiles[index])
        self._count_move()

    def _count_move(self):
        """Count one player action and clear an old hint."""
        self.moves += 1
        self.hint_positions = None

    def is_complete(self):
        """Return True if every tile is home and correctly oriented."""
        return self.tiles_left == 0

    def solve(self):
        """Restore every tile to its original position and orientation."""
        # This is equivalent to undoing all remaining scramble/player
        # transformations because each Tile retains its immutable target image.
        ordered = [None] * len(self.tiles)
        for tile in self.tiles:
            tile.reset()
            ordered[tile.home_index] = tile
        self.tiles = ordered
        self.moves = 0
        self.completed = True
        self.hint_positions = None

    def hint(self):
        """Return one incorrect tile and its correct home position."""
        incorrect = [
            (index, tile)
            for index, tile in enumerate(self.tiles)
            if not tile.is_correct(index)
        ]
        if not incorrect or self.hints_used >= self.max_hints:
            return None

        current_index, tile = random.choice(incorrect)
        home_index = tile.home_index
        self.hints_used += 1
        self.hint_positions = (current_index, home_index)
        return self.hint_positions


# Tkinter GUI
class PuzzleApp:
    """Tkinter desktop interface for the image puzzle."""

    DISPLAY_SIZE = 620

    def __init__(self, root):
        self.root = root
        self.root.title("HIT137 Assignment 3 - Image Scramble Puzzle")
        self.root.resizable(False, False)

        self.puzzle = Puzzle(3)
        self.selected_index = None
        self.original_photo = None
        self.puzzle_photo = None
        self.current_image_path = None

        self._build_gui()
        self._update_controls()

    def _build_gui(self):
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill="x")

        ttk.Label(
            header,
            text="HIT137 Image Scramble Puzzle",
            font=("Segoe UI", 18, "bold")
        ).pack()

        ttk.Label(
            header,
            text="Choose a grid size, load an image, then restore the scrambled tiles."
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
            state="readonly"
        )
        self.grid_box.pack(side="left", padx=5)

        self.load_button = ttk.Button(
            controls, text="Load Image", command=self.load_image
        )
        self.load_button.pack(side="left", padx=5)

        self.hint_button = ttk.Button(
            controls, text="Hint", command=self.use_hint
        )
        self.hint_button.pack(side="left", padx=5)

        self.solve_button = ttk.Button(
            controls, text="Solve", command=self.solve_puzzle
        )
        self.solve_button.pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="Load an image to begin.")
        ttk.Label(
            self.root,
            textvariable=self.status_var,
            padding=(10, 0, 10, 8)
        ).pack()

        self.stats_var = tk.StringVar(value="Moves: 0    Tiles left: 0    Hints: 0/3")
        ttk.Label(
            self.root,
            textvariable=self.stats_var,
            font=("Segoe UI", 11, "bold"),
            padding=(10, 0, 10, 8)
        ).pack()

        images = ttk.Frame(self.root, padding=10)
        images.pack()

        left = ttk.Frame(images)
        left.pack(side="left", padx=8)
        right = ttk.Frame(images)
        right.pack(side="left", padx=8)

        ttk.Label(left, text="Original", font=("Segoe UI", 12, "bold")).pack()
        ttk.Label(right, text="Puzzle (click here)", font=("Segoe UI", 12, "bold")).pack()

        self.original_canvas = tk.Canvas(
            left, width=self.DISPLAY_SIZE, height=self.DISPLAY_SIZE,
            bg="#eeeeee", highlightthickness=1
        )
        self.original_canvas.pack()

        self.puzzle_canvas = tk.Canvas(
            right, width=self.DISPLAY_SIZE, height=self.DISPLAY_SIZE,
            bg="#eeeeee", highlightthickness=1
        )
        self.puzzle_canvas.pack()

        self.puzzle_canvas.bind("<Button-1>", self.left_click)
        self.puzzle_canvas.bind("<Button-3>", self.right_click)

        ttk.Label(
            self.root,
            text="Left click: select/swap   |   Right click: rotate   |   Shift + left click: flip",
            padding=(10, 0, 10, 12)
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
            ]
        )
        if not path:
            return

        try:
            self.puzzle = Puzzle(self.grid_var.get())
            self.puzzle.load_image(path)
            self.current_image_path = path
            self.selected_index = None
            self.status_var.set(
                f"Loaded: {os.path.basename(path)} | "
                f"{self.puzzle.grid_size} × {self.puzzle.grid_size}"
            )
            self._render()
        except Exception as exc:
            messagebox.showerror("Unable to load image", str(exc))

    def _display_image(self, canvas, rgb_image):
        """Display an RGB OpenCV image centered on a fixed canvas."""
        pil = Image.fromarray(rgb_image)
        pil.thumbnail((self.DISPLAY_SIZE - 10, self.DISPLAY_SIZE - 10), Image.LANCZOS)

        background = Image.new("RGB", (self.DISPLAY_SIZE, self.DISPLAY_SIZE), "white")
        x = (self.DISPLAY_SIZE - pil.width) // 2
        y = (self.DISPLAY_SIZE - pil.height) // 2
        background.paste(pil, (x, y))

        photo = ImageTk.PhotoImage(background)
        canvas.delete("all")
        canvas.create_image(
            self.DISPLAY_SIZE // 2,
            self.DISPLAY_SIZE // 2,
            image=photo
        )

        if canvas == self.original_canvas:
            self.original_photo = photo
        else:
            self.puzzle_photo = photo

    def _reassemble(self):
        """Reassemble current tiles into one RGB image."""
        if not self.puzzle.tiles:
            return None

        rows = []
        for row in range(self.puzzle.grid_size):
            start = row * self.puzzle.grid_size
            rows.append(np.hstack([
                self.puzzle.tiles[start + col].image
                for col in range(self.puzzle.grid_size)
            ]))
        return np.vstack(rows)

    def _render(self):
        """Render both images, grid lines, selection, hints and correct ticks."""
        if self.puzzle.image is None:
            return

        self._display_image(self.original_canvas, self.puzzle.image)
        puzzle_image = self._reassemble()
        self._display_image(self.puzzle_canvas, puzzle_image)

        # Grid overlay.
        n = self.puzzle.grid_size
        cell = self.DISPLAY_SIZE / n
        for i in range(1, n):
            pos = i * cell
            self.puzzle_canvas.create_line(
                pos, 0, pos, self.DISPLAY_SIZE, fill="#777777", width=1
            )
            self.puzzle_canvas.create_line(
                0, pos, self.DISPLAY_SIZE, pos, fill="#777777", width=1
            )

        # Selected tile highlight.
        if self.selected_index is not None:
            row, col = divmod(self.selected_index, n)
            x1, y1 = col * cell, row * cell
            self.puzzle_canvas.create_rectangle(
                x1 + 2, y1 + 2, x1 + cell - 2, y1 + cell - 2,
                outline="red", width=4
            )

        # Hint circles on both images.
        if self.puzzle.hint_positions:
            current, home = self.puzzle.hint_positions
            self._draw_hint_circle(self.puzzle_canvas, current, n, "blue")
            self._draw_hint_circle(self.original_canvas, home, n, "blue")

        # Green tick for each correctly placed tile.
        for index, tile in enumerate(self.puzzle.tiles):
            if tile.is_correct(index):
                row, col = divmod(index, n)
                x1, y1 = col * cell, row * cell
                self.puzzle_canvas.create_oval(
                    x1 + cell - 30, y1 + 8,
                    x1 + cell - 8, y1 + 30,
                    outline="green", width=3
                )
                self.puzzle_canvas.create_text(
                    x1 + cell - 19, y1 + 19, text="✓",
                    fill="green", font=("Segoe UI", 12, "bold")
                )

        self._update_controls()

    def _draw_hint_circle(self, canvas, index, n, outline):
        """Draw a blue hint circle around the centre of a tile."""
        cell = self.DISPLAY_SIZE / n
        row, col = divmod(index, n)
        cx = col * cell + cell / 2
        cy = row * cell + cell / 2
        radius = min(cell * 0.25, 38)
        canvas.create_oval(
            cx - radius, cy - radius, cx + radius, cy + radius,
            outline=outline, width=4
        )

    def _tile_index_from_event(self, event):
        """Map a canvas click to a tile index; ignore off-image clicks."""
        if self.puzzle.image is None:
            return None

        n = self.puzzle.grid_size
        cell = self.DISPLAY_SIZE / n
        col = int(event.x // cell)
        row = int(event.y // cell)
        if 0 <= row < n and 0 <= col < n:
            return row * n + col
        return None

    def left_click(self, event):
        """Select/swap a tile, or horizontally flip it with Shift."""
        if self.puzzle.completed or not self.puzzle.tiles:
            return

        index = self._tile_index_from_event(event)
        if index is None:
            return

        # Tkinter sets the lowest state bit for Shift on standard desktop Tk.
        if event.state & 0x0001:
            self.selected_index = None
            self.puzzle.flip(index)
            self._after_action()
            return

        self.puzzle.hint_positions = None

        if self.selected_index is None:
            self.selected_index = index
        elif self.selected_index == index:
            self.selected_index = None
        else:
            self.puzzle.swap_positions(self.selected_index, index)
            self.selected_index = None

        self._after_action()

    def shift_left_click(self, event):
        """Flip a tile horizontally using Shift + left click."""
        if self.puzzle.completed or not self.puzzle.tiles:
            return

        index = self._tile_index_from_event(event)
        if index is None:
            return

        self.selected_index = None
        self.puzzle.flip(index)
        self._after_action()

    def right_click(self, event):
        """Rotate a tile 90 degrees clockwise."""
        if self.puzzle.completed or not self.puzzle.tiles:
            return

        index = self._tile_index_from_event(event)
        if index is None:
            return

        self.selected_index = None
        self.puzzle.rotate(index)
        self._after_action()

    def _after_action(self):
        """Re-render after an action and check for completion."""
        self._render()
        if self.puzzle.is_complete():
            self.puzzle.completed = True
            self.status_var.set("Puzzle completed! Input is now locked.")
            self._render()
            messagebox.showinfo(
                "Puzzle Complete",
                f"Congratulations! You solved the puzzle in {self.puzzle.moves} moves."
            )

    def use_hint(self):
        """Use one of the three available hints."""
        if self.puzzle.completed or not self.puzzle.tiles:
            return

        result = self.puzzle.hint()
        if result is None:
            if self.puzzle.hints_used >= self.puzzle.max_hints:
                messagebox.showinfo("Hints", "You have used all 3 hints for this image.")
            return

        self.status_var.set(
            f"Hint {self.puzzle.hints_used}/3: blue circles show a tile and its home position."
        )
        self._render()

    def solve_puzzle(self):
        """Instantly solve and reset moves/score."""
        if not self.puzzle.tiles:
            return

        self.puzzle.solve()
        self.selected_index = None
        self.status_var.set("Puzzle solved. Load another image to play again.")
        self._render()

    def _update_controls(self):
        """Update counters and button states."""
        if self.puzzle.image is None:
            tiles_left = 0
        else:
            tiles_left = self.puzzle.tiles_left

        self.stats_var.set(
            f"Moves: {self.puzzle.moves}    "
            f"Tiles left: {tiles_left}    "
            f"Hints: {self.puzzle.hints_used}/3"
        )

        self.hint_button.config(
            state=("disabled" if self.puzzle.hints_used >= 3 or
                   self.puzzle.completed or self.puzzle.image is None else "normal")
        )
        self.solve_button.config(
            state=("disabled" if self.puzzle.completed or self.puzzle.image is None else "normal")
        )


def main():
    root = tk.Tk()
    PuzzleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
