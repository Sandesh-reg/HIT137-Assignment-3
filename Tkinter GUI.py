"""
Tkinter GUI for the HIT137 Assignment 3 image puzzle.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

from image_processing import ImageProcessor
from puzzle import Puzzle


class PuzzleGUI:
    """Create and manage the puzzle application interface."""

    def __init__(self, root):
        self.root = root
        self.root.title("Image Scramble Puzzle")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 650)

        self.processor = ImageProcessor(
            max_width=500,
            max_height=500
        )

        self.puzzle = None
        self.original_image = None
        self.selected_tile = None
        self.image_path = None
        self.tile_canvases = []

        self.grid_size = tk.IntVar(value=3)

        self.create_interface()

    def create_interface(self):
        """Create the main interface."""

        title = tk.Label(
            self.root,
            text="Image Scramble Puzzle",
            font=("Arial", 22, "bold")
        )
        title.pack(pady=10)

        controls = tk.Frame(self.root)
        controls.pack(pady=5)

        tk.Label(
            controls,
            text="Grid Size:"
        ).pack(side=tk.LEFT, padx=5)

        grid_menu = tk.OptionMenu(
            controls,
            self.grid_size,
            3,
            4,
            5
        )
        grid_menu.pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="Choose Image",
            command=self.choose_image
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="New Image",
            command=self.choose_image
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="Hint",
            command=self.use_hint
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            controls,
            text="Solve",
            command=self.solve_puzzle
        ).pack(side=tk.LEFT, padx=5)

        self.moves_label = tk.Label(
            controls,
            text="Moves: 0",
            font=("Arial", 11, "bold")
        )
        self.moves_label.pack(side=tk.LEFT, padx=15)

        self.tiles_label = tk.Label(
            controls,
            text="Tiles incorrect: 0",
            font=("Arial", 11, "bold")
        )
        self.tiles_label.pack(side=tk.LEFT, padx=5)

        images_frame = tk.Frame(self.root)
        images_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=10
        )

        original_frame = tk.Frame(images_frame)
        original_frame.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
            padx=10
        )

        transformed_frame = tk.Frame(images_frame)
        transformed_frame.pack(
            side=tk.RIGHT,
            fill=tk.BOTH,
            expand=True,
            padx=10
        )

        tk.Label(
            original_frame,
            text="Original Image",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        tk.Label(
            transformed_frame,
            text="Puzzle",
            font=("Arial", 14, "bold")
        ).pack(pady=5)

        self.original_canvas = tk.Canvas(
            original_frame,
            width=500,
            height=500,
            bg="white"
        )
        self.original_canvas.pack()

        self.puzzle_frame = tk.Frame(
            transformed_frame,
            bg="white"
        )
        self.puzzle_frame.pack()

        self.status_label = tk.Label(
            self.root,
            text="Choose an image to start.",
            font=("Arial", 11)
        )
        self.status_label.pack(pady=5)

    def choose_image(self):
        """Open the image selection dialog."""

        file_path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[
                (
                    "Image files",
                    "*.jpg *.jpeg *.png *.bmp"
                ),
                ("JPG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp")
            ]
        )

        if not file_path:
            return

        try:
            self.load_puzzle(file_path)
        except Exception as error:
            messagebox.showerror(
                "Error",
                str(error)
            )

    def load_puzzle(self, file_path):
        """Load an image and create a new puzzle."""

        grid_size = self.grid_size.get()

        original_image, tiles = self.processor.process(
            file_path,
            grid_size
        )

        self.image_path = file_path
        self.original_image = original_image

        self.puzzle = Puzzle(grid_size)
        self.puzzle.set_tiles(tiles)
        self.puzzle.scramble()

        self.selected_tile = None

        self.display_original()
        self.display_puzzle()
        self.update_counters()

        self.status_label.config(
            text="Puzzle ready. Restore the original image."
        )

    def display_original(self):
        """Display the original image."""

        if self.original_image is None:
            return

        image = cv2.cvtColor(
            self.original_image,
            cv2.COLOR_BGR2RGB
        )

        image = Image.fromarray(image)
        image.thumbnail((500, 500))

        self.original_photo = ImageTk.PhotoImage(image)

        self.original_canvas.delete("all")

        self.original_canvas.create_image(
            250,
            250,
            image=self.original_photo
        )

        self.draw_original_grid()

    def draw_original_grid(self):
        """Draw the faint grid over the original image."""

        if self.puzzle is None:
            return

        grid_size = self.puzzle.grid_size
        size = 500
        tile_size = size / grid_size

        for i in range(grid_size + 1):
            position = i * tile_size

            self.original_canvas.create_line(
                position,
                0,
                position,
                size,
                fill="gray"
            )

            self.original_canvas.create_line(
                0,
                position,
                size,
                position,
                fill="gray"
            )

    def display_puzzle(self):
        """Display all scrambled puzzle tiles."""

        for widget in self.puzzle_frame.winfo_children():
            widget.destroy()

        self.tile_canvases = []

        if self.puzzle is None:
            return

        grid_size = self.puzzle.grid_size

        for position, tile in enumerate(
            self.puzzle.tiles
        ):
            row = position // grid_size
            column = position % grid_size

            canvas = tk.Canvas(
                self.puzzle_frame,
                width=500 // grid_size,
                height=500 // grid_size,
                highlightthickness=1,
                highlightbackground="gray"
            )

            canvas.grid(
                row=row,
                column=column
            )

            canvas.bind(
                "<Button-1>",
                lambda event, index=position:
                self.left_click(event, index)
            )

            canvas.bind(
                "<Button-3>",
                lambda event, index=position:
                self.right_click(event, index)
            )

            canvas.bind(
                "<Shift-Button-1>",
                lambda event, index=position:
                self.shift_click(event, index)
            )

            self.tile_canvases.append(canvas)

            self.display_tile(
                position,
                tile.image
            )

        self.update_selection()

    def display_tile(self, position, image):
        """Display one tile."""

        canvas = self.tile_canvases[position]

        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        pil_image = Image.fromarray(
            rgb_image
        )

        size = 500 // self.puzzle.grid_size

        pil_image = pil_image.resize(
            (size, size),
            Image.Resampling.LANCZOS
        )

        photo = ImageTk.PhotoImage(
            pil_image
        )

        canvas.delete("all")

        canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=photo
        )

        canvas.image = photo

    def left_click(self, event, position):
        """Select a tile or swap two tiles."""

        if self.puzzle is None or self.puzzle.finished:
            return

        if self.selected_tile is None:
            self.selected_tile = position
            self.update_selection()
            return

        if self.selected_tile == position:
            self.selected_tile = None
            self.update_selection()
            return

        self.puzzle.swap(
            self.selected_tile,
            position
        )

        self.selected_tile = None
        self.display_puzzle()
        self.check_completion()

    def right_click(self, event, position):
        """Rotate a tile clockwise."""

        if self.puzzle is None or self.puzzle.finished:
            return

        self.puzzle.rotate(position)

        self.selected_tile = None

        self.display_puzzle()
        self.check_completion()

    def shift_click(self, event, position):
        """Flip a tile horizontally."""

        if self.puzzle is None or self.puzzle.finished:
            return

        self.puzzle.flip(position)

        self.selected_tile = None

        self.display_puzzle()
        self.check_completion()

    def update_selection(self):
        """Highlight the selected tile."""

        for index, canvas in enumerate(
            self.tile_canvases
        ):
            if index == self.selected_tile:
                canvas.config(
                    highlightthickness=3,
                    highlightbackground="blue"
                )
            else:
                canvas.config(
                    highlightthickness=1,
                    highlightbackground="gray"
                )

    def update_counters(self):
        """Update the move and incorrect-tile counters."""

        if self.puzzle is None:
            return

        self.moves_label.config(
            text=f"Moves: {self.puzzle.moves}"
        )

        self.tiles_label.config(
            text=(
                f"Tiles incorrect: "
                f"{self.puzzle.tiles_left}"
            )
        )

    def use_hint(self):
        """Show a hint for one incorrect tile."""

        if self.puzzle is None or self.puzzle.finished:
            return

        hint = self.puzzle.get_hint()

        if hint is None:
            messagebox.showinfo(
                "Hint",
                "No more hints are available."
            )
            return

        current_position, home_position = hint

        self.display_puzzle()

        self.tile_canvases[
            current_position
        ].config(
            highlightthickness=4,
            highlightbackground="blue"
        )

        self.status_label.config(
            text=(
                f"Hint: tile belongs in "
                f"position {home_position + 1}."
            )
        )

    def solve_puzzle(self):
        """Instantly solve the puzzle."""

        if self.puzzle is None:
            return

        if self.puzzle.finished:
            return

        self.puzzle.solve()

        self.selected_tile = None

        self.display_puzzle()
        self.update_counters()

        self.status_label.config(
            text="Puzzle solved."
        )

    def check_completion(self):
        """Check whether the puzzle has been solved."""

        self.update_counters()

        if self.puzzle.is_solved():
            self.puzzle.finished = True

            self.display_puzzle()

            messagebox.showinfo(
                "Puzzle Complete",
                (
                    "Congratulations!\n\n"
                    f"You solved the puzzle in "
                    f"{self.puzzle.moves} moves."
                )
            )

            self.status_label.config(
                text="Puzzle completed. Load another image to play again."
            )


def start_application():
    """Start the puzzle application."""

    root = tk.Tk()
    PuzzleGUI(root)
    root.mainloop()