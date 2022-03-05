#!/usr/bin/python3
import os

class Player:
  def __init__(self, pieceIdentifiers, pieceInfo, drawGrid, playerNum):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.drawGrid = drawGrid
    self.playerNum = playerNum

  #Helper function to clear the screen and display player number
  def resetScreen(self):
    os.system("cls||clear")
    print(f"Player {self.playerNum}:\n")

  #Helper function to convert user input into valid coords
  def inputToReference(self, position, grid):
    #Split position into a separate row and column value, attempt to guess format
    if "," in position:
      position = position.split(",")
    else:
      position = position.split(" ")
    if len(position) != 2:
      input("Grid reference must be in the format 'col, row'")
      return None, None

    #Convert to expected data types
    x = str(position[0])
    try:
      y = int(position[1])
    except ValueError:
      input("Row must be an integer")
      return None, None

    #Convert input to grid position
    try:
      x = ord(x) - 97
    except TypeError:
      input("Alphabetical grid reference must be a single character")
      return None, None
    y -= 1

    #Check coords fall inside grid boundaries
    if y > len(grid) - 1 or x > len(grid[0]) - 1 or y < 0 or x < 0:
      input("Coordinates must be within grid boundaries")
      return None, None

    #If the input was valid, return coords
    return x, y

  def placePiece(self, grid, piece, flipped, position):
    x, y = self.inputToReference(position, grid)

    #Check coords were actually returned
    if x == None:
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
    input(f"Player {self.playerNum}: \nPress any key to start placing ships:")

    #Fill the grids with ships
    for piece in self.pieceIdentifiers:
      placing = True
      flipped = False
      #Keep trying to place until it succeeds
      while placing:
        #Clear the screen and draw the grid
        self.resetScreen()
        self.drawGrid(grid, False)

        #Display ship to place
        print(f"\nPlacing {self.pieceInfo[piece][0].capitalize()}:")
        if not flipped:
          print(piece * self.pieceInfo[piece][1])
        else:
          for i in range(self.pieceInfo[piece][1]):
            print(piece)

        #Flip piece or place it
        action = input("Enter f to flip piece, or a grid reference (x, y): ")
        if action == "f":
          flipped = not flipped
        else:
          if self.placePiece(grid, piece, flipped, action):
            placing = False

  def nextMove(self, usedMoves):
    while True:
      #Reset screen each input attempt
      self.resetScreen()
      self.drawGrid(usedMoves, True)

      #Take input and validate position
      position = input("Enter a grid reference to fire at (x, y): ")
      x, y = self.inputToReference(position, usedMoves)

      #Check coords were actually returned
      if x == None:
        continue

      #Check coords haven't already been used
      if usedMoves[y][x] != "0":
        input("The location has already been fired at!")
        continue

      break

    return [x, y]
