"""
Transformation classes for the HIT137 Assignment 3 image puzzle.

The classes demonstrate inheritance and polymorphism: every concrete
transformation implements the same apply() interface.
"""

import random

import cv2
import numpy as np


class TileTransformation:
    """Base class for all tile transformations."""

    name = "Transformation"

    def apply(self, tiles, index=None, other_index=None):
        """Apply this transformation to a collection of tiles."""
        raise NotImplementedError("Subclasses must implement apply().")


class RotateTransformation(TileTransformation):
    """Rotate one tile clockwise by 90, 180 or 270 degrees."""

    name = "Rotate"

    def __init__(self, angle=None):
        self.angle = (
            random.choice((90, 180, 270))
            if angle is None
            else angle
        )
        if self.angle not in (90, 180, 270):
            raise ValueError("Rotation must be 90, 180 or 270 degrees.")

    def apply(self, tiles, index=None, other_index=None):
        """Rotate the selected tile clockwise."""
        if index is None:
            raise ValueError("A tile index is required for rotation.")

        turns = self.angle // 90
        tiles[index].image = np.rot90(
            tiles[index].image, k=-turns
        ).copy()


class FlipTransformation(TileTransformation):
    """Flip one tile horizontally or vertically."""

    name = "Flip"

    def __init__(self, direction=None):
        self.direction = (
            random.choice(("horizontal", "vertical"))
            if direction is None
            else direction
        )
        if self.direction not in ("horizontal", "vertical"):
            raise ValueError(
                "Flip direction must be horizontal or vertical."
            )

    def apply(self, tiles, index=None, other_index=None):
        """Flip the selected tile."""
        if index is None:
            raise ValueError("A tile index is required for flipping.")

        code = 1 if self.direction == "horizontal" else 0
        tiles[index].image = cv2.flip(tiles[index].image, code)


class SwapTransformation(TileTransformation):
    """Exchange the positions of two tiles."""

    name = "Swap"

    def apply(self, tiles, index=None, other_index=None):
        """Swap two tile positions."""
        if index is None or other_index is None:
            raise ValueError(
                "Two tile indices are required for swapping."
            )
        if index == other_index:
            return

        tiles[index], tiles[other_index] = (
            tiles[other_index],
            tiles[index],
        )
