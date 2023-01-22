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
    self.followingDirection = False
    self.directionSwapped = False

    self.impossibleTiles = [[], []]

  #Helper function to clear the screen and display player number
  def resetScreen(self):
    os.system("clear")
    print(f"Player {self.playerNum}: (computer)")

  def intToRef(self, coord):
    #Convert coord to alphabetical grid reference
    return chr(coord + 96)

  def placeShips(self, grid):
    #Create empty grid for help with AI
    self.impossibleTiles = [["0" for x in range(len(grid[0]))] for i in range(len(grid))]

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

  def getFreeSpace(self, x, y, usedMoves):
    free = True
    freeCount = 1

    #Find free space after it on the same row
    for i in range(x + 1, len(usedMoves[0])):
      tile = usedMoves[y][i]
      if tile == "0":
        freeCount += 1
      else:
        break

    #Find free space before it on the same row
    for i in range(x - 1, -1, -1):
      tile = usedMoves[y][i]
      if tile == "0":
        freeCount += 1
      else:
        break

    #Find free space after it on the same column
    for i in range(y + 1, len(usedMoves)):
      tile = usedMoves[i][x]
      if tile == "0":
        freeCount += 1
      else:
        break

    #Find free space before it on the same column
    for i in range(y - 1, -1, -1):
      tile = usedMoves[i][x]
      if tile == "0":
        freeCount += 1
      else:
        break

    return freeCount

  def cutGrid(self, usedMoves):
    optimalLength = 0
    optimalTargets = []

    #Identify the largest free spaces
    for rowNum in range(0, len(usedMoves)):
      for colNum in range(0, len(usedMoves[0])):
        if usedMoves[rowNum][colNum] == "0":
          #Get number of free spaces in line with the coord
          freeLength = self.getFreeSpace(colNum, rowNum, usedMoves)
          #If it's equivalent to the best target, remember it
          if freeLength == optimalLength:
            optimalTargets.append([colNum, rowNum])
          #If it's better than the old best target, forget all remembered coords and remember this one
          elif freeLength > optimalLength:
            optimalLength = freeLength
            optimalTargets = [[colNum, rowNum]]

    #Pick best target at random from candidates, to hide any patern that may form
    target = optimalTargets[random.randint(0, len(optimalTargets) - 1)]
    return target

  def nextMove(self, usedMoves, remainingShips):
    self.resetScreen()
    self.playerHelpers.printShips(remainingShips)
    self.playerHelpers.drawGrid(usedMoves)

#If the last hit was successful, try guessing around it in a circle
# Swap the order of locations guessed around it, to prevent players figuring out a strategy
#If any of these hit, follow in the same direction
#If it reaches the end of a ship, try the other end
#Once a ship is sunk, go back to searching for ships
#If the the AI didn't sink the ship and can't find a new location, fall back to searching (happens when shooting at 2 ships at once)

