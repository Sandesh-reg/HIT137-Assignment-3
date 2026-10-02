"""
Puzzle state and gameplay logic for HIT137 Assignment 3.
"""

import random

import numpy as np

from transformations import (
    FlipTransformation,
    RotateTransformation,
    SwapTransformation,
)


class Tile:
    """Represent one image tile and its immutable home position."""

    def __init__(self, tile_id, image):
        self.tile_id = tile_id
        self.home_position = tile_id
        self.original_image = image.copy()
        self.image = image.copy()

    def reset(self):
        """Restore the tile to its original orientation."""
        self.image = self.original_image.copy()

    def is_correct(self, current_position):
        """Return whether position and orientation are both correct."""
        return (
            current_position == self.home_position
            and np.array_equal(self.image, self.original_image)
        )


class Puzzle:
    """Manage tiles, scrambling, gameplay actions, hints and solving."""

    TRANSFORMATION_COUNTS = {3: 6, 4: 12, 5: 20}

    def __init__(self, grid_size=3):
        if grid_size not in self.TRANSFORMATION_COUNTS:
            raise ValueError("Grid size must be 3, 4 or 5.")

        self.grid_size = grid_size
        self.tiles = []
        self.moves = 0
        self.hints_used = 0
        self.max_hints = 3
        self.finished = False
        self.hint_positions = None
        self.scramble_plan = []

    @property
    def tile_count(self):
        """Return the total number of tiles."""
        return self.grid_size * self.grid_size

    @property
    def tiles_left(self):
        """Return the number of tiles that are currently incorrect."""
        return sum(
            not tile.is_correct(position)
            for position, tile in enumerate(self.tiles)
        )

    def set_tiles(self, tiles):
        """Set tiles for a new image and reset the round state."""
        if len(tiles) != self.tile_count:
            raise ValueError("Incorrect number of tiles for this grid.")

        self.tiles = list(tiles)
        self.moves = 0
        self.hints_used = 0
        self.finished = False
        self.hint_positions = None
        self.scramble_plan = []

    def _find_tile_position(self, tile_id):
        """Return the current position of a tile ID."""
        for position, tile in enumerate(self.tiles):
            if tile.tile_id == tile_id:
                return position
        return None

    def _generate_scramble_plan(self):
        """
        Generate all scramble transformations before applying any.

        Every tile involved in the plan is used at most once. A swap
        uses two unique tile IDs; rotate/flip use one. The number of
        transformations is fixed by the selected grid size.
        """
        count = self.TRANSFORMATION_COUNTS[self.grid_size]

        # Keep at least one swap, one rotation and one flip.
        # The number of swaps is capped so every involved tile remains
        # unique: count + swaps <= total number of tiles.
        max_swaps = min(
            self.tile_count // 2,
            self.tile_count - count,
        )
        swap_count = random.randint(1, max_swaps)

        types = ["swap"] * swap_count
        types.extend(["rotate", "flip"])
        types.extend(
            random.choice(("rotate", "flip"))
            for _ in range(count - swap_count - 2)
        )
        random.shuffle(types)

        available_ids = [tile.tile_id for tile in self.tiles]
        random.shuffle(available_ids)

        plan = []
        cursor = 0

        for transformation_type in types:
            if transformation_type == "swap":
                first = available_ids[cursor]
                second = available_ids[cursor + 1]
                cursor += 2
                plan.append(("swap", first, second))
            else:
                target = available_ids[cursor]
                cursor += 1
                if transformation_type == "rotate":
                    angle = random.choice((90, 180, 270))
                    plan.append(("rotate", target, angle))
                else:
                    direction = random.choice(("horizontal", "vertical"))
                    plan.append(("flip", target, direction))

        return plan

    def _apply_scramble_plan(self, plan):
        """Apply a previously generated scramble plan by tile ID."""
        for transformation in plan:
            kind = transformation[0]

            if kind == "swap":
                _, first_id, second_id = transformation
                first = self._find_tile_position(first_id)
                second = self._find_tile_position(second_id)
                SwapTransformation().apply(self.tiles, first, second)

            elif kind == "rotate":
                _, tile_id, angle = transformation
                index = self._find_tile_position(tile_id)
                RotateTransformation(angle).apply(self.tiles, index)

            else:
                _, tile_id, direction = transformation
                index = self._find_tile_position(tile_id)
                FlipTransformation(direction).apply(self.tiles, index)

    def scramble(self):
        """
        Randomly scramble the puzzle using the required transformation count.

        The complete transformation plan is generated first, contains all
        three required transformation types, and never targets the same
        tile twice.
        """
        for tile in self.tiles:
            tile.reset()

        for _ in range(50):
            plan = self._generate_scramble_plan()
            self._apply_scramble_plan(plan)

            if not self.is_solved():
                self.scramble_plan = plan
                return

            for tile in self.tiles:
                tile.reset()

        raise RuntimeError("Unable to generate a non-solved scramble.")

    def swap(self, first, second):
        """Swap two tiles and count one player move."""
        if first == second:
            return
        SwapTransformation().apply(self.tiles, first, second)
        self.record_move()

    def rotate(self, index):
        """Rotate one tile 90 degrees clockwise and count one move."""
        RotateTransformation(90).apply(self.tiles, index)
        self.record_move()

    def flip(self, index):
        """Flip one tile horizontally and count one move."""
        FlipTransformation("horizontal").apply(self.tiles, index)
        self.record_move()

    def record_move(self):
        """Count a player action and clear the current hint."""
        self.moves += 1
        self.hint_positions = None

    def is_solved(self):
        """Return True when every tile is correct."""
        return self.tiles_left == 0

    def get_hint(self):
        """Mark one incorrect tile and its correct home position."""
        if self.hints_used >= self.max_hints:
            return None

        incorrect = [
            (position, tile)
            for position, tile in enumerate(self.tiles)
            if not tile.is_correct(position)
        ]
        if not incorrect:
            return None

        current_position, tile = random.choice(incorrect)
        self.hints_used += 1
        self.hint_positions = (
            current_position,
            tile.home_position,
        )
        return self.hint_positions

    def solve(self):
        """Restore every tile to its home position and orientation."""
        ordered = [None] * self.tile_count

        for tile in self.tiles:
            tile.reset()
            ordered[tile.home_position] = tile

        self.tiles = ordered
        self.moves = 0
        self.hint_positions = None
        self.finished = True
