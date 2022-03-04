#!/usr/bin/python3
import os
import player

pieceIdentifiers = ["c", "b", "d", "s", "p"]
pieceInfo = {
  "c": ["carrier", 5],
  "b": ["battleship", 4],
  "d": ["destroyer", 3],
  "s": ["submarine", 3],
  "p": ["patrol boat", 2]
}

#Return a list of blank grids (1 for each controller)
def createGrids(gridWidth, gridHeight):
  if gridWidth <= 26 and gridHeight <= 26:
    return [[["0" for x in range(gridWidth)] for i in range(gridHeight)] for grid in range (2)]
  else:
    return False

#Print the passed grid, hiding any ships if specified
def drawGrid(grid, hideShips):
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
      if col not in pieceIdentifiers or hideShips == False:
        print(col, end = "")
      #Otherwise, censor any ships
      else:
        print("0", end = "")
    print()

def checkWinner(grid):
  #Return true if all pieces are gone
  for row in grid:
    for i in row:
      if i != "0":
        return False
  return True

def placeMove(grid, usedMoves, move):
  hitTile = grid[move[1]][move[0]]

  #If guess was a miss, blank that tile and return
  if hitTile not in pieceIdentifiers:
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
  print(f"Sank {pieceInfo[hitTile][0].capitalize()}")

#Initialise grids (standard 7x7)
grids = createGrids(7, 7) #Store player ships
moves = createGrids(7, 7) #Store moves made
if not grids:
  input("Failed to create grids, exiting")
  exit(1)

#Create controllers, and pass drawGrid method
controllers = [0, 0]
controllers[0] = player.Player(pieceIdentifiers, pieceInfo, drawGrid, 1)
controllers[1] = player.Player(pieceIdentifiers, pieceInfo, drawGrid, 2)

controllers[0].placeShips(grids[0])
os.system("cls||clear")
controllers[1].placeShips(grids[1])

while True:
  #Get next move from controller, using existing moves
  move = controllers[0].nextMove(moves[0])
  #Update enemy grid and made moves grids
  placeMove(grids[1], moves[0], move)

  #If the game is over, exit
  if checkWinner(grids[1]):
    winner = "Player 1"
    break

  #Clear screen for next player
  os.system("cls||clear")
  input("Press any key to continue")
  os.system("cls||clear")

  #Same as controller 1
  move = controllers[1].nextMove(moves[1])
  placeMove(grids[0], moves[1], move)
  if checkWinner(grids[0]):
    winner = "Player 2"
    break

print(f"{winner} wins!")
