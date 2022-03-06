#!/usr/bin/python3
import os, random
import controller

class Player(controller.BaseController):
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    super().__init__(pieceIdentifiers, pieceInfo, playerNum)
    self.isComputer = True
    self.lastHit = [-1, -1]
    self.lastGuess = [-2, -2]
    self.lastDirection = -1

  #Helper function to clear the screen and display player number
  def resetScreen(self):
    os.system("cls||clear")
    print(f"Player {self.playerNum}: (computer)")

  def intToRef(self, coord):
    #Convert coord to alphabetical grid reference
    return chr(coord + 96)

  def placeShips(self, grid):
    #Fill the grids with ships
    for piece in self.pieceIdentifiers:
      placing = True

      print(f"Placing {self.pieceInfo[piece][0]}")

      #Keep trying to place until it succeeds
      while placing:
        flipped = bool(random.randint(0, 1))

        xCoord = self.intToRef(random.randint(1, len(grid[0])))
        position = f"{xCoord}, {random.randint(1, len(grid))}"

        #Attempt to place the piece
        if self.playerHelpers.placePiece(grid, piece, flipped, position, False):
          placing = False

  def nextMove(self, usedMoves, remainingShips):
    self.resetScreen()
    self.playerHelpers.printShips(remainingShips)
    self.playerHelpers.drawGrid(usedMoves)

#If the last hit was successful, try guessing around it in a circle
#If any of these hit, follow in the same direction
#If it reaches the end of a ship, try the other end
#If once a ship is sunk, go back to searching for ships
#If the logic gets confused, fall back to searching

#TODO (Split up large areas): When searching, try to intelligently look for ships

    done = False
    #If there's a relevant hit to guess from, use it
    if self.lastHit != [-1, -1]:
      #Guess around the last hit, following the same direction if possible
      directions = range(4)
      if self.lastDirection != -1:
        #If the last guess was actually a hit, keep going that direction
        if self.lastGuess == self.lastHit:
          directions = [self.lastDirection] + list(directions)

      for guessDirection in directions:
        #If computer is happy with the guess, finish
        if done:
          break

        movingDirection = True
        directionSwapped = False
        while movingDirection:
          #Select the next grid space in the current direction
          move = self.lastHit
          if directionSwapped:
            move = [gridX, gridY]

          if guessDirection == 0:
            gridX, gridY = move[0], move[1] - 1
          elif guessDirection == 1:
            gridX, gridY = move[0] + 1, move[1]
          elif guessDirection == 2:
            gridX, gridY = move[0], move[1] + 1
          elif guessDirection == 3:
            gridX, gridY = move[0] - 1, move[1]

          #Convert grid coords to display coords
          x = self.intToRef(gridX + 1)
          y = gridY + 1
          position = f"{x}, {y}"
          x, y = self.playerHelpers.inputToReference(position, usedMoves, False)

          #Check coords were valid
          if x == None:
            #If it was following a direction, go the other way
            if not directionSwapped and len(directions) == 5:
              print("Changing direction")
              guessDirection += 2
              guessDirection = guessDirection % 4
              directionSwapped = True
            else:
              movingDirection = False

            continue

          #Check that position hasn't already been used
          if usedMoves[gridY][gridX] != "0":
            #If they were already used, try another direction

            if directionSwapped:
              continue

            #If it was following a direction, go the other way
            if not directionSwapped and len(directions) == 5:
              print("Changing direction")
              guessDirection += 2
              guessDirection = guessDirection % 4
              directionSwapped = True
            else:
              movingDirection = False

            continue
          else:
            self.lastDirection = guessDirection
            self.lastGuess = [gridX, gridY]
            done = True
            break

    #If the computer has no relevant hit to work from, or it failed, guess randomly
    if not done:
      self.lastDirection = -1
      self.lastHit = [-1, -1]
      self.lastGuess = [-2, -2]

      #Guess randomly until a valid move is found
      while True:
        #Take input and validate position
        xCoord = self.intToRef(random.randint(1, len(usedMoves[0])))
        position = f"{xCoord}, {random.randint(1, len(usedMoves))}"
        x, y = self.playerHelpers.inputToReference(position, usedMoves, False)

        #Check coords were actually returned
        if x == None:
          continue

        #Check coords haven't already been used
        if usedMoves[y][x] != "0":
          continue

        break

    return [x, y]
