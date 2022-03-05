#!/usr/bin/python3
import os, time
import player
import computer

#Board identifiers, as well as corresponding names and ship lengths
pieceIdentifiers = ["c", "b", "d", "s", "p"]
pieceInfo = {
  "c": ["carrier", 5],
  "b": ["battleship", 4],
  "d": ["destroyer", 3],
  "s": ["submarine", 3],
  "p": ["patrol boat", 2]
}

class PlayerHelpers:
  def __init__(self, pieceInfo):
    self.pieceInfo = pieceInfo

  #Helper function to convert user input into valid coords
  def inputToReference(self, position, grid, verbose):
    #Split position into a separate row and column value, attempt to guess format
    if "," in position:
      position = position.split(",")
    else:
      position = position.split(" ")
    if len(position) != 2:
      if verbose:
        input("Grid reference must be in the format 'col, row'")
      return None, None

    #Convert to expected data types
    x = str(position[0])
    try:
      y = int(position[1])
    except ValueError:
      if verbose:
        input("Row must be an integer")
      return None, None

    #Convert input to grid position
    try:
      x = ord(x) - 97
    except TypeError:
      if verbose:
        input("Alphabetical grid reference must be a single character")
      return None, None
    y -= 1

    #Check coords fall inside grid boundaries
    if y > len(grid) - 1 or x > len(grid[0]) - 1 or y < 0 or x < 0:
      if verbose:
        input("Coordinates must be within grid boundaries")
      return None, None

    #If the input was valid, return coords
    return x, y

  def placePiece(self, grid, piece, flipped, position, verbose):
    x, y = self.inputToReference(position, grid, verbose)

    #Check coords were actually returned
    if x == None:
      return False

    #Return false if the ship won't fit
    shipLength = self.pieceInfo[piece][1]
    pieceName = self.pieceInfo[piece][0].capitalize()
    if not flipped:
      if x + shipLength > len(grid[0]):
        if verbose:
          input(f"{pieceName} won't fit there")
        return False
    else:
      if y + shipLength > len(grid):
        if verbose:
          input(f"{pieceName} won't fit there")
        return False

    #Return false if another ship is in the way
    if not flipped:
      for i in range(x, x + shipLength):
        if grid[y][i] != "0":
          if verbose:
            input(f"{pieceName} would collide with another ship")
          return False
    else:
      for i in range(y, y + shipLength):
        if grid[i][x] != "0":
          if verbose:
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

  def printShips(self, remainingShips):
    #Print the reamining ships
    print("Target ships:", end = "")
    for ship in remainingShips:
      print(f" {self.pieceInfo[ship][0]}", end = "")
    print("\n")

