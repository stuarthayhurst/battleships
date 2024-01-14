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

//Note: Attribute order must not be changed
//Note: If types change, CopyData will need updating too
struct DataPtrs {
  int* shipLengthsPtr;
  unsigned long long int* totalBoardsPtr;
  unsigned int boardMemSize;
  int boardWidth;
  int32_t* boardPtr;
  int validShipIndicesCount;
  int* validShipIndicesPtr;
};

//Struct for the data frequently copied, only to calculate the size
struct CopyData {int* a; unsigned long long int* b; unsigned int c; int d;};

bool placePiece(int32_t* origBoardPtr, int32_t* newBoardPtr,
                unsigned int boardMemSize, int boardWidth,
                int shipLength, int x, int y, bool rotated) {
  //Starting index for the ship
  int start = (y * boardWidth) + x;

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
  memcpy(newBoardPtr, origBoardPtr, boardMemSize);

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

void compute(struct DataPtrs* dataPtrsPtr) {
  //Return if all ships have been placed
  if (dataPtrsPtr->validShipIndicesCount != 0) {
    //Copy across constant values between recursions
    struct DataPtrs requiredData;
    memcpy(&requiredData, dataPtrsPtr, sizeof(struct CopyData));

    int boardWidth = dataPtrsPtr->boardWidth;
    for (int rawShipIndex = 0; rawShipIndex < dataPtrsPtr->validShipIndicesCount; rawShipIndex++) {
      int validShipIndex = dataPtrsPtr->validShipIndicesPtr[rawShipIndex];

      //Filter the currently selected ship out for next recursion
      int newShipCount = dataPtrsPtr->validShipIndicesCount - 1;
      int updatedShipIndices[newShipCount];
      if (newShipCount > 0) {
        int nextEmpty = 0;
        for (int i = 0; i < newShipCount + 1; i++) {
          int newIndex = dataPtrsPtr->validShipIndicesPtr[i];
          if (newIndex != validShipIndex) {
            updatedShipIndices[nextEmpty] = newIndex;
            nextEmpty++;
          }
        }
      }

      //Update the list of valid ships for next recursion
      requiredData.validShipIndicesPtr = updatedShipIndices;
      requiredData.validShipIndicesCount = newShipCount;

      //Create a new empty board, to copy the last good board onto when placing a ship
      int32_t newBoard[boardWidth * boardWidth];

      int shipLength = dataPtrsPtr->shipLengthsPtr[validShipIndex];
      int reducedLength = boardWidth - (shipLength - 1);

      //Attempt to place the current ship on the new board, and recurse
      for (int x = 0; x < boardWidth; x++) {
        for (int y = 0; y < reducedLength; y++) {
          //Attempt to place vertically
          bool success = placePiece(dataPtrsPtr->boardPtr, newBoard,
                                    dataPtrsPtr->boardMemSize, boardWidth,
                                    shipLength, x, y, true);

          //Move on to the next ship
          if (success) {
            requiredData.boardPtr = newBoard;
            compute(&requiredData);
          }

          //Attempt to place horizontally
          success = placePiece(dataPtrsPtr->boardPtr, newBoard,
                               dataPtrsPtr->boardMemSize, boardWidth,
                               shipLength, y, x, false);

          //Move on to the next ship
          if (!success) {
            continue;
          }

          requiredData.boardPtr = newBoard;
          compute(&requiredData);
        }
      }
    }
  } else {
    //Increase total valid boards found, only print every 10 million
    (*dataPtrsPtr->totalBoardsPtr)++;
    if ((*dataPtrsPtr->totalBoardsPtr) % 10000000 != 0) {
      return;
    }

    printf("Found valid board %lli\n", (*dataPtrsPtr->totalBoardsPtr));
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
  const int boardMemSize = boardWidth * boardWidth * sizeof(board[0]);
  memset(&board, 0, boardMemSize);

  //Initialise ship indices (0 -> n)
  const int validShipCount = sizeof(shipLengths) / sizeof(shipLengths[0]);
  int validShipIndices[validShipCount];
  for (int i = 0; i < validShipCount; i++) {
    validShipIndices[i] = i;
  }

  //Pack data into struct to start recursion
  struct DataPtrs initialData;
  initialData.shipLengthsPtr = &shipLengths[0];
  initialData.totalBoardsPtr = &totalBoards;
  initialData.boardMemSize = boardMemSize;
  initialData.boardWidth = boardWidth;
  initialData.boardPtr = board;
  initialData.validShipIndicesCount = validShipCount;
  initialData.validShipIndicesPtr = &validShipIndices[0];

  struct timespec start, finish;
  timespec_get(&start, TIME_UTC);

  //Do actual calculations
  compute(&initialData);

  //Calculate time delta to nearest nanosecond
  timespec_get(&finish, TIME_UTC);
  double deltaTime = (double)(finish.tv_sec - start.tv_sec) + ((double)(finish.tv_nsec - start.tv_nsec) / 1000000000.0f);
  double boardRate = (double)totalBoards / deltaTime;

  printf("\nFound %lli boards in %0.2f seconds\n", totalBoards, deltaTime);
  printf("%0.2f boards / second\n", boardRate);

  return EXIT_SUCCESS;
}
