"""
Puzzle logic for the image scrambling game.

This file contains the Tile and Puzzle classes.
The classes manage the puzzle state, transformations,
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

        # The position where this tile originally belonged.
        self.home_position = tile_id

        # Keep a copy of the original image so the tile
        # can be restored later.
        self.original_image = image.copy()

        # Current version of the tile.
        self.image = image.copy()

    def reset(self):
        """Return the tile to its original orientation."""

        self.image = self.original_image.copy()

    def is_correct(self, current_position):
        """
        Check whether the tile is in its original position
        and has its original orientation.
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

    # Number of transformations required for each grid.
    TRANSFORMATION_COUNTS = {
        3: 6,
        4: 12,
        5: 20
    }

    def __init__(self, grid_size=3):
        """Create a new puzzle."""

        if grid_size not in [3, 4, 5]:
            raise ValueError(
                "Grid size must be 3, 4 or 5."
            )

        self.grid_size = grid_size

        # The list of tiles currently in the puzzle.
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
        """Return how many tiles are still incorrect."""

        incorrect_tiles = 0

        for position, tile in enumerate(self.tiles):
            if not tile.is_correct(position):
                incorrect_tiles += 1

        return incorrect_tiles

    def set_tiles(self, tiles):
        """
        Give the puzzle its tiles.

        This is normally called after the image processor
        has divided the selected image into pieces.
        """

        self.tiles = tiles

        # Start the game with fresh statistics.
        self.moves = 0
        self.hints_used = 0
        self.finished = False
        self.hint_positions = None

    def scramble(self):
        """
        Randomly transform the puzzle.

        The required number of transformations is:

        3x3 -> 6
        4x4 -> 12
        5x5 -> 20
        """

        transformation_count = (
            self.TRANSFORMATION_COUNTS[self.grid_size]
        )

        # Make sure all three transformation types
        # are included in every scramble.
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

        # Keep track of tile positions that have been
        # selected as transformation targets.
        available_positions = list(
            range(self.tile_count)
        )

        random.shuffle(available_positions)

        for transformation_type in transformation_types:

            if not available_positions:
                break

            current_position = (
                available_positions.pop()
            )

            if transformation_type == "rotate":

                transformation = RotateTransformation()

                transformation.apply(
                    self.tiles[current_position]
                )

            elif transformation_type == "flip":

                transformation = FlipTransformation()

                transformation.apply(
                    self.tiles[current_position]
                )

            else:
                # Swap the selected tile with another
                # different tile.
                other_positions = [
                    position
                    for position in range(self.tile_count)
                    if position != current_position
                ]

                other_position = random.choice(
                    other_positions
                )

                transformation = SwapTransformation()

                transformation.apply(
                    self.tiles,
                    current_position,
                    other_position
                )

        # Avoid the unlikely situation where random
        # transformations leave the puzzle solved.
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

        RotateTransformation(90).apply(
            self.tiles[index]
        )

        self.record_move()

    def flip(self, index):
        """Flip one tile horizontally."""

        FlipTransformation(
            "horizontal"
        ).apply(
            self.tiles[index]
        )

        self.record_move()

    def record_move(self):
        """Record a player action."""

        self.moves += 1

        # A hint is only shown until the next move.
        self.hint_positions = None

    def is_solved(self):
        """Return True when every tile is correct."""

        return self.tiles_left == 0

    def get_hint(self):
        """
        Return the current position and correct position
        of one incorrect tile.

        A maximum of three hints can be used per puzzle.
        """

        if self.hints_used >= self.max_hints:
            return None

        incorrect_tiles = []

        for position, tile in enumerate(self.tiles):

            if not tile.is_correct(position):
                incorrect_tiles.append(
                    (position, tile)
                )

        # There is nothing to hint if the puzzle is solved.
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

        The tiles are restored to their original
        orientation and placed in their home positions.
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

        # Solve clears the player's move count.
        self.moves = 0

        self.hint_positions = None
        self.finished = True