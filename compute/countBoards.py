#!/usr/bin/python3

import time

def placePiece(grid, length, x, y, flipped):
  #Return false if another ship is in the way
  if not flipped:
    for i in range(x, x + length):
      if grid[y][i] != 0:
        return [], False
  else:
    for i in range(y, y + length):
      if grid[i][x] != 0:
        return [], False

  newGrid = [row[:] for row in grid]

  #Place the ship on the grid
  if not flipped:
    for i in range(x, x + length):
      newGrid[y][i] = 1
  else:
    for i in range(y, y + length):
      newGrid[i][x] = 1

  return newGrid, True

def compute(validShips, grid):
  global n
  if len(validShips) == 0:
    n += 1
    if n % 10000000 == 0:
      print(f"Found valid board {n}")
    return

  shipLength = shipData[validShips[0]]
  newValidShips = validShips[1:]
  reducedLength = boardSize - (shipLength - 1)
  for x in range(boardSize):
    for y in range(reducedLength):
      newBoard, success = placePiece(grid, shipLength, x, y, True)
      if success:
        compute(newValidShips, newBoard)
  for x in range(reducedLength):
    for y in range(boardSize):
      newBoard, success = placePiece(grid, shipLength, x, y, False)
      if success:
        compute(newValidShips, newBoard)

shipData = [5, 4, 3, 3, 2]
boardSize = 7

n = 0
initialValidShips = [i for i in range(len(shipData))]
grid = [[0 for i in range(boardSize)] for j in range(boardSize)]

startTime = time.time()
compute(initialValidShips, grid)
deltaTime = time.time() - startTime

print(f"\nFound {n} boards in {round(deltaTime, 2)} seconds")
print(f"{round((n / deltaTime), 2)} boards / second");
