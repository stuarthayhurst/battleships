## battleships
  - A repository to experiment with the battleships board game
  - I don't particularly like battleships, but it makes for interesting problem solving

## Sub-projects:
  - Battleships computer opponent: A computer opponent to play battleships against
  - Battleships board compute: Find every valid battleships layout, according to grid size and a set of ship lengths
    - Includes AVX2 and AVX-512 accelerated C implementations

## Battleships computer opponent:
  - `battleships.py` runs a game of battleships, with options to play with 2 players, against the computer, or watch the computer play against a random number generator
  - The computer opponent has been designed to be as hard as is possible
  - The opponent plays completely fairly, and can't see the locations of your ships (read the source code if you don't believe me)
  - The opponents are stored in `opponents/`, and can be benchmarked with `./benchmark.py`

## Battleships board compute:
  - `compute/countBoards.py` will calculate the number of valid battleships layouts from a grid size and list of ship lengths
    - This code has been written with `pypy3` in mind, and is strongly suggested to be used (~5x performance improvement)
    - This script takes around 13.5 seconds to run using a Ryzen 7 7700X and `pypy3`
      - With `n` being the number of ships and `w` being with width of the board, the time complexity scales with `O((w^2 * 2)^n * n!)`
        - This is the unoptimised time complexity, if every board was checked
        - In reality, it likely won't scale this way, as most boards are discarded early
      - Using 5 ships and a width of 7, this gives ~1.1 trillion combinations to try
  - **Alternatively**, `compute/countBoards.c` is a C implementation of the same algorithm
    - This runs in about 0.5 seconds, using a Ryzen 7 7700X
      - However, optimisation work has only been done on Zen 3, Zen 3+ and Zen 4 systems
    - Compile: `make -C compute`
      - Supports `DEBUG=[true/false]` to enable debug support and verbose build output
      - Supports `VERBOSE=[true/false]` to enable verbose build output
      - Supports `ARCH=[microarchitecture]` to target a specific microarchitecture
        - Defaults to using `-march=native`
        - `ARCH=x86-64` could be helpful to run on any x86-64 CPU, if being used to benchmark
      - Supports `AVX2=[true/false]` to enable AVX2 optimisations
      - Supports `AVX512=[true/false]` to enable AVX-512 optimisations
      - Supports `AVX512_SHORT=[true/false]` to enable AVX-512 optimisations, with 8-bit elements
        - AVX2, AVX-512 and AVX-512 8-bit optimisations are enabled by default
        - They'll be used in order of AVX-512 8-bit -> AVX-512 -> AVX2 -> scalar
          - The Makefile selects which options the code is allowed to use
          - The code tests for support at compile time and makes a decision
      - Supports `BOARD_TYPE_SIZE=[integer]` to force a specific board element size
        - Defaults to `32`
        - If `AVX512_SHORT` is enabled and supported, this will be overridden
      - Supports `BOARD_WIDTH=[integer]` to force a select board width
        - Defaults to `7`
    - Run: `./compute/countBoards`
  - These programs don't save the boards, but could easily be modified to save or print them
  - Comparison of implementation performance:

    | Runner + version      | Runtime | Valid boards / s |
    |:----------------------|:--------|:-----------------|
    | Python (3.12)         | 71.56s  | 1,743,000        |
    | Pypy3 (3.10 / 7.3.16) | 13.28s  | 9,394,000        |
    | C (Scalar) (GCC-15)   | 0.63s   | 198,900,000      |
    | C (AVX2) (GCC-15)     | 0.55s   | 228,900,000      |
    | C (AVX-512) (GCC-15)  | 0.80s   | 155,100,000      |
    | C (AVX-512S) (GCC-15) | 0.46s   | 269,800,000      |

    - Runtime is rounded to 2 decimal places
    - Number of valid boards per second is rounded to 4 significant figures
  - Comparison of SIMD selection performance by runtime (Ryzen 7 9700X, GCC-14):

    | SIMD     | 9x9   | 10x10   | 11x11   | 12x12   | 13x13     |
    |:---------|:------|:--------|:--------|:--------|:----------|
    | Scalar   | 18.74s|   67.56s|  379.26s|  1396.50s|          |
    | AVX2     | 26.94s|   89.10s|  531.56s|  1633.51s|          |
    | AVX512   | 19.71s|  121.06s|  363.69s|  1330.86s|          |
    | AVX512S  | 16.02s|   83.26s|  234.88s|   786.12s|  2087.83s|