#When searching for a ship:
#When all hit tiles are accounted for with downed ships, those hits can be guaranteed to have no live ship on
#These can be made impossible, along with the hits that sank ships, and empty tiles
#Then figure out every possible ship location, using these impossible tiles as reference, and guess the tile with the highest probability of having a ship
#Use the middle of the largest continuous space of high probability as the guess

    done = False
    #If there's a relevant hit to guess from, use it
    if self.lastHit != [-1, -1]:
      #Guess around the last hit, following the same direction if possible
      if random.randint(0, 1) == 0:
        directions = range(4)
      else:
        directions = [1, 0, 3, 2]

      if self.lastDirection != -1:
        #If the last guess was actually a hit, keep going that direction
        if self.lastGuess == self.lastHit:
          self.followingDirection = True
          directions = [self.lastDirection] + list(directions)
        elif self.followingDirection:
          directions = [(self.lastDirection + 2) % 4] + list(directions)
          self.directionSwapped = True

      for guessDirection in directions:
        #If computer is happy with the guess, finish
        if done:
          break

        movingDirection = True
        directionSwapped = self.directionSwapped
        while movingDirection:
          #Select the next grid space in the current direction
          move = self.lastHit
          try:
            if directionSwapped:
              move = [gridX, gridY]
          except UnboundLocalError:
            move = self.lastHit

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
            if not directionSwapped and self.followingDirection:
              guessDirection += 2
              guessDirection = guessDirection % 4
              directionSwapped = True
            else:
              movingDirection = False

            continue

          #Check that position hasn't already been used
          if usedMoves[gridY][gridX] == "X":
            #If they were already used, try another direction
            if directionSwapped:
              continue

          #Check that position hasn't already been used
          if usedMoves[gridY][gridX] != "0":
            #If it was following a direction, go the other way
            if not directionSwapped and self.followingDirection:
              guessDirection += 2
              guessDirection = guessDirection % 4
              directionSwapped = True
            else:
              movingDirection = False

            continue
          else:
            self.lastDirection = guessDirection
            done = True
            break

    #If the last guess sank a ship, mark that no ship can be there anymore
    if self.lastHit == [-1, -1] and self.lastGuess != [-2, -2]:
      self.impossibleTiles[self.lastGuess[1]][self.lastGuess[0]] = "X"

    #If last guess was a miss, mark as impossible
    if self.lastHit != self.lastGuess:
      if self.lastHit != [-1, -1] and self.lastGuess != [-2, -2]:
        self.impossibleTiles[self.lastGuess[1]][self.lastGuess[0]] = "X"

    #If the AI made an educated guess, use it and exit
    if done:
      self.lastGuess = [x, y]
      return [x, y]

    #Reset attributes related to tracking a ship
    self.lastDirection = -1
    self.lastHit = [-1, -1]
    self.followingDirection = False
    self.directionSwapped = False
    x, y = 0, 0

    #Create grid of impossible tiles and empty grid for probabilities
    grid = self.impossibleTiles
    probs = [[0 for x in range(len(grid[0]))] for i in range(len(grid))]

    sunkTiles = 0
    for ship in self.pieceIdentifiers:
      if ship not in remainingShips[1 - self.playerNum]:
        sunkTiles += self.pieceInfo[ship][1]

    hitTiles = 0
    for row in usedMoves:
      for col in row:
        if col == "X":
          hitTiles += 1

    #If all hit tiles are accounted for with a downed ship, mark hit tiles as impossible
    if sunkTiles == hitTiles:
      for rowNum in range(len(usedMoves)):
        for colNum in range(len(usedMoves[0])):
          if usedMoves[rowNum][colNum] == "X":
            #Mark impossible tiles (2D array, Python shares it with grid, so only 1 needs updating)
            self.impossibleTiles[rowNum][colNum] = "X"

    #Attempt to identify all possible locations for enemy pieces left
    for ship in remainingShips[1 - self.playerNum]:
      #Iterate over every grid position
      for rowNum in range(len(grid)):
        for colNum in range(len(grid[0])):
          #And try the ship in both orientations
          for flipped in [False, True]:
            #Check if the ship would stay in the board
            shipLength = self.pieceInfo[ship][1]
            if not flipped:
              if colNum + shipLength > len(grid[0]):
                continue
            else:
              if rowNum + shipLength > len(grid):
                continue

            #Check if the ship would cross a position known to contain no live ships
            failed = False
            if not flipped:
              for i in range(colNum, colNum + shipLength):
                if grid[rowNum][i] == "X":
                  failed = True
                  break
              if failed:
                continue
            else:
              for i in range(rowNum, rowNum + shipLength):
                if grid[i][colNum] == "X":
                  failed = True
                  break
              if failed:
                continue

            #Increment the probability of a ship being in that tile, anywhere the ship would cross
            if not flipped:
              for i in range(colNum, colNum + shipLength):
                prob = probs[rowNum][i] + 1
                probs[rowNum][i] = prob
            else:
              for i in range(rowNum, rowNum + shipLength):
                prob = probs[i][colNum] + 1
                probs[i][colNum] = prob

    #If the tile has already been guessed, set the probability to 0
    for rowNum in range(len(probs)):
      for colNum in range(len(probs[0])):
        if usedMoves[rowNum][colNum] != "0":
          probs[rowNum][colNum] = 0

    #Find the highest probability of a ship being there
    maxProb = 0
    for row in probs:
      for prob in row:
        if prob > maxProb:
          maxProb = prob

    #Mark all high probability tiles with "X", set the rest to "0"
    for rowNum in range(len(probs)):
      for colNum in range(len(probs[0])):
        if probs[rowNum][colNum] == maxProb:
          probs[rowNum][colNum] = "0"
        else:
          probs[rowNum][colNum] = "X"

    #Guess most efficient high probability tile
    [x, y] = self.cutGrid(probs)

    self.lastGuess = [x, y]
    return [x, y]
