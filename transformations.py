"""
Transformation classes for the image puzzle.

This file contains the different ways a puzzle tile
can be changed during the game.
"""

import random

import cv2
import numpy as np


class TileTransformation:
    """Base class for all tile transformations."""

    def apply(self, tile):
        """Apply a transformation to a tile."""
        raise NotImplementedError(
            "This method must be implemented by a subclass."
        )


class RotateTransformation(TileTransformation):
    """Rotate a tile by 90, 180 or 270 degrees."""

    def __init__(self, angle=None):
        if angle is None:
            angle = random.choice([90, 180, 270])

        if angle not in [90, 180, 270]:
            raise ValueError(
                "Rotation must be 90, 180 or 270 degrees."
            )

        self.angle = angle

    def apply(self, tile):
        """Rotate the tile clockwise."""

        number_of_rotations = self.angle // 90

        tile.image = np.rot90(
            tile.image,
            -number_of_rotations
        ).copy()


class FlipTransformation(TileTransformation):
    """Flip a tile horizontally or vertically."""

    def __init__(self, direction=None):
        if direction is None:
            direction = random.choice(
                ["horizontal", "vertical"]
            )

        if direction not in ["horizontal", "vertical"]:
            raise ValueError(
                "Flip direction must be horizontal or vertical."
            )

        self.direction = direction

    def apply(self, tile):
        """Flip the tile in the selected direction."""

        if self.direction == "horizontal":
            tile.image = cv2.flip(tile.image, 1)
        else:
            tile.image = cv2.flip(tile.image, 0)


class SwapTransformation(TileTransformation):
    """Swap the positions of two tiles."""

    def apply(self, tiles, first, second):
        """Exchange the positions of two tiles."""

        if first == second:
            return

        tiles[first], tiles[second] = (
            tiles[second],
            tiles[first]
        )