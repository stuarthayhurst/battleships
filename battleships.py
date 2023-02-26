#!/usr/bin/python3
import os, time, sys

import player
import opponents.computer as computer
import opponents.random as randomComputer

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
  def __init__(self, pieceIdentifiers, pieceInfo):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo

  #Helper function to convert user input into valid coords
  def inputToReference(self, position, grid, verbose):
    #Split position into a separate row and column value, attempt to guess format
    if "," in position:
      position = position.split(",")
    else:
      position = position.split(" ")

    if len(position) == 1:
      if len(position[0]) >= 2:
        position = [position[0][0], position[0][1:]]

    if len(position) != 2:
      if verbose:
        input("Grid reference must be in the format 'col, row'")
      return None, None

    #Convert to expected data types
    x = str(position[0]).lower()
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
    #Print the remaining ships
    for playerNum, playerShips in enumerate(remainingShips):
      print(f" Player {playerNum + 1}'s ships:", end = "")
      for ship in playerShips:
        print(f" {self.pieceInfo[ship][0]}:{self.pieceInfo[ship][1]}", end = "")
      print()
    print()

class GameController:
  def __init__(self, pieceIdentifiers, pieceInfo):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.controllers = [0, 0]
    self.startTime = 0
    self.playerHelpers = PlayerHelpers(self.pieceIdentifiers, self.pieceInfo)

  #Return a list of blank grids (1 for each controller)
  def createGrids(self, gridWidth, gridHeight):
    if gridWidth <= 26 and gridHeight <= 26:
      return [[["0" for x in range(gridWidth)] for i in range(gridHeight)] for grid in range (2)]
    else:
      return False

  def checkWinner(self, grid):
    #Return true if all pieces are gone
    for row in grid:
      for i in row:
        if i != "0":
          return False
    return True

  def handleMove(self, controller, grid, move, delay):
    hitTile = grid[move[1]][move[0]]

    print(f"Firing at {chr(move[0] + 97).upper()}, {move[1] + 1}", end = "", flush = True)
    if delay:
      for i in range(3):
        time.sleep(0.15)
        print(".", end = "", flush = True)
      time.sleep(0.15)
      print(" ", end = "")
    else:
      print("... ", end = "")

#TODO comment

    didHit = hitTile in self.pieceIdentifiers

    grid[move[1]][move[0]] = "0"

