"""
Basic tests for the Puzzle and Tile classes.

These tests check the main functionality implemented
for the OOP section of Assignment 3.
"""

import numpy as np

from puzzle import Puzzle, Tile


def create_test_puzzle(size):
    """Create a puzzle using simple test images."""

    puzzle = Puzzle(size)

    tiles = []

    for tile_number in range(size * size):

        image = np.zeros(
            (20, 20, 3),
            dtype=np.uint8
        )

        tile = Tile(
            tile_number,
            image
        )

        tiles.append(tile)

    puzzle.set_tiles(tiles)

    return puzzle


# Test grid sizes

for size, expected_count in [
    (3, 9),
    (4, 16),
    (5, 25)
]:

    puzzle = create_test_puzzle(size)

    assert puzzle.tile_count == expected_count

print("✓ Grid size tests passed")


# Test player moves

puzzle = create_test_puzzle(3)

puzzle.swap(0, 1)

assert puzzle.moves == 1

puzzle.rotate(0)

assert puzzle.moves == 2

puzzle.flip(0)

assert puzzle.moves == 3

print("✓ Move counter tests passed")


# Test hints

puzzle = create_test_puzzle(3)

# Create an incorrect puzzle first.
puzzle.swap(0, 1)

first_hint = puzzle.get_hint()
second_hint = puzzle.get_hint()
third_hint = puzzle.get_hint()

assert first_hint is not None
assert second_hint is not None
assert third_hint is not None

# A fourth hint should not be available.
fourth_hint = puzzle.get_hint()

assert fourth_hint is None
assert puzzle.hints_used == 3

print("✓ Hint tests passed")


# Test Solve

puzzle = create_test_puzzle(3)

puzzle.swap(0, 1)

assert not puzzle.is_solved()

puzzle.solve()

assert puzzle.is_solved()
assert puzzle.moves == 0
assert puzzle.finished is True

print("✓ Solve tests passed")


# Test transformation counts

expected_transformations = {
    3: 6,
    4: 12,
    5: 20
}

for size, expected in expected_transformations.items():

    puzzle = create_test_puzzle(size)

    actual = puzzle.TRANSFORMATION_COUNTS[size]

    assert actual == expected

    puzzle.scramble()

    assert not puzzle.is_solved()

    print(
        f"✓ {size}x{size} scramble test passed "
        f"({actual} transformations)"
    )


print()
print("ALL TESTS PASSED!")