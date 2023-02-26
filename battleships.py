#!/usr/bin/python3
import os, time, sys

import player
import opponents.computer as computer
import opponents.random as randomComputer

#TODO:
# - Update player controller (+ remove old files)
# - Finish computer opponent
# - Implement neural network opponent

#Board identifiers, as well as corresponding names and ship lengths
pieceIdentifiers = ["c", "b", "d", "s", "p"]
pieceInfo = {
  "c": ["carrier", 5],
  "b": ["battleship", 4],
  "d": ["destroyer", 3],
  "s": ["submarine", 3],
  "p": ["patrol boat", 2]
}

class GameController:
  def __init__(self, pieceIdentifiers, pieceInfo, delayLength):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.delayLength = delayLength

    self.controllers = [None, None]
    self.startTime = 0

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
        if i in self.pieceIdentifiers:
          return False
    return True

  def handleMove(self, controller, grid, move):
    #Print mini firing animation
    print(f"Firing at {chr(move[0] + 97).upper()}, {move[1] + 1}", end = "", flush = True)
    for i in range(3):
      time.sleep(self.delayLength)
      print(".", end = "", flush = True)
    time.sleep(self.delayLength)
    print(" ", end = "")

    hitTile = grid[move[1]][move[0]]
    didHit = hitTile in self.pieceIdentifiers

    #Mark the hit on the visible board
    if didHit:
      grid[move[1]][move[0]] = "X"
    else:
      grid[move[1]][move[0]] = " "

    #Decide whether the whole ship has been hit
    didSink = False
    if didHit:
      didSink = True
      for row in grid:
        if hitTile in row:
          didSink = False
          break

    #Get the destroyed ship (if relevant), and feedback to controller
    destroyedShip = None
    if didSink:
      destroyedShip = hitTile
    controller.feedbackMove(didHit, didSink, destroyedShip)

    #Print the guess results
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

  #Print the passed grid
  def drawGrid(self, grid, hideShips):
    #Print a line of text with the given colour
    def getColoured(text, colour):
      return f"{colour}{text}\033[0m"

    def getRowRef(rowNum):
      #Prefix a zero if single digit
      if rowNum < 10:
        return f"0{rowNum}"
      return str(rowNum)

    #Get a string of alphabetical grid references (A -> upper bound)
    colRef = f"   {''.join([chr(i + 65) for i in range(len(grid[0]))])}"
    print(colRef)

    #Iterate over grid coords
    for rowNum, row in enumerate(grid):
      rowRef = getRowRef(rowNum + 1)
      rowBuffer = f"{rowRef} "

      #Show each grid point
      for col in row:
        #Print hit markers in red
        if col == "X":
          rowBuffer += getColoured(col, "\033[31m")
        elif col in self.pieceIdentifiers and not hideShips:
          rowBuffer += getColoured(col, "\033[94m")
        elif col == " ":
          rowBuffer += " "
        else:
          rowBuffer += "0"

      rowBuffer += f" {rowRef}"
      print(rowBuffer)

    print(colRef)

  def start(self):
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

    winner = ""
    while True:
      for i in [0, 1]:
        #Draw controller's hits
        os.system("clear")
        self.drawGrid(self.grids[1 - i], True)

        #Get next move from controller
        print(f"Player {i + 1}'s guess:")
        move = self.controllers[i].makeMove()

        #Update enemy grid and made moves grids
        self.handleMove(self.controllers[i], self.grids[1 - i], move)
        #If the game is over, exit
        if self.checkWinner(self.grids[1 - i]):
          winner = f"Player {i + 1}"
          break

        #Wait for next player
        input("\nPress enter to continue")

      if winner != "":
        break

    print(f"{winner} wins!")

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
delayLength = 0.15
if len(sys.argv) > 1:
  if sys.argv[1] == "--no-delay":
    delayLength = 0.0

#Create instance of the game logic
game = GameController(pieceIdentifiers, pieceInfo, delayLength)

#Use standard 7x7 setup
if not game.setup(7, 7):
  input("Failed to create grids, exiting")
  exit(1)

while True:
  try:
    #Handle each run of the game
    game.addPlayers(players)
    game.start()
    game.printRuntime()
    #Reset player ships and moves to blank grids
    game.reset()
    if input("Play again? (Y/n): ").lower() != "y":
      break
  #Catch keyboard exit to exit gracefully
  except KeyboardInterrupt:
    print("\nExiting, goodbye :)")
    exit(0)