#TODO: Use gameHelper for this

    #Return if the full ship hasn't been hit
    didSink = False
    if didHit:
      didSink = True
      for row in grid:
        if hitTile in row:
          didSink = False
          break

    destroyedShip = None
    if didSink:
      destroyedShip = hitTile

    controller.feedbackMove(didHit, didSink, destroyedShip)

    #If guess was a miss, blank that tile and return
    if not didHit:
      print("miss!")
      return

    print("hit!")

    if didSink:
      print(f"Enemy {self.pieceInfo[hitTile][0]} was sunk!")

  def printRuntime(self):
    runtimeSeconds = time.time() - self.startTime
    runtimeMinutes = int(runtimeSeconds // 60)
    runtimeSeconds = int(runtimeSeconds % 60)

    print(f"\nGame runtime: {runtimeMinutes}:{runtimeSeconds:02d}")

  def setup(self, gridWidth, gridHeight):
    #Initialise grids
    self.grids = self.createGrids(gridWidth, gridHeight) #Store player ships

    if not self.grids:
      return False
    return True

  def reset(self):
    gridWidth = len(self.grids[0][0])
    gridHeight = len(self.grids[0])
    self.grids = self.createGrids(gridWidth, gridHeight)

  def addPlayers(self, controllers):
    #Create a controller for each player
    self.controllers[0] = controllers[0]()
    self.controllers[1] = controllers[1]()

  def getShips(self, grids):
    #Find all remaining ships for both players
    ships = [[], []]
    for playerNum, grid in enumerate(grids):
      for row in grid:
        for col in row:
          if col != "0" and col not in ships[playerNum]:
            ships[playerNum].append(col)
      ships[playerNum] = sorted(ships[playerNum], key = lambda x:self.pieceInfo[x][1], reverse = True)

    return ships

  #Print the passed grid
  def drawGrid(self, grid):
    #Print a line of text with the given colour
    def printColour(text, colour):
      print(f"{colour}{text}\033[0m", end = "")

    #Print alphabetical grid references in a bar
    def printAlphaRef(grid):
      print("   ", end = "")
      for i in range(len(grid[0])):
        #Print each alphabetical grid reference
        print(chr(i + 65), end = "")
      print()

    #Print row number
    def printNumRef(rowNum):
      #Prefix a zero if single digit
      rowNum += 1
      if rowNum < 10:
        print("0", end = "")
      print(f"{rowNum} ", end = "")

    printAlphaRef(grid)

    #Iterate over grid coords
    for rowNum, row in enumerate(grid):
      printNumRef(rowNum)

      #Show each grid point
      for col in row:
        #Print hit markers in red
        if col == "X":
          printColour(col, "\033[31m")
        elif col in self.pieceIdentifiers:
          printColour(col, "\033[94m")
        else:
          print(col, end = "")

      print(" ", end = "")
      printNumRef(rowNum)
      print()

    printAlphaRef(grid)
    print()

  def start(self, delayHit):
    #Start game timer
    self.startTime = time.time()

    def convertBoard(board):
      for i in range(len(board)):
        for j in range(len(board)):
          if board[i][j] == 0:
            board[i][j] = "0"

    for i in [0, 1]:
      os.system("clear")
      self.grids[i] = self.controllers[i].placeShips()
      convertBoard(self.grids[i])

    while True:

      self.drawGrid(self.grids[1])

      #Get next move from controller, using existing moves and remaining ships
      print("player 1 move:") #TODO debug
      move = self.controllers[0].makeMove()
      #Update enemy grid and made moves grids
      self.handleMove(self.controllers[0], self.grids[1], move, delayHit)
      #If the game is over, exit
      if self.checkWinner(self.grids[1]):
        input("Winner 1") #TODO debug
        winner = "Player 1"
        break

#TODO share logic
#TODO board drawing needs to be done here

      #Wait for next player
      if delayHit:
        input("\nPress enter to continue")

      #Same as controller 1
      print("player 2 move:") #TODO debug
      move = self.controllers[1].makeMove()
      self.handleMove(self.controllers[1], self.grids[0], move, delayHit)
      if self.checkWinner(self.grids[0]):
        input("Winner 2") #TODO debug
        winner = "Player 2"
        break

      if delayHit:
        input("\nPress enter to continue")

    print(f"{winner} wins!")

#Create instance of the game logic
game = GameController(pieceIdentifiers, pieceInfo)

#Use standard 7x7 setup
if not game.setup(7, 7):
  input("Failed to create grids, exiting")
  exit(1)

#Choose the gamemode
while True:
  os.system("clear")
  print("1: Player vs player")
  print("2: Player vs computer")
  print("3: Random shots vs computer")
  try:
    gamemode = int(input("Select a gamemode (1-3): "))
    if gamemode < 1 or gamemode > 3:
      os.system("clear")
    else:
      break
  except ValueError:
    os.system("clear")

if gamemode == 1:
  players = [player.Player, player.Player]
elif gamemode == 2:
  players = [player.Player, computer.Opponent]
else:
  players = [randomComputer.Opponent, computer.Opponent]

#If '--no-delay' is passed, skip delays
delay = True
if len(sys.argv) > 1:
  if sys.argv[1] == "--no-delay":
    delay = False

while True:
  try:
    #Handle each run of the game
    game.addPlayers(players)
    game.start(delay)
    game.printRuntime()
    #Reset player ships and moves to blank grids
    game.reset()
    if input("Play again? (Y/n): ").lower() != "y":
      break
  #Catch keyboard exit to exit gracefully
  except KeyboardInterrupt:
    print("\nExiting, goodbye :)")
    exit(0)
