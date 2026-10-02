"""
Integration tests for the HIT137 Assignment 3 puzzle.
"""

import os
import tempfile

import cv2
import numpy as np

from image_processing import ImageProcessor
from puzzle import Puzzle


def create_test_image():
    """Create a temporary image for integration testing."""
    image = np.zeros((300, 400, 3), dtype=np.uint8)
    image[:, :200] = (255, 0, 0)
    image[:, 200:] = (0, 255, 0)
    return image


def run_tests():
    """Run image-processing and puzzle integration tests."""
    processor = ImageProcessor(max_width=500, max_height=500)
    test_image = create_test_image()

    with tempfile.NamedTemporaryFile(
        suffix=".png",
        delete=False,
    ) as file:
        test_path = file.name

    cv2.imwrite(test_path, test_image)

    try:
        for grid_size in (3, 4, 5):
            prepared_image, tiles = processor.process(
                test_path,
                grid_size,
            )

            assert len(tiles) == grid_size * grid_size
            assert prepared_image.shape[0] % grid_size == 0
            assert prepared_image.shape[1] % grid_size == 0

            puzzle = Puzzle(grid_size)
            puzzle.set_tiles(tiles)
            puzzle.scramble()

            assert len(puzzle.scramble_plan) in (6, 12, 20)
            assert puzzle.moves == 0

            puzzle.swap(0, 1)
            assert puzzle.moves == 1

            puzzle.rotate(0)
            assert puzzle.moves == 2

            puzzle.flip(0)
            assert puzzle.moves == 3

            print(f"✓ {grid_size}x{grid_size} integration test passed")

    finally:
        if os.path.exists(test_path):
            os.remove(test_path)

    print("ALL INTEGRATION TESTS PASSED!")


if __name__ == "__main__":
    run_tests()
