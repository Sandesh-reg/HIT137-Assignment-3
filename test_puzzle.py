"""
Tests for the HIT137 Assignment 3 puzzle logic and transformations.
"""

import numpy as np

from puzzle import Puzzle, Tile
from transformations import (
    FlipTransformation,
    RotateTransformation,
    SwapTransformation,
    TileTransformation,
)


def create_test_puzzle(size):
    """Create deterministic test tiles."""
    puzzle = Puzzle(size)
    tiles = []

    for number in range(size * size):
        image = np.zeros((20, 20, 3), dtype=np.uint8)
        image[:, :10] = number + 10
        image[:10, :] = number + 20
        tiles.append(Tile(number, image))

    puzzle.set_tiles(tiles)
    return puzzle


def test_grid_sizes():
    for size in (3, 4, 5):
        puzzle = create_test_puzzle(size)
        assert puzzle.grid_size == size
        assert puzzle.tile_count == size * size


def test_move_counter():
    puzzle = create_test_puzzle(3)
    assert puzzle.moves == 0

    puzzle.swap(0, 1)
    puzzle.rotate(0)
    puzzle.flip(0)

    assert puzzle.moves == 3


def test_transformations():
    puzzle = create_test_puzzle(3)

    original = puzzle.tiles[0].image.copy()
    RotateTransformation(90).apply(puzzle.tiles, 0)
    assert not np.array_equal(puzzle.tiles[0].image, original)

    puzzle = create_test_puzzle(3)
    original = puzzle.tiles[0].image.copy()
    FlipTransformation("horizontal").apply(puzzle.tiles, 0)
    assert not np.array_equal(puzzle.tiles[0].image, original)

    puzzle = create_test_puzzle(3)
    first_id = puzzle.tiles[0].tile_id
    second_id = puzzle.tiles[1].tile_id
    SwapTransformation().apply(puzzle.tiles, 0, 1)
    assert puzzle.tiles[0].tile_id == second_id
    assert puzzle.tiles[1].tile_id == first_id


def test_inheritance():
    assert isinstance(RotateTransformation(90), TileTransformation)
    assert isinstance(FlipTransformation("horizontal"), TileTransformation)
    assert isinstance(SwapTransformation(), TileTransformation)


def test_transformation_options():
    assert RotateTransformation(90).angle == 90
    assert RotateTransformation(180).angle == 180
    assert RotateTransformation(270).angle == 270

    assert FlipTransformation("horizontal").direction == "horizontal"
    assert FlipTransformation("vertical").direction == "vertical"


def test_scramble_counts_and_unique_targets():
    for size, expected_count in ((3, 6), (4, 12), (5, 20)):
        puzzle = create_test_puzzle(size)
        puzzle.scramble()

        assert len(puzzle.scramble_plan) == expected_count
        assert {item[0] for item in puzzle.scramble_plan} == {
            "swap",
            "rotate",
            "flip",
        }

        involved = []
        for item in puzzle.scramble_plan:
            if item[0] == "swap":
                involved.extend(item[1:3])
            else:
                involved.append(item[1])

        assert len(involved) == len(set(involved))
        assert not puzzle.is_solved()


def test_hints():
    puzzle = create_test_puzzle(3)
    puzzle.swap(0, 1)

    assert puzzle.get_hint() is not None
    assert puzzle.get_hint() is not None
    assert puzzle.get_hint() is not None
    assert puzzle.hints_used == 3
    assert puzzle.get_hint() is None
    assert puzzle.hints_used == 3

    assert puzzle.hint_positions is not None
    puzzle.rotate(0)
    assert puzzle.hint_positions is None


def test_solve():
    puzzle = create_test_puzzle(3)
    puzzle.swap(0, 1)
    puzzle.rotate(0)
    puzzle.flip(0)

    assert puzzle.moves == 3

    puzzle.solve()

    assert puzzle.is_solved()
    assert puzzle.moves == 0
    assert puzzle.finished is True
    assert puzzle.hint_positions is None


def test_invalid_grid_size():
    for size in (2, 6):
        try:
            Puzzle(size)
            raise AssertionError("Invalid grid size was accepted.")
        except ValueError:
            pass


if __name__ == "__main__":
    tests = [
        test_grid_sizes,
        test_move_counter,
        test_transformations,
        test_inheritance,
        test_transformation_options,
        test_scramble_counts_and_unique_targets,
        test_hints,
        test_solve,
        test_invalid_grid_size,
    ]

    for test_function in tests:
        test_function()

    print("ALL TESTS PASSED!")


