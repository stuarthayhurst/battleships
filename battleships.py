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
  for i, row in enumerate(grid):
    #Prefix a zero if single digit
    if i + 1 < 10:
      print("0", end = "")
    print(f"{i + 1} ", end = "")
    for i in row:
      #If the piece isn't a ship, or ships are being shown, show the actual piece
      if i not in pieceIdentifiers or hideShips == False:
        print(i, end = "")
      #Otherwise, censor any ships
      else:
        print("0", end = "")
    print()

#Initialise grids (standard 7x7)
grids = createGrids(7, 7)
if grids == False:
  input("Failed to create grids, exiting")
  exit(1)

#Create controllers
controllers = [0, 0]
controllers[0] = player.Player(pieceIdentifiers, pieceInfo, drawGrid)
controllers[1] = player.Player(pieceIdentifiers, pieceInfo, drawGrid)

controllers[0].placeShips(grids[0])
os.system("cls||clear")
controllers[1].placeShips(grids[1])
