## battleships
  - A repository to experiment with the battleships board game
  - I don't particularly like battleships, but it makes for interesting problem solving

## Sub-projects:
  - Battleships computer opponent: A computer opponent to play battleships against
  - Battleships board compute: Find every valid battleships layout, according to grid size and a set of ship lengths
    - Includes an AVX2 + AVX-512 accelerated C implementation

## Battleships computer opponent:
  - `battleships.py` runs a game of battleships, with options to play with 2 players, against the computer, or watch the computer play against a random number generator
  - The computer opponent has been designed to be as hard as is possible
  - The opponent plays completely fairly, and can't see the locations of your ships (read the source code if you don't believe me)
  - The opponents are stored in `opponents/`, and can be benchmarked with `./benchmark.py`

## Battleships board compute:
  - `compute/countBoards.py` will calculate the number of valid battleships layouts from a grid size and list of ship lengths
    - This code has been written with `pypy3` in mind, and is strongly suggested to be used (~5x performance improvement)
    - This script takes around 36 minutes to run using a Ryzen 7 7700X and `pypy3`
      - With `n` being the number of ships and `w` being with width of the board, the time complexity scales with `O((w^2 * 2)^n * n!)`
        - This is the unoptimised time complexity, if every board was checked
        - In reality, it likely won't scale this way, as most boards are discarded early
      - Using 5 ships and a width of 7, this gives ~1.1 trillion combinations to try
  - **Alternatively**, `compute/countBoards.c` is a C implementation of the same algorithm
    - This runs in about 1 minute and 10 seconds, using a Ryzen 7 7700X
      - However, optimisation work has only been done on Zen 3, Zen 3+ and Zen 4 systems
    - Compile: `make -C compute`
      - Supports `FAST=[true/false]` to enable additional optimisations
      - Supports `DEBUG=[true/false]` to enable debug symbols and verbose build output
      - Supports `VERBOSE=[true/false]` to enable verbose build output
      - Supports `AVX2=[true/false]` to disable AVX2 optimisations
        - AVX2 optimisations are enabled by default, when supported
      - Supports `AVX512=[true/false]` to enable AVX-512 optimisations
        - AVX-512 optimisations are disabled by default
        - If `AVX2` and `AVX512` are both true, `AVX512` will be chosen
    - Run: `./compute/countBoards`
  - These programs don't save the boards, but could easily be modified to save or print them
  - Comparison of implementation performance:
<br><br>
    | Runner + version     | Runtime  | Valid boards / s |
    |:---------------------|:---------|------------------|
    | Python (3.12)        | 169m 51s | 1,469,000        |
    | Pypy3 (3.9 / 7.3.15) | 35m 52s  | 6,957,000        |
    | C (Scalar)           | 1m 21s   | 184,900,000      |
    | C (AVX2)             | 1m 10s   | 212,800,000      |
    | C (AVX-512)          | 1m 11s   | 210,100,000      |
