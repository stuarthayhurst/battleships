#if defined(USE_AVX512_SHORT) && defined(__AVX512BW__) && defined(__AVX512VL__) && defined(__BMI2__)
  #define USING_AVX512_SHORT
  #ifdef BOARD_TYPE_SIZE
    #ifdef VERBOSE
      #pragma message("Overriding specified board type size")
    #endif
    #undef BOARD_TYPE_SIZE
  #endif
  #define BOARD_TYPE_SIZE 8
#else
  //Ensure the board type's size is set
  #ifndef BOARD_TYPE_SIZE
    #define BOARD_TYPE_SIZE 32
  #else
    #ifdef VERBOSE
      #pragma message("Using non-default board type")
    #endif
  #endif

  //Determine whether any AVX implementations can be used
  #if defined(USE_AVX512) && (BOARD_TYPE_SIZE == 32) && defined(__AVX512F__) && defined(__BMI2__)
    #define USING_AVX512
  #elif defined(USE_AVX2) && (BOARD_TYPE_SIZE == 32) && defined(__AVX2__)
    #define USING_AVX2
  #endif
#endif

//Report the selection result
#ifdef VERBOSE
  #ifdef USING_AVX512_SHORT
    #pragma message("Using AVX-512 8-bit")
  #elifdef USING_AVX512
    #pragma message("Using AVX-512")
  #elifdef USING_AVX2
    #pragma message("Using AVX2")
  #else
    #pragma message("Using scalar code")
  #endif
#endif

//Create a type from the size
#define MAKE_BOARD_TYPE_N(B_TYPE, B_SIZE, B_SUFFIX) B_TYPE ## B_SIZE ## B_SUFFIX
#define MAKE_BOARD_TYPE(B_TYPE, B_SIZE, B_SUFFIX) MAKE_BOARD_TYPE_N(B_TYPE, B_SIZE, B_SUFFIX)
#define BOARD_TYPE MAKE_BOARD_TYPE(int, BOARD_TYPE_SIZE, _t)

//Pick a board width
#if !defined(BOARD_WIDTH) || (BOARD_WIDTH == 7)
  #undef BOARD_WIDTH
  #define BOARD_WIDTH 7
  #ifdef VERBOSE
    #pragma message("Using default board width")
  #endif
#else
  #ifdef VERBOSE
    #pragma message("Using non-default board width")
  #endif
#endif

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#if defined(USING_AVX512_SHORT) || defined(USING_AVX512) || defined(USING_AVX2)
  #include <immintrin.h>
#endif

uintmax_t totalBoards = 0;

static bool placePieceHoriz(BOARD_TYPE* restrict origBoardPtr, BOARD_TYPE* restrict newBoardPtr,
                            int shipLength, int start) {
  //Check for a ship collision horizontally
#ifdef USING_AVX512_SHORT
  //Generate mask for loading ship remainder
  int remainingLength = shipLength % 16;
  BOARD_TYPE* restrict nextTilePtr = origBoardPtr + start;

  //Horizontally check for a ship on the board, using AVX-512
  for (int i = 0; i < shipLength / 16; i++) {
    __m128i result = _mm_loadu_epi8(nextTilePtr);
    nextTilePtr += 16;
    if (!_mm_test_epi8_mask(result, result)) {
      continue;
    }

    return false;
  }

  //Check any remainder of the ship
  __mmask16 mask = _bzhi_u32(0xFFFF, remainingLength);
  __m128i result = _mm_maskz_loadu_epi8(mask, nextTilePtr);
  if (_mm_test_epi8_mask(result, result)) {
    return false;
  }
#elifdef USING_AVX512
  //Generate mask for loading ship remainder
  int remainingLength = shipLength % 16;
  BOARD_TYPE* restrict nextTilePtr = origBoardPtr + start;

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
  __mmask16 mask = _bzhi_u32(0xFFFF, remainingLength);
  __m512i result = _mm512_maskz_loadu_epi32(mask, nextTilePtr);
  if (_mm512_test_epi32_mask(result, result)) {
    return false;
  }
#elifdef USING_AVX2
  //Generate mask for loading ship remainder
  int remainingLength = shipLength % 8;
  BOARD_TYPE* restrict nextTilePtr = origBoardPtr + start;

  //Horizontally check for a ship on the board, using AVX2
  for (int i = 0; i < shipLength / 8; i++) {
    __m256i result = _mm256_loadu_si256((__m256i const * restrict)(nextTilePtr));
    nextTilePtr += 8;
    if (_mm256_testz_si256(result, result)) {
      continue;
    }

    return false;
  }

  //Check any remainder of the ship
  if (remainingLength > 0) {
    //Generate a mask vector to load the remainder
    __m256i indexVec = _mm256_setr_epi32(0, 1, 2, 3, 4, 5, 6, 7);
    __m256i lengthVec = _mm256_set1_epi32(remainingLength);
    __m256i shipMask = _mm256_cmpgt_epi32(lengthVec, indexVec);

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

static bool placePieceVert(BOARD_TYPE* restrict origBoardPtr, BOARD_TYPE* restrict newBoardPtr,
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

static void compute(int* restrict shipLengthsPtr, BOARD_TYPE* restrict boardPtr) {
  //Check there's a ship to place, and place it
  int shipLength = *(shipLengthsPtr++);
  if (shipLength == 0) {
    //Increase total valid boards found, only print every 10 million
    if (++totalBoards % 10000000 == 0) {
      printf("Found valid board %ju\n", totalBoards);
    }
  } else {
    //Create a new empty board, to copy the last good board onto when placing a ship
    BOARD_TYPE newBoard[BOARD_WIDTH * BOARD_WIDTH];

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
  }
}

int main() {
  //Zero-terminated ship lengths
  int shipLengths[] = {5, 4, 3, 3, 2, 0};

  //Initialise board with 0s
  BOARD_TYPE board[BOARD_WIDTH * BOARD_WIDTH] = {};

  struct timespec start, finish;
  timespec_get(&start, TIME_UTC);

  //Do actual calculations
  compute(shipLengths, board);

  //Calculate time delta to nearest nanosecond
  timespec_get(&finish, TIME_UTC);
  double deltaTime = (double)(finish.tv_sec - start.tv_sec) + ((double)(finish.tv_nsec - start.tv_nsec) / 1000000000.0f);
  double boardRate = (double)totalBoards / deltaTime;

  printf("\nFound %ju boards in %0.2f seconds\n", totalBoards, deltaTime);
  printf("%0.2f boards / second\n", boardRate);

  return EXIT_SUCCESS;
}
