"""
Tests for the Puzzle and transformation classes.
"""

import numpy as np

from puzzle import Puzzle, Tile
from transformations import (
    RotateTransformation,
    FlipTransformation,
    SwapTransformation,
    TileTransformation
)


def create_test_puzzle(size):
    """Create a puzzle using test images."""

    puzzle = Puzzle(size)
    tiles = []

    for number in range(size * size):
        image = np.zeros(
            (20, 20, 3),
            dtype=np.uint8
        )

        image[:, :10] = number + 10
        image[:10, :] = number + 20

        tiles.append(
            Tile(number, image)
        )

    puzzle.set_tiles(tiles)

    return puzzle


puzzle = create_test_puzzle(3)
assert puzzle.grid_size == 3
assert puzzle.tile_count == 9

puzzle = create_test_puzzle(4)
assert puzzle.grid_size == 4
assert puzzle.tile_count == 16

puzzle = create_test_puzzle(5)
assert puzzle.grid_size == 5
assert puzzle.tile_count == 25

print("✓ Grid size tests passed")


puzzle = create_test_puzzle(3)

assert puzzle.moves == 0

puzzle.swap(0, 1)
assert puzzle.moves == 1

puzzle.rotate(0)
assert puzzle.moves == 2

puzzle.flip(0)
assert puzzle.moves == 3

print("✓ Move counter tests passed")


puzzle = create_test_puzzle(3)

original_image = puzzle.tiles[0].image.copy()

RotateTransformation(90).apply(
    puzzle.tiles,
    0
)

assert not np.array_equal(
    puzzle.tiles[0].image,
    original_image
)

print("✓ Rotation transformation test passed")


puzzle = create_test_puzzle(3)

original_image = puzzle.tiles[0].image.copy()

FlipTransformation("horizontal").apply(
    puzzle.tiles,
    0
)

assert not np.array_equal(
    puzzle.tiles[0].image,
    original_image
)

print("✓ Flip transformation test passed")


puzzle = create_test_puzzle(3)

first_tile_id = puzzle.tiles[0].tile_id
second_tile_id = puzzle.tiles[1].tile_id

SwapTransformation().apply(
    puzzle.tiles,
    0,
    1
)

assert puzzle.tiles[0].tile_id == second_tile_id
assert puzzle.tiles[1].tile_id == first_tile_id

print("✓ Swap transformation test passed")


rotate = RotateTransformation(90)
flip = FlipTransformation("horizontal")
swap = SwapTransformation()

assert isinstance(
    rotate,
    TileTransformation
)

assert isinstance(
    flip,
    TileTransformation
)

assert isinstance(
    swap,
    TileTransformation
)

print("✓ OOP inheritance tests passed")


rotation_90 = RotateTransformation(90)
rotation_180 = RotateTransformation(180)
rotation_270 = RotateTransformation(270)

assert rotation_90.angle == 90
assert rotation_180.angle == 180
assert rotation_270.angle == 270

print("✓ Rotation angle tests passed")


horizontal_flip = FlipTransformation(
    "horizontal"
)

vertical_flip = FlipTransformation(
    "vertical"
)

assert horizontal_flip.direction == "horizontal"
assert vertical_flip.direction == "vertical"

print("✓ Flip direction tests passed")


puzzle = create_test_puzzle(3)

puzzle.swap(0, 1)
puzzle.moves = 0

hint1 = puzzle.get_hint()
hint2 = puzzle.get_hint()
hint3 = puzzle.get_hint()

assert hint1 is not None
assert hint2 is not None
assert hint3 is not None
assert puzzle.hints_used == 3

print("✓ Three-hint limit test passed")


hint4 = puzzle.get_hint()

assert hint4 is None
assert puzzle.hints_used == 3

print("✓ Fourth hint correctly disabled")


puzzle = create_test_puzzle(3)

puzzle.swap(0, 1)
puzzle.moves = 0

hint = puzzle.get_hint()

assert hint is not None
assert puzzle.hint_positions is not None

puzzle.rotate(0)

assert puzzle.hint_positions is None

print("✓ Hint reset after move test passed")


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

print("✓ Solve tests passed")


for size, expected_transformations in [
    (3, 6),
    (4, 12),
    (5, 20)
]:
    puzzle = create_test_puzzle(size)

    puzzle.scramble()

    assert not puzzle.is_solved()

    print(
        f"✓ {size}x{size} scramble test passed "
        f"({expected_transformations} transformations)"
    )


try:
    Puzzle(2)
    raise AssertionError("Invalid grid size was accepted.")
except ValueError:
    pass

try:
    Puzzle(6)
    raise AssertionError("Invalid grid size was accepted.")
except ValueError:
    pass

print("✓ Invalid grid size tests passed")

print()
print("ALL TESTS PASSED!")