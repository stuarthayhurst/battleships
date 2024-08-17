#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(USE_AVX512) && defined(__AVX512F__) && defined(__BMI2__)
  #define USING_AVX512
#elif defined(USE_AVX2) && defined(__AVX2__)
  #define USING_AVX2
#endif

#if defined(USING_AVX512) || defined(USING_AVX2)
  #include <immintrin.h>
#endif

#ifdef VERBOSE
  #ifdef USING_AVX512
    #pragma message("Using AVX-512")
  #elif defined(USING_AVX2)
    #pragma message("Using AVX2")
  #else
    #pragma message("Using scalar code")
  #endif
#endif

#define BOARD_WIDTH 7
unsigned long long int totalBoards = 0;

static bool placePieceHoriz(int32_t* origBoardPtr, int32_t* newBoardPtr,
                            int shipLength, int start) {
  //Check for a ship collision horizontally
#ifdef USING_AVX512
  //Generate mask for loading ship remainder
  int remainingLength = shipLength % 16;
  int32_t* nextTilePtr = origBoardPtr + start;
  __mmask16 mask = _bzhi_u32(0xFFFF, remainingLength);

  //Horizontally check for a ship on the board, using AVX-512
  for (int i = 0; i < shipLength / 16; i++) {
    __m512i result = _mm512_loadu_epi32(nextTilePtr);
    nextTilePtr += 16;
    if (!_mm512_test_epi32_mask(result, result)) {
      continue;
    }

    return false;
  }

  //Check any remainder of the ship
  __m512i result = _mm512_maskz_loadu_epi32(mask, nextTilePtr);
  if (_mm512_test_epi32_mask(result, result)) {
    return false;
  }
#elif defined(USING_AVX2)
  //Generate mask for loading ship remainder
  int remainingLength = shipLength % 8;
  int32_t* nextTilePtr = origBoardPtr + start;
  __m256i shipMask = _mm256_setr_epi32((0 < remainingLength) * -1,
                                       (1 < remainingLength) * -1,
                                       (2 < remainingLength) * -1,
                                       (3 < remainingLength) * -1,
                                       (4 < remainingLength) * -1,
                                       (5 < remainingLength) * -1,
                                       (6 < remainingLength) * -1,
                                       (7 < remainingLength) * -1);

  //Horizontally check for a ship on the board, using AVX2
  for (int i = 0; i < shipLength / 8; i++) {
    __m256i result = _mm256_loadu_si256((__m256i const *)(nextTilePtr));
    nextTilePtr += 8;
    if (_mm256_testz_si256(result, result)) {
      continue;
    }

    return false;
  }

  //Check any remainder of the ship
  if (remainingLength > 0) {
    __m256i result = _mm256_maskload_epi32(nextTilePtr, shipMask);
    if (!_mm256_testz_si256(result, result)) {
      return false;
    }
  }
#else
  //Iterate horizontally over the board
  for (int i = start; i < start + shipLength; i++) {
    if (origBoardPtr[i] == 0) {
      continue;
    }

    return false;
  }
#endif

  //Copy the original board, as a ship is going to be placed
  memcpy(newBoardPtr, origBoardPtr, BOARD_WIDTH * BOARD_WIDTH * sizeof(newBoardPtr[0]));

  //Place the ship horizontally
  for (int i = start; i < start + shipLength; i++) {
    newBoardPtr[i] = 1;
  }

  return true;
}

static bool placePieceVert(int32_t* origBoardPtr, int32_t* newBoardPtr,
                           int shipLength, int start) {
  //Check for a ship collision vertically
  int stop = start + (shipLength * BOARD_WIDTH);
  for (int i = start; i < stop; i += BOARD_WIDTH) {
    if (origBoardPtr[i] == 0) {
      continue;
    }

    return false;
  }

  //Copy the original board, as a ship is going to be placed
  memcpy(newBoardPtr, origBoardPtr, BOARD_WIDTH * BOARD_WIDTH * sizeof(newBoardPtr[0]));

  //Place the ship vertically
  stop = start + (shipLength * BOARD_WIDTH);
  for (int i = start; i < stop; i += BOARD_WIDTH) {
    newBoardPtr[i] = 1;
  }

  return true;
}

void compute(int* shipLengthsPtr, int32_t* boardPtr) {
  //Check there's a ship to place, and place it
  int shipLength = *(shipLengthsPtr++);
  if (shipLength != 0) {
    //Create a new empty board, to copy the last good board onto when placing a ship
    int32_t newBoard[BOARD_WIDTH * BOARD_WIDTH];

    //Attempt to place the current ship on the new board, and recurse
    int reducedLength = BOARD_WIDTH - (shipLength - 1);
    for (int x = 0; x < BOARD_WIDTH; x++) {
      for (int y = 0; y < reducedLength; y++) {
        //Attempt to place vertically
        bool success = placePieceVert(boardPtr, newBoard, shipLength, (y * BOARD_WIDTH) + x);

        //Move on to the next location
        if (success) {
         compute(shipLengthsPtr, newBoard);
        }

        //Attempt to place horizontally
        success = placePieceHoriz(boardPtr, newBoard, shipLength, (x * BOARD_WIDTH) + y);

        //Move on to the next location
        if (!success) {
          continue;
        }

        compute(shipLengthsPtr, newBoard);
      }
    }
  } else {
    //Increase total valid boards found, only print every 10 million
    if (++totalBoards % 10000000 == 0) {
      printf("Found valid board %lli\n", totalBoards);
    }
  }
}

int main() {
  //Zero-terminated ship lengths
  int shipLengths[] = {5, 4, 3, 3, 2, 0};

  //Initialise board with 0s
  int32_t board[BOARD_WIDTH * BOARD_WIDTH];
  memset(&board, 0, BOARD_WIDTH * BOARD_WIDTH * sizeof(board[0]));

  struct timespec start, finish;
  timespec_get(&start, TIME_UTC);

  //Do actual calculations
  compute(shipLengths, board);

  //Calculate time delta to nearest nanosecond
  timespec_get(&finish, TIME_UTC);
  double deltaTime = (double)(finish.tv_sec - start.tv_sec) + ((double)(finish.tv_nsec - start.tv_nsec) / 1000000000.0f);
  double boardRate = (double)totalBoards / deltaTime;

  printf("\nFound %lli boards in %0.2f seconds\n", totalBoards, deltaTime);
  printf("%0.2f boards / second\n", boardRate);

  return EXIT_SUCCESS;
}
