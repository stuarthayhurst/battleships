## battleships
  - A repository to experiment with the battleships board game
  - I don't particularly like battleships, but it makes for interesting problem solving

## Sub-projects:
  - Battleships computer opponent: A computer opponent to play battleships against
  - Battleships board compute: Find every valid battleships layout, according to grid size and a set of ship lengths

## Battleships computer opponent:
  - `battleships.py` runs a game of battleships, with options to play with 2 players, against the computer, or watch the computer play against a random number generator
  - The computer opponent has been designed to be as hard as is possible
  - The opponent plays completely fairly, and can't see the locations of your ships (read the source code if you don't believe me)
  - The opponents are stored in `opponents/`, and can be benchmarked with `./benchmark.py`

## Battleships board compute:
  - `compute/countBoards.py` will calculate the number of valid battleships layouts from a grid size and list of ship lengths
  - The code has been written with `pypy3` in mind, this is strongly suggested to be used (~6x performance improvement)
  - This script takes around 45 minutes to run using a Ryzen 5 5600X
    - With `n` being the number of ships and `w` being with width of the board, the time compelxity scales with `O(w^2 * 2)^n * n!`
    - Using a width of 7 and 5 ships, this gives ~ 1.1 trillion combinations to try

## To-do:
  - Rewrite board compute in C, add Makefile, document and show benchmarks
  - Finish to-do list in `battleships.py`
