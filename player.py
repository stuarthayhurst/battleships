#!/usr/bin/python3
import os

class Player:
  def __init__(self, pieceIdentifiers, pieceInfo, drawGrid):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.drawGrid = drawGrid

  def placePiece(self, grid, piece, flipped):
    #Take desired coords
    x = str(input("Enter alphabetical column: "))
    try:
      y = int(input("Enter numerical row: "))
    except ValueError:
      input("Row must be an integer")
      return False

    #Convert input to grid position
    try:
      x = ord(x) - 97
    except TypeError:
      input("Alphabetical grid reference must be a single character")
      return False
    y -= 1

    #Check coords fall inside grid boundaries
    if y > len(grid) - 1 or x > len(grid[0]) - 1 or y < 0 or x < 0:
      input("Coordinates must be within grid boundaries")
      return False

    #Return false if the ship won't fit
    shipLength = self.pieceInfo[piece][1]
    pieceName = self.pieceInfo[piece][0].capitalize()
    if not flipped:
      if x + shipLength > len(grid[0]):
        input(f"{pieceName} won't fit there")
        return False
    else:
      if y + shipLength > len(grid):
        input(f"{pieceName} won't fit there")
        return False

    #Return false if another ship is in the way
    if not flipped:
      for i in range(x, x + shipLength):
        if grid[y][i] != "0":
          input(f"{pieceName} would collide with another ship")
          return False
    else:
      for i in range(y, y + shipLength):
        if grid[i][x] != "0":
          input(f"{pieceName} would collide with another ship")
          return False

    #Place the ship on the grid
    if not flipped:
      for i in range(x, x + shipLength):
        grid[y][i] = piece
    else:
      for i in range(y, y + shipLength):
        grid[i][x] = piece

    return True

  def placeShips(self, grid):
    #Wait for input, to allow any players to swap
    input("Press any key to start placing ships")

    #Fill the grids with ships
    for piece in self.pieceIdentifiers:
      placing = True
      flipped = False
      #Keep trying to place until it succeeds
      while placing:
        #Clear the screen and draw the grid
        os.system("cls||clear")
        self.drawGrid(grid, False)

        #Display ship to place
        print(f"\nPlacing {self.pieceInfo[piece][0].capitalize()}:")
        if not flipped:
          print(piece * self.pieceInfo[piece][1])
        else:
          for i in range(self.pieceInfo[piece][1]):
            print(piece)

        #Flip piece or place it
        action = input("Enter f to flip piece, or nothing to place piece: ")
        if action == "f":
          flipped = not flipped
        else:
          if self.placePiece(grid, piece, flipped):
            placing = False