class GameController:
  def __init__(self, pieceIdentifiers, pieceInfo):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.controllers = [0, 0]
    self.startTime = 0
    self.playerHelpers = PlayerHelpers(self.pieceInfo)

  #Return a list of blank grids (1 for each controller)
  def createGrids(self, gridWidth, gridHeight):
    if gridWidth <= 26 and gridHeight <= 26:
      return [[["0" for x in range(gridWidth)] for i in range(gridHeight)] for grid in range (2)]
    else:
      return False

  #Print the passed grid, hiding any ships if specified
  def drawGrid(self, grid, hideShips):
    #Print alphabetical grid references as header
    print("   ", end = "")

    for i in range(len(grid[0])):
      #Print each alphabetical grid reference
      print(chr(i + 65), end = "")
    print()

    #Iterate over grid coords
    for rowNum, row in enumerate(grid):
      #Prefix a zero if single digit
      rowNum += 1
      if rowNum < 10:
        print("0", end = "")
      print(f"{rowNum} ", end = "")

      for col in row:
        #If the piece isn't a ship, or ships are being shown, show the actual piece
        if col not in self.pieceIdentifiers or hideShips == False:
          print(col, end = "")
        #Otherwise, censor any ships
        else:
          print("0", end = "")
      print()

  def checkWinner(self, grid):
    #Return true if all pieces are gone
    for row in grid:
      for i in row:
        if i != "0":
          return False
    return True

  def placeMove(self, grid, usedMoves, move, delay):
    hitTile = grid[move[1]][move[0]]

    print(f"Firing at {chr(move[0] + 97).upper()}, {move[1] + 1}", end = "", flush = True)
    if delay:
      for i in range(3):
        time.sleep(0.2)
        print(".", end = "", flush = True)
      time.sleep(0.2)
      print(" ", end = "")
    else:
      print("... ", end = "")

    #If guess was a miss, blank that tile and return
    if hitTile not in self.pieceIdentifiers:
      usedMoves[move[1]][move[0]] = " "
      print("miss!")
      return

    print("hit!")
    usedMoves[move[1]][move[0]] = "X"
    grid[move[1]][move[0]] = "0"

    #Return if the full ship hasn't been hit
    for row in grid:
      if hitTile in row:
        return

    #Whichever ship was hit is no longer on the grid, announce it sank
    print(f"Enemy {self.pieceInfo[hitTile][0]} was sunk!")

  def printRuntime(self):
    runtimeSeconds = time.time() - self.startTime
    runtimeMinutes = int(runtimeSeconds // 60)
    runtimeSeconds = int(runtimeSeconds % 60)

    print(f"\nGame runtime: {runtimeMinutes}:{runtimeSeconds:02d}")

  def setup(self, gridWidth, gridHeight):
    #Initialise grids
    self.grids = self.createGrids(gridWidth, gridHeight) #Store player ships
    self.moves = self.createGrids(gridWidth, gridHeight) #Store moves made

    if not self.grids:
      return False
    return True

  def reset(self):
    gridWidth = len(self.grids[0][0])
    gridHeight = len(self.grids[0])
    self.grids = self.createGrids(gridWidth, gridHeight)
    self.moves = self.createGrids(gridWidth, gridHeight)

  def addPlayers(self, controllers):
    #Create a controller for each player
    self.controllers[0] = controllers[0](self.pieceIdentifiers, self.pieceInfo, self.drawGrid, 1)
    self.controllers[0].passHelpers(self.playerHelpers)
    self.controllers[1] = controllers[1](self.pieceIdentifiers, self.pieceInfo, self.drawGrid, 2)
    self.controllers[1].passHelpers(self.playerHelpers)

  def getShips(self, grid):
    #Find all remaining ships
    ships = []
    for row in grid:
      for col in row:
        if col != "0" and col not in ships:
          ships.append(col)
    return sorted(ships)

  def start(self, delayHit):
    #Start game timer
    self.startTime = time.time()

    os.system("cls||clear")
    self.controllers[0].placeShips(self.grids[0])
    os.system("cls||clear")
    self.controllers[1].placeShips(self.grids[1])

    while True:
      #Get next move from controller, using existing moves and remaining ships
      move = self.controllers[0].nextMove(self.moves[0], self.getShips(self.grids[1]))
      #Update enemy grid and made moves grids
      self.placeMove(self.grids[1], self.moves[0], move, delayHit)
      #If the game is over, exit
      if self.checkWinner(self.grids[1]):
        winner = "Player 1"
        break

      #Wait for next player
      if delayHit:
        input("\nPress any key to continue")

      #Same as controller 1
      move = self.controllers[1].nextMove(self.moves[1], self.getShips(self.grids[0]))
      self.placeMove(self.grids[0], self.moves[1], move, delayHit)
      if self.checkWinner(self.grids[0]):
        winner = "Player 2"
        break

      if delayHit:
        input("\nPress any key to continue")

    print(f"{winner} wins!")

#Create instance of the game logic
game = GameController(pieceIdentifiers, pieceInfo)

#Use standard 7x7 setup
if not game.setup(7, 7):
  input("Failed to create grids, exiting")
  exit(1)

while True:
  try:
    #Handle each run of the game
    game.addPlayers([computer.Player, player.Player])
    game.start(False)
    game.printRuntime()
    #Reset player ships and moves to blank grids
    game.reset()
    if input("Play again? (Y/n): ").lower() != "y":
      break
  #Catch keyboard exit to exit gracefully
  except KeyboardInterrupt:
    print("\nExiting, goodbye :)")
    exit(0)
