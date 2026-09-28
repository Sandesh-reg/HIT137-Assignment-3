"""
Transformation classes for the HIT137 Assignment 3 puzzle.

This module demonstrates inheritance and polymorphism.
Each transformation provides an apply() method.
"""

import random

import cv2
import numpy as np


class TileTransformation:
    """Base class for all tile transformations."""

    def apply(self, tiles, index=None, other_index=None):
        """
        Apply a transformation.

        Subclasses override this method to provide
        their own transformation behaviour.
        """
        raise NotImplementedError(
            "Subclasses must implement apply()."
        )


class RotateTransformation(TileTransformation):
    """Rotate one tile by 90, 180 or 270 degrees."""

    def __init__(self, angle=None):
        if angle is None:
            angle = random.choice([90, 180, 270])

        if angle not in [90, 180, 270]:
            raise ValueError(
                "Rotation must be 90, 180 or 270 degrees."
            )

        self.angle = angle

    def apply(self, tiles, index=None, other_index=None):
        """Rotate the selected tile clockwise."""

        if index is None:
            raise ValueError(
                "A tile index is required for rotation."
            )

        rotations = self.angle // 90

        tiles[index].image = np.rot90(
            tiles[index].image,
            -rotations
        ).copy()


class FlipTransformation(TileTransformation):
    """Flip one tile horizontally or vertically."""

    def __init__(self, direction=None):
        if direction is None:
            direction = random.choice(
                ["horizontal", "vertical"]
            )

        if direction not in ["horizontal", "vertical"]:
            raise ValueError(
                "Flip direction must be horizontal "
                "or vertical."
            )

        self.direction = direction

    def apply(self, tiles, index=None, other_index=None):
        """Flip the selected tile."""

        if index is None:
            raise ValueError(
                "A tile index is required for flipping."
            )

        if self.direction == "horizontal":
            tiles[index].image = cv2.flip(
                tiles[index].image,
                1
            )
        else:
            tiles[index].image = cv2.flip(
                tiles[index].image,
                0
            )


class SwapTransformation(TileTransformation):
    """Swap two tiles."""

    def apply(self, tiles, index=None, other_index=None):
        """Exchange two tile positions."""

        if index is None or other_index is None:
            raise ValueError(
                "Two tile indices are required for swapping."
            )

        if index == other_index:
            return

        tiles[index], tiles[other_index] = (
            tiles[other_index],
            tiles[index]
        )