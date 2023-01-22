#!/usr/bin/python3
import os, random
import controller

class Player(controller.BaseController):
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    super().__init__(pieceIdentifiers, pieceInfo, playerNum)

  #Helper function to clear the screen and display player number
  def resetScreen(self):
    os.system("clear")
    print(f"Player {self.playerNum}: (computer)")

  def intToRef(self, coord):
    #Convert coord to alphabetical grid reference
    return chr(coord + 96)

  def placeShips(self, grid):
    #Fill the grids with ships
    for piece in self.pieceIdentifiers:
      placing = True

      print(f"Placing {self.pieceInfo[piece][0]}")

      #Keep trying to place until it succeeds
      while placing:
        flipped = bool(random.randint(0, 1))

        xCoord = self.intToRef(random.randint(1, len(grid[0])))
        position = f"{xCoord}, {random.randint(1, len(grid))}"

        #Attempt to place the piece
        if self.playerHelpers.placePiece(grid, piece, flipped, position, False):
          placing = False

  def nextMove(self, usedMoves, remainingShips):
    self.resetScreen()
    self.playerHelpers.printShips(remainingShips)
    self.playerHelpers.drawGrid(usedMoves)

    while True:
      #Take input and validate position
      xCoord = self.intToRef(random.randint(1, len(usedMoves[0])))
      position = f"{xCoord}, {random.randint(1, len(usedMoves))}"
      x, y = self.playerHelpers.inputToReference(position, usedMoves, False)

      #Check coords were actually returned
      if x == None:
        continue

      #Check coords haven't already been used
      if usedMoves[y][x] != "0":
        continue

      break

    return [x, y]
