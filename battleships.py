#!/usr/bin/python3
import os, time
import player

pieceIdentifiers = ["c", "b", "d", "s", "p"]
pieceInfo = {
  "c": ["carrier", 5],
  "b": ["battleship", 4],
  "d": ["destroyer", 3],
  "s": ["submarine", 3],
  "p": ["patrol boat", 2]
}

class GameController:
  def __init__(self, pieceIdentifiers, pieceInfo):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.controllers = [0, 0]
    self.startTime = 0

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

  def placeMove(self, grid, usedMoves, move):
    hitTile = grid[move[1]][move[0]]

    #If guess was a miss, blank that tile and return
    if hitTile not in self.pieceIdentifiers:
      usedMoves[move[1]][move[0]] = " "
      print("Miss!")
      return

    print("Hit!")
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
    self.controllers[1] = controllers[1](self.pieceIdentifiers, self.pieceInfo, self.drawGrid, 2)

  def start(self):
    #Start game timer
    self.startTime = time.time()

    os.system("cls||clear")
    self.controllers[0].placeShips(self.grids[0])
    os.system("cls||clear")
    self.controllers[1].placeShips(self.grids[1])

    while True:
      #Get next move from controller, using existing moves
      move = self.controllers[0].nextMove(self.moves[0])
      #Update enemy grid and made moves grids
      self.placeMove(self.grids[1], self.moves[0], move)
      #If the game is over, exit
      if self.checkWinner(self.grids[1]):
        winner = "Player 1"
        break

      #Wait for next player
      input("\nPress any key to continue")

      #Same as controller 1
      move = self.controllers[1].nextMove(self.moves[1])
      self.placeMove(self.grids[0], self.moves[1], move)
      if self.checkWinner(self.grids[0]):
        winner = "Player 2"
        break

      input("\nPress any key to continue")

    print(f"{winner} wins!")

game = GameController(pieceIdentifiers, pieceInfo)

#Use standard 7x7 setup
if not game.setup(7, 7):
  input("Failed to create grids, exiting")
  exit(1)

while True:
  try:
    game.addPlayers([player.Player, player.Player])
    game.start()
    game.printRuntime()
    game.reset()
    if input("Play again? (Y/n): ").lower() != "y":
      break
  except KeyboardInterrupt:
    print("\nExiting, goodbye :)")
    exit(0)
