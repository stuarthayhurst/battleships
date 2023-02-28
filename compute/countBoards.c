#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

struct DataPtrs {
  int* shipLengthsPtr;
  unsigned long long int* totalBoardsPtr;
  int boardMemSize;
  int boardWidth;
  char* boardPtr;
  int validShipIndicesCount;
  int* validShipIndicesPtr;
};

bool placePiece(char* origBoardPtr, char* newBoardPtr, int boardMemSize, int boardWidth, int shipLength, int x, int y, bool rotated) {
  //Check for a ship collision
  if (rotated) {
    //Iterate vertically over the board
    int start = (y * boardWidth) + x;
    int stop = start + (shipLength * boardWidth);
    for (int i = start; i < stop; i += boardWidth) {
      if (origBoardPtr[i] != 0) {
        return false;
      }
    }
  } else {
    //Iterate horizontally over the board
    int start = (y * boardWidth) + x;
    for (int i = start; i < start + shipLength; i++) {
      if (origBoardPtr[i] != 0) {
        return false;
      }
    }
  }

  //Copy the original board, as a ship is going to be placed
  memcpy(newBoardPtr, origBoardPtr, boardMemSize);

  //Place the ship
  if (rotated) {
    //Iterate vertically over the board
    int start = (y * boardWidth) + x;
    int stop = start + (shipLength * boardWidth);
    for (int i = start; i < stop; i += boardWidth) {
      newBoardPtr[i] = 1;
    }
  } else {
    //Iterate horizontally over the board
    int start = (y * boardWidth) + x;
    for (int i = start; i < start + shipLength; i++) {
      newBoardPtr[i] = 1;
    }
  }

  return true;
}

void compute(struct DataPtrs* dataPtrsPtr) {
  //Return if all ships have been placed
  if (dataPtrsPtr->validShipIndicesCount == 0) {
    //Increase total valid boards found, print every 10 million
    (*dataPtrsPtr->totalBoardsPtr)++;
    if ((*dataPtrsPtr->totalBoardsPtr) % 10000000 == 0) {
      printf("Found valid board %lli\n", (*dataPtrsPtr->totalBoardsPtr));
    }

    return;
  }

  //Copy across constant values between recursions
  struct DataPtrs requiredData;
  requiredData.shipLengthsPtr = dataPtrsPtr->shipLengthsPtr;
  requiredData.totalBoardsPtr = dataPtrsPtr->totalBoardsPtr;
  requiredData.boardMemSize = dataPtrsPtr->boardMemSize;
  requiredData.boardWidth = dataPtrsPtr->boardWidth;

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
    char newBoard[boardWidth * boardWidth];

    int shipLength = dataPtrsPtr->shipLengthsPtr[validShipIndex];
    int reducedLength = boardWidth - (shipLength - 1);
    for (int rotated = 0; rotated <= 1; rotated++) {
      bool rotatedBool = (bool)rotated;
      if (rotatedBool) {
        //Rotated vertically
        for (int x = 0; x < boardWidth; x++) {
          for (int y = 0; y < reducedLength; y++) {
            //Attempt to place the current ship on the new board
            bool success = placePiece(dataPtrsPtr->boardPtr, newBoard, dataPtrsPtr->boardMemSize, boardWidth, shipLength, x, y, rotatedBool);

            //Move on to the next ship
            if (success) {
              requiredData.boardPtr = newBoard;
              compute(&requiredData);
            }
          }
        }
      } else {
        //Rotated horizontally
        for (int x = 0; x < reducedLength; x++) {
          for (int y = 0; y < boardWidth; y++) {
            //Attempt to place the current ship on the new board
            bool success = placePiece(dataPtrsPtr->boardPtr, newBoard, dataPtrsPtr->boardMemSize, boardWidth, shipLength, x, y, rotatedBool);

            //Move on to the next ship
            if (success) {
              requiredData.boardPtr = newBoard;
              compute(&requiredData);
            }
          }
        }
      }
    }
  }

  return;
}

int main() {
  //Configurable inputs
  int shipLengths[5] = {5, 4, 3, 3, 2};
  const int boardWidth = 7;

  char board[boardWidth * boardWidth];
  unsigned long long int totalBoards = 0;

  //Initialise with 0s
  int boardMemSize = boardWidth * boardWidth * sizeof(board[0]);
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

  compute(&initialData);

  printf("Found %lli boards\n", totalBoards);

  return EXIT_SUCCESS;
}
