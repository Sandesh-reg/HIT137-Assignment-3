"""
HIT137 Group Assignment 3 - Image Scramble Puzzle.

Application entry point. The project is split into:
- gui.py: Tkinter interface and user interaction
- image_processing.py: OpenCV image loading and tiling
- puzzle.py: puzzle state, scrambling, moves, hints and solving
- transformations.py: transformation classes demonstrating inheritance
  and polymorphism
"""


from gui import PuzzleApp


def main():
    """Start the Tkinter puzzle application."""
    PuzzleApp().run()


if __name__ == "__main__":
    main()
