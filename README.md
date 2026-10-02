# HIT137 Group Assignment 3 — Image Scramble Puzzle

A desktop image-scramble puzzle developed for HIT137 Group Assignment 3.

The application uses Python, Tkinter, OpenCV, NumPy and Pillow. It demonstrates
object-oriented programming, image processing, GUI development and
inheritance/polymorphism through transformation classes.

## Features

- JPG, JPEG, PNG and BMP image loading
- 3x3, 4x4 and 5x5 grid selection before loading
- OpenCV resizing and even grid preparation
- Random Swap, Rotate and Flip transformations
- 6 transformations for 3x3, 12 for 4x4 and 20 for 5x5
- Every scramble transformation is generated before application
- No tile is targeted more than once during a scramble
- Original and scrambled images displayed side by side
- Faint grid drawn only over the transformed image
- Left-click selection and tile swapping
- Right-click 90-degree clockwise rotation
- Shift + left-click horizontal flip
- Green indicators for correctly placed/oriented tiles
- Moves and incorrect-tile counters
- Maximum of three hints per image
- Hints shown on both the current and home positions
- Hints disappear after the next actual move
- Completion notification and input lock
- Solve button that restores the puzzle and clears moves

## Project Structure

```text
HIT137-Assignment-3/
├── assignment.py
├── gui.py
├── image_processing.py
├── puzzle.py
├── transformations.py
├── test_puzzle.py
├── test_integration.py
├── github_link.txt
└── README.md
```

## Requirements

Install the required packages:

```bash
pip install opencv-python numpy pillow
```

Tkinter is included with standard Python installations on Windows.

## Run the application

From the project folder:

```bash
python assignment.py
```

## Run the tests

```bash
python test_puzzle.py
python test_integration.py
```

Both test files should finish with:

```text
ALL TESTS PASSED!
```
