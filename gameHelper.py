#!/usr/bin/python3

import random

def placePiece(grid, identifier, length, x, y, flipped):
  #Return false if another ship is in the way
  if not flipped:
    for i in range(x, x + length):
      if grid[y][i] != 0:
        return False
  else:
    for i in range(y, y + length):
      if grid[i][x] != 0:
        return False

  #Place the ship on the grid
  if not flipped:
    for i in range(x, x + length):
      grid[y][i] = identifier
  else:
    for i in range(y, y + length):
      grid[i][x] = identifier

  return True

def placeShips(grid, boardSize, pieceInfo):
    #Fill the grids with ships
    for piece in pieceInfo.keys():
      shipLength = pieceInfo[piece]

      #Keep trying to place until it succeeds
      placing = True
      while placing:
        #Generate position
        flipped = bool(random.randint(0, 1))
        reducedLength = boardSize - (shipLength - 1) - 1
        if flipped:
          x, y = random.randint(0, boardSize - 1), random.randint(0, reducedLength)
        else:
          x, y = random.randint(0, reducedLength), random.randint(0, boardSize - 1)

        #Attempt to place the piece
        if placePiece(grid, piece, pieceInfo[piece], x, y, flipped):
          placing = False

def generateBoard(size):
  pieceInfo = {"c": 5, "b": 4, "d": 3, "s": 3, "p": 2}
  grid = [[0 for i in range(size)] for j in range(size)]
  placeShips(grid, 7, pieceInfo)

  return grid

def searchGrid(grid, identifier):
  for row in grid:
    if identifier in row:
      return True
  return False
