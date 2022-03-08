#!/usr/bin/python3
import os, time, sys
import player
import computer
import randomComputer

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

  #Print the passed grid, hiding any ships if specified
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

  def printShips(self, remainingShips):
    #Print the reamining ships
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

  def placeMove(self, controller, grid, usedMoves, move, delay):
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

    #If guess was a miss, blank that tile and return
    if hitTile not in self.pieceIdentifiers:
      usedMoves[move[1]][move[0]] = " "
      print("miss!")
      return

    print("hit!")
    usedMoves[move[1]][move[0]] = "X"
    grid[move[1]][move[0]] = "0"

    #If the controller is a computer, let it know it hit
    if controller.isComputer:
      controller.lastHit = move

    #Return if the full ship hasn't been hit
    for row in grid:
      if hitTile in row:
        return

    #Whichever ship was hit is no longer on the grid, announce it sank
    print(f"Enemy {self.pieceInfo[hitTile][0]} was sunk!")
    if controller.isComputer:
      controller.lastHit = [-1, -1]

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
    self.controllers[0] = controllers[0](self.pieceIdentifiers, self.pieceInfo, 1)
    self.controllers[0].passHelpers(self.playerHelpers)
    self.controllers[1] = controllers[1](self.pieceIdentifiers, self.pieceInfo, 2)
    self.controllers[1].passHelpers(self.playerHelpers)

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

  def start(self, delayHit):
    #Start game timer
    self.startTime = time.time()

    os.system("cls||clear")
    self.controllers[0].placeShips(self.grids[0])
    os.system("cls||clear")
    self.controllers[1].placeShips(self.grids[1])

    while True:
      #Get next move from controller, using existing moves and remaining ships
      move = self.controllers[0].nextMove(self.moves[0], self.getShips(self.grids))
      #Update enemy grid and made moves grids
      self.placeMove(self.controllers[0], self.grids[1], self.moves[0], move, delayHit)
      #If the game is over, exit
      if self.checkWinner(self.grids[1]):
        winner = "Player 1"
        break

      #Wait for next player
      if delayHit:
        input("\nPress enter to continue")

      #Same as controller 1
      move = self.controllers[1].nextMove(self.moves[1], self.getShips(self.grids))
      self.placeMove(self.controllers[1], self.grids[0], self.moves[1], move, delayHit)
      if self.checkWinner(self.grids[0]):
        winner = "Player 2"
        break

      if delayHit:
        input("\nPress enter to continue")

    print(f"{winner} wins!")

#Extra class to patch standard game, allowing an AI to play without an opponent
class GameBenchmark(GameController):
  #Setup the board
  def __init__(self, pieceIdentifiers, pieceInfo):
    super().__init__(pieceIdentifiers, pieceInfo)
    self.setup(7, 7)
    self.guesses = 0

  #Only add one player
  def addPlayers(self, player):
    self.controllers[0] = player(self.pieceIdentifiers, self.pieceInfo, 1)
    self.controllers[0].passHelpers(self.playerHelpers)

  #Skip the opponents turn, track guesses
  def start(self):
    self.controllers[0].placeShips(self.grids[0])

    while True:
      self.guesses += 1
      #Get next move from controller, using existing moves and remaining ships
      move = self.controllers[0].nextMove(self.moves[0], self.getShips(self.grids))
      #Update ship grid and made moves grids
      self.placeMove(self.controllers[0], self.grids[0], self.moves[0], move, False)
      #If the game is over, exit
      if self.checkWinner(self.grids[0]):
        break

    return self.guesses

#If benchmarking, use a patched game and exit early
if len(sys.argv) > 1:
  if sys.argv[1] == "--benchmark":
    #Setup modified game
    game = GameBenchmark(pieceIdentifiers, pieceInfo)
    try:
      runCount = int(sys.argv[2])
    except:
      print("Number of games to run is required")
      exit(1)

    threshold = 38
    totalGuesses = 0
    fails = 0

    #Run specified number of games
    for i in range(runCount):
      game.addPlayers(computer.Player)
      totalGuesses += game.start()
      game.reset()
      if game.guesses >= threshold:
        fails += 1
      game.guesses = 0

    #Print AI performance data and exit
    failPercent = round(((fails / runCount) * 100), 1)
    print(f"Average attempts: {totalGuesses / runCount}")
    print(f"{fails} games took more than {threshold} attempts ({failPercent}%)")
    exit()

#Create instance of the game logic
game = GameController(pieceIdentifiers, pieceInfo)

#Use standard 7x7 setup
if not game.setup(7, 7):
  input("Failed to create grids, exiting")
  exit(1)

#Choose the gamemode
while True:
  os.system("cls || clear")
  print("1: Player vs player")
  print("2: Player vs computer")
  print("3: Random shots vs computer")
  try:
    gamemode = int(input("Select a gamemode (1-3): "))
    if gamemode < 1 or gamemode > 3:
      os.system("cls || clear")
    else:
      break
  except ValueError:
    os.system("cls || clear")

if gamemode == 1:
  players = [player.Player, player.Player]
elif gamemode == 2:
  players = [player.Player, computer.Player]
else:
  players = [randomComputer.Player, computer.Player]

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
