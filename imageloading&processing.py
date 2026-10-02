from pathlib import Path

import cv2

from puzzle import Tile


SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp"
}


class ImageProcessor:
    """Process source images into puzzle-ready tiles."""

    def _init_(self, max_width=500, max_height=500):
        self.max_width = max_width
        self.max_height = max_height

    def process(self, image_path, grid_size):
        """
        Load and prepare an image for the puzzle.

        Returns:
            tuple:
                prepared_image: The processed RGB image.
                tiles: List of Tile objects.
        """

        path = Path(image_path)

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG or BMP."
            )

        image = cv2.imread(str(path))

        if image is None:
            raise ValueError(
                "Unable to load the selected image."
            )

        # OpenCV loads images as BGR.
        image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        image = self._resize_image(image)

        image = self._crop_for_grid(
            image,
            grid_size
        )

        tiles = self._split_into_tiles(
            image,
            grid_size
        )

        return image, tiles

    def _resize_image(self, image):
        """Resize image while maintaining aspect ratio."""

        height, width = image.shape[:2]

        if height <= 0 or width <= 0:
            raise ValueError(
                "Image has invalid dimensions."
            )

        scale = min(
            self.max_width / width,
            self.max_height / height,
            1.0
        )

        new_width = max(
            1,
            int(width * scale)
        )

        new_height = max(
            1,
            int(height * scale)
        )

        if new_width != width or new_height != height:
            image = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_AREA
            )

        return image

    def _crop_for_grid(self, image, grid_size):
        """
        Crop the image so both dimensions are divisible
        by the selected grid size.
        """

        if grid_size not in [3, 4, 5]:
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        height, width = image.shape[:2]

        cropped_height = (
            height - height % grid_size
        )

        cropped_width = (
            width - width % grid_size
        )

        if cropped_height == 0 or cropped_width == 0:
            raise ValueError(
                "Image is too small for the selected grid."
            )

        return image[
            :cropped_height,
            :cropped_width
        ].copy()

    def _split_into_tiles(self, image, grid_size):
        """Split the image into equal-sized Tile objects."""

        height, width = image.shape[:2]

        tile_height = height // grid_size
        tile_width = width // grid_size

        tiles = []

        tile_id = 0

        for row in range(grid_size):
            for column in range(grid_size):

                y_start = row * tile_height
                y_end = y_start + tile_height

                x_start = column * tile_width
                x_end = x_start + tile_width

                tile_image = image[
                    y_start:y_end,
                    x_start:x_end
                ].copy()

                tile = Tile(
                    tile_id,
                    tile_image
                )

                tiles.append(tile)

                tile_id += 1

        return tiles