"""
Puzzle logic for the HIT137 Assignment 3 image puzzle.

This module contains the Tile and Puzzle classes.
The classes manage puzzle state, transformations,
moves, hints and solving.
"""

import random

import numpy as np

from transformations import (
    RotateTransformation,
    FlipTransformation,
    SwapTransformation
)


class Tile:
    """Represent one piece of the original image."""

    def __init__(self, tile_id, image):
        self.tile_id = tile_id
        self.home_position = tile_id

        # Keep the original image for comparison and solving.
        self.original_image = image.copy()

        # Current image after transformations.
        self.image = image.copy()

    def reset(self):
        """Restore the tile to its original orientation."""
        self.image = self.original_image.copy()

    def is_correct(self, current_position):
        """
        Check whether the tile is in the correct position
        and has the correct orientation.
        """

        correct_position = (
            current_position == self.home_position
        )

        correct_orientation = np.array_equal(
            self.image,
            self.original_image
        )

        return (
            correct_position
            and correct_orientation
        )


class Puzzle:
    """Manage the state and actions of the puzzle."""

    TRANSFORMATION_COUNTS = {
        3: 6,
        4: 12,
        5: 20
    }

    def __init__(self, grid_size=3):
        """Create a puzzle with a 3x3, 4x4 or 5x5 grid."""

        if grid_size not in [3, 4, 5]:
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        self.grid_size = grid_size
        self.tiles = []

        # Game statistics.
        self.moves = 0
        self.hints_used = 0
        self.max_hints = 3

        # Puzzle state.
        self.finished = False
        self.hint_positions = None

    @property
    def tile_count(self):
        """Return the total number of tiles."""
        return self.grid_size * self.grid_size

    @property
    def tiles_left(self):
        """Return the number of tiles that are incorrect."""

        incorrect_tiles = 0

        for position, tile in enumerate(self.tiles):
            if not tile.is_correct(position):
                incorrect_tiles += 1

        return incorrect_tiles

    def set_tiles(self, tiles):
        """
        Give the puzzle its tiles.

        This is normally called after the image processor
        divides the selected image into pieces.
        """

        self.tiles = tiles

        # Reset game state for a new image.
        self.moves = 0
        self.hints_used = 0
        self.finished = False
        self.hint_positions = None

    def scramble(self):
        """
        Randomly transform the puzzle.

        Required transformation counts:

        3x3 -> 6
        4x4 -> 12
        5x5 -> 20

        Each tile is selected as a primary transformation
        target at most once.
        """

        transformation_count = (
            self.TRANSFORMATION_COUNTS[self.grid_size]
        )

        # Guarantee that all three required
        # transformation types are represented.
        transformation_types = [
            "swap",
            "rotate",
            "flip"
        ]

        while len(transformation_types) < transformation_count:
            transformation_types.append(
                random.choice(
                    ["swap", "rotate", "flip"]
                )
            )

        random.shuffle(transformation_types)

        # Track tile IDs rather than only positions.
        # This prevents the same tile from being selected
        # as the main transformation target twice.
        available_tile_ids = [
            tile.tile_id
            for tile in self.tiles
        ]

        random.shuffle(available_tile_ids)

        for transformation_type in transformation_types:

            if not available_tile_ids:
                break

            target_tile_id = available_tile_ids.pop()

            target_position = self._find_tile_position(
                target_tile_id
            )

            if target_position is None:
                continue

            if transformation_type == "rotate":

                transformation = RotateTransformation()

                transformation.apply(
                    self.tiles,
                    target_position
                )

            elif transformation_type == "flip":

                transformation = FlipTransformation()

                transformation.apply(
                    self.tiles,
                    target_position
                )

            else:

                # Choose another tile position.
                other_positions = [
                    position
                    for position in range(self.tile_count)
                    if position != target_position
                ]

                if not other_positions:
                    continue

                other_position = random.choice(
                    other_positions
                )

                transformation = SwapTransformation()

                transformation.apply(
                    self.tiles,
                    target_position,
                    other_position
                )

        # Extremely unlikely safety check:
        # a scrambled puzzle should not start solved.
        if self.is_solved() and self.tile_count >= 2:

            first, second = random.sample(
                range(self.tile_count),
                2
            )

            SwapTransformation().apply(
                self.tiles,
                first,
                second
            )

    def _find_tile_position(self, tile_id):
        """Return the current position of a tile."""

        for position, tile in enumerate(self.tiles):

            if tile.tile_id == tile_id:
                return position

        return None

    def swap(self, first, second):
        """Swap two tiles during gameplay."""

        if first == second:
            return

        SwapTransformation().apply(
            self.tiles,
            first,
            second
        )

        self.record_move()

    def rotate(self, index):
        """Rotate one tile 90 degrees clockwise."""

        RotateTransformation(
            90
        ).apply(
            self.tiles,
            index
        )

        self.record_move()

    def flip(self, index):
        """Flip one tile horizontally."""

        FlipTransformation(
            "horizontal"
        ).apply(
            self.tiles,
            index
        )

        self.record_move()

    def record_move(self):
        """Record one player action."""

        self.moves += 1

        # A hint disappears after the next move.
        self.hint_positions = None

    def is_solved(self):
        """Return True when every tile is correct."""

        return self.tiles_left == 0

    def get_hint(self):
        """
        Return the current and correct position
        of one incorrect tile.

        A maximum of three hints is allowed.
        """

        if self.hints_used >= self.max_hints:
            return None

        incorrect_tiles = []

        for position, tile in enumerate(self.tiles):

            if not tile.is_correct(position):
                incorrect_tiles.append(
                    (position, tile)
                )

        if not incorrect_tiles:
            return None

        current_position, tile = random.choice(
            incorrect_tiles
        )

        self.hints_used += 1

        self.hint_positions = (
            current_position,
            tile.home_position
        )

        return self.hint_positions

    def solve(self):
        """
        Instantly solve the puzzle.

        Tiles are restored to their original orientation
        and placed into their home positions.
        """

        correct_order = [
            None
        ] * self.tile_count

        for tile in self.tiles:

            tile.reset()

            correct_order[
                tile.home_position
            ] = tile

        self.tiles = correct_order

        # Solve clears the player's score.
        self.moves = 0
        self.hint_positions = None
        self.finished = True