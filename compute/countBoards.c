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

static bool placePiece(int32_t* origBoardPtr, int32_t* newBoardPtr,
                int boardWidth, int shipLength, int start, bool rotated) {
  //Check for a ship collision
  if (rotated) {
    //Iterate vertically over the board
    int stop = start + (shipLength * boardWidth);
    for (int i = start; i < stop; i += boardWidth) {
      if (origBoardPtr[i] == 0) {
        continue;
      }

      return false;
    }
  } else {
#ifdef USING_AVX512
    //Generate mask for loading ship remainder
    int remainingLength = shipLength % 16;
    int32_t* nextTilePtr = origBoardPtr + start;
    uint16_t mask = _bzhi_u32(0xFFFF, remainingLength);

    //Horizontally check for a ship on the board, using AVX-512
    for (int i = 0; i < shipLength / 16; i++) {
      __m512i result = _mm512_loadu_epi32((__m512i const *)(nextTilePtr));
      nextTilePtr += 16;
      if (!_mm512_mask2int(_mm512_cmpneq_epi32_mask(result, _mm512_setzero_epi32()))) {
        continue;
      }

      return false;
    }

    //Check any remainder of the ship
    __m512i result = _mm512_maskz_loadu_epi32(mask, nextTilePtr);

    if (_mm512_mask2int(_mm512_cmpneq_epi32_mask(result, _mm512_setzero_epi32()))) {
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
  }

  //Copy the original board, as a ship is going to be placed
  memcpy(newBoardPtr, origBoardPtr, boardWidth * boardWidth * sizeof(newBoardPtr[0]));

  //Place the ship
  if (rotated) {
    //Iterate vertically over the board
    int stop = start + (shipLength * boardWidth);
    for (int i = start; i < stop; i += boardWidth) {
      newBoardPtr[i] = 1;
    }
  } else {
    //Iterate horizontally over the board
    for (int i = start; i < start + shipLength; i++) {
      newBoardPtr[i] = 1;
    }
  }

  return true;
}

void compute(int* shipLengthsPtr, unsigned long long int* totalBoardsPtr,
             int boardWidth, int32_t* boardPtr, int validShipIndicesCount,
             int* validShipIndicesPtr) {
  //Return if all ships have been placed
  if (validShipIndicesCount != 0) {
    for (int rawShipIndex = 0; rawShipIndex < validShipIndicesCount; rawShipIndex++) {
      int validShipIndex = validShipIndicesPtr[rawShipIndex];

      //Filter the currently selected ship out for next recursion
      int newShipCount = validShipIndicesCount - 1;
      int updatedShipIndices[newShipCount];
      if (newShipCount > 0) {
        int nextEmpty = 0;
        for (int i = 0; i < newShipCount + 1; i++) {
          int newIndex = validShipIndicesPtr[i];
          if (newIndex != validShipIndex) {
            updatedShipIndices[nextEmpty] = newIndex;
            nextEmpty++;
          }
        }
      }

      //Create a new empty board, to copy the last good board onto when placing a ship
      int32_t newBoard[boardWidth * boardWidth];

      int shipLength = shipLengthsPtr[validShipIndex];
      int reducedLength = boardWidth - (shipLength - 1);

      //Attempt to place the current ship on the new board, and recurse
      for (int x = 0; x < boardWidth; x++) {
        for (int y = 0; y < reducedLength; y++) {
          //Attempt to place vertically
          bool success = placePiece(boardPtr, newBoard, boardWidth,
                                    shipLength, (y * boardWidth) + x, true);

          //Move on to the next ship
          if (success) {
            compute(shipLengthsPtr, totalBoardsPtr, boardWidth,
                    newBoard, newShipCount, updatedShipIndices);
          }

          //Attempt to place horizontally
          success = placePiece(boardPtr, newBoard, boardWidth,
                               shipLength, (x * boardWidth) + y, false);

          //Move on to the next ship
          if (!success) {
            continue;
          }

          compute(shipLengthsPtr, totalBoardsPtr, boardWidth,
                  newBoard, newShipCount, updatedShipIndices);
        }
      }
    }
  } else {
    //Increase total valid boards found, only print every 10 million
    if (++(*totalBoardsPtr) % 10000000 != 0) {
      return;
    }

    printf("Found valid board %lli\n", *totalBoardsPtr);
  }

  return;
}

int main() {
  //Configurable inputs
  int shipLengths[5] = {5, 4, 3, 3, 2};
  const unsigned int boardWidth = 7;

  int32_t board[boardWidth * boardWidth];
  unsigned long long int totalBoards = 0;

  //Initialise with 0s
  memset(&board, 0, boardWidth * boardWidth * sizeof(board[0]));

  //Initialise ship indices (0 -> n)
  const int validShipCount = sizeof(shipLengths) / sizeof(shipLengths[0]);
  int validShipIndices[validShipCount];
  for (int i = 0; i < validShipCount; i++) {
    validShipIndices[i] = i;
  }

  struct timespec start, finish;
  timespec_get(&start, TIME_UTC);

  //Do actual calculations
  compute(shipLengths, &totalBoards, boardWidth, board, validShipCount, validShipIndices);

  //Calculate time delta to nearest nanosecond
  timespec_get(&finish, TIME_UTC);
  double deltaTime = (double)(finish.tv_sec - start.tv_sec) + ((double)(finish.tv_nsec - start.tv_nsec) / 1000000000.0f);
  double boardRate = (double)totalBoards / deltaTime;

  printf("\nFound %lli boards in %0.2f seconds\n", totalBoards, deltaTime);
  printf("%0.2f boards / second\n", boardRate);

  return EXIT_SUCCESS;
}
