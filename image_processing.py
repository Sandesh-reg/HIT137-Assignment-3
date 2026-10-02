"""
OpenCV image loading and tiling for HIT137 Assignment 3.
"""

import os

import cv2

from puzzle import Tile


class ImageProcessor:
    """Load, resize and divide an image into equal puzzle tiles."""

    SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}

    def __init__(self, max_width=620, max_height=520):
        self.max_width = max_width
        self.max_height = max_height

    def process(self, image_path, grid_size):
        """
        Load an image, resize it proportionally, crop it so the
        dimensions divide evenly, and return the image plus its tiles.
        """
        extension = os.path.splitext(image_path)[1].lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError("Please select a JPG, PNG or BMP image.")

        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("The selected file could not be read as an image.")

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        height, width = image.shape[:2]
        scale = min(
            self.max_width / width,
            self.max_height / height,
            1.0,
        )

        new_width = max(grid_size, int(width * scale))
        new_height = max(grid_size, int(height * scale))

        image = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_AREA,
        )

        tile_width = image.shape[1] // grid_size
        tile_height = image.shape[0] // grid_size

        if tile_width < 1 or tile_height < 1:
            raise ValueError("The image is too small for this grid size.")

        crop_width = tile_width * grid_size
        crop_height = tile_height * grid_size
        image = image[:crop_height, :crop_width].copy()

        tiles = []
        for row in range(grid_size):
            for column in range(grid_size):
                y1 = row * tile_height
                y2 = (row + 1) * tile_height
                x1 = column * tile_width
                x2 = (column + 1) * tile_width

                tile_id = row * grid_size + column
                tiles.append(
                    Tile(tile_id, image[y1:y2, x1:x2])
                )

        return image, tiles
