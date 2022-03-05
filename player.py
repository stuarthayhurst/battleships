#!/usr/bin/python3
import os
import controller

class Player(controller.BaseController):
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    super().__init__(pieceIdentifiers, pieceInfo, playerNum)

  #Helper function to clear the screen and display player number
  def resetScreen(self):
    os.system("cls||clear")
    print(f"Player {self.playerNum}:")

  def placeShips(self, grid):
    #Wait for input, to allow any players to swap
    input(f"Player {self.playerNum}: \nPress any key to start placing ships:")

    #Fill the grids with ships
    for piece in self.pieceIdentifiers:
      placing = True
      flipped = False
      #Keep trying to place until it succeeds
      while placing:
        #Clear the screen and draw the grid
        self.resetScreen()
        self.playerHelpers.drawGrid(grid)

        #Display ship to place
        print(f"\nPlacing {self.pieceInfo[piece][0]}:")
        if not flipped:
          print(piece * self.pieceInfo[piece][1])
        else:
          for i in range(self.pieceInfo[piece][1]):
            print(piece)

        #Flip piece or place it
        action = input("Enter r to rotate piece, or a grid reference (x, y): ")
        if action == "f" or action == "r":
          flipped = not flipped
        else:
          if self.playerHelpers.placePiece(grid, piece, flipped, action, True):
            placing = False

    self.resetScreen()
    self.playerHelpers.drawGrid(grid)
    input("\nPress any key to continue")

  def nextMove(self, usedMoves, remainingShips):
    while True:
      #Reset screen each input attempt
      self.resetScreen()
      self.playerHelpers.printShips(remainingShips)
      self.playerHelpers.drawGrid(usedMoves)

      #Take input and validate position
      position = input("Enter a grid reference to fire at (x, y): ")
      x, y = self.playerHelpers.inputToReference(position, usedMoves, True)

      #Check coords were actually returned
      if x == None:
        continue

      #Check coords haven't already been used
      if usedMoves[y][x] != "0":
        input("The location has already been fired at!")
        continue

      print()
      break

    return [x, y]
