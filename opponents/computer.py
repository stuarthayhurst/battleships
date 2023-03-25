#!/usr/bin/python3

import random
import gameHelper

#Info:
# -  0 : unguessed
# - -1 : miss
# -  1 : hit
# -  2 : destroyed ship - calculated
# -  3 : destroyed ship - feedback

#TODO: update this
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

class Opponent():
  def __init__(self):
    self.opponentGrid = [[0 for i in range(7)] for j in range(7)]
    self.lastMove = [None, None]
    self.lastHit = [None, None]
    self.unsunkHits = []
    self.hitsMade = 0

    self.shipInfo = {"c": 5, "b": 4, "d": 3, "s": 3, "p": 2}
    self.remainingIdentifiers = list(self.shipInfo.keys())

#TODO: any hit streak (including single hits) that doesn't hit a sunk ship at some point can be marked as an unsunk ship

#TODO: logic to target any definitely unsunk hits
#TODO: then fix logic to follow a thread (might not need - but could be good at keep trying to hit a ship until it gets a new sunk marker)

#TODO: improve cut grid and getFreeSpace code
#TODO: - Update this logic to split a section in min turns (straddle centre), benchmark

#TODO: rewrite algorithm overview
# - Add a copy to the readme
# - In the readme, mention the performance improvements from using pypy3
# - Document each subproject


#If all ships have been hit, require guesses to aim for ships passing through an unresolved hit
#If guaranteed unsunk ships remain, boost the probability for ships passing through this (experiment with coefficient)

#TODO: - rewrite this, neaten up and move other plans to list at top of doc
# - Maths to decide if all ships have been hit, and if true then all guessed locations must be aiming for a ship intersecting a previous non-sunk hit
# - Lean more on probability distribution
# - Grid splitting should plan ahead, depending on the size of ship it's looking for

#When a ship has sunk, mark all tiles of that ship as sunk, if possible

#Attempt to identify when a ship has been hit and not sunk

  def feedbackMove(self, wasHit, didSink, destroyedShip):
    marker = -1
    if didSink:
      marker = 3
    elif wasHit:
      marker = 1

    #Update the last successful hit and known data
    if wasHit:
      self.lastHit = [self.lastMove[0], self.lastMove[1]]
    self.opponentGrid[self.lastMove[1]][self.lastMove[0]] = marker

    #Remove destroyed ship from remaining ships
    if destroyedShip != None:
      for i in range(len(self.remainingIdentifiers)):
        if self.remainingIdentifiers[i] == destroyedShip:
          self.remainingIdentifiers.pop(i)
          break

    sunkTiles = 17
    for identifier in self.remainingIdentifiers:
      sunkTiles -= self.shipInfo[identifier]

    self.hitsMade = 0
    for row in self.opponentGrid:
      for col in row:
        if col > 0:
          self.hitsMade += 1

    #If all hits are on destroyed ships, mark them as such
    if self.hitsMade == sunkTiles:
      for col in range(7):
        for row in range(7):
          if self.opponentGrid[col][row] == 1:
            self.opponentGrid[col][row] = 2

    if didSink:
      streak = False
      intersects = False
      horizStreak = 0
      streakLength = 0
      streakPos = [None, None]
      for col in range(7):
        if self.opponentGrid[self.lastMove[1]][col] == 1 or col == self.lastMove[0]:
          if not streak:
            streak = True
            streakLength = 0
            streakPos[0] = col

          if col == self.lastMove[0]:
            intersects = True
          streakLength += 1
        else:
          #Streak broken
          if intersects:
            horizStreak = streakLength
            streakPos[1] = col - 1
          intersects = False
          streakLength = 0
          streak = False
      if intersects:
        horizStreak = streakLength
        streakPos[1] = 6

      horizPos = [streakPos[0], streakPos[1]]

      streak = False
      intersects = False
      vertStreak = 0
      streakLength = 0
      streakPos = [None, None]
      for row in range(7):
        if self.opponentGrid[row][self.lastMove[0]] == 1 or row == self.lastMove[1]:
          if not streak:
            streak = True
            streakLength = 0
            streakPos[0] = row

          if row == self.lastMove[1]:
            intersects = True
          streakLength += 1
        else:
          #Streak broken
          if intersects:
            vertStreak = streakLength
            streakPos[1] = row - 1
          intersects = False
          streakLength = 0
          streak = False
      if intersects:
        vertStreak = streakLength
        streakPos[1] = 6

      vertPos = [streakPos[0], streakPos[1]]

      if vertStreak != horizStreak:
        streakDirection = "horizontal"
        if vertStreak > horizStreak:
          streakDirection = "vertical"
          finalLength = vertStreak
        else:
          finalLength = horizStreak

        if finalLength == self.shipInfo[destroyedShip]:
          if streakDirection == "horizontal":
            for col in range(horizPos[0], horizPos[1] + 1):
              self.opponentGrid[self.lastMove[1]][col] = 2
          else:
            for row in range(vertPos[0], vertPos[1] + 1):
              self.opponentGrid[row][self.lastMove[0]] = 2

      #Attempt to identify any ships sunk on their end, and mark ship as sunk from the end using their length
      lastX, lastY = self.lastMove[0], self.lastMove[1]
      clearLeft, clearRight, clearAbove, clearBelow = False, False, False, False
      unclearDirection = ""
      unclearCount = 0
      if lastX > 0:
        if self.opponentGrid[self.lastMove[1]][lastX - 1] > 0:
          unclearDirection = "left"
          unclearCount += 1

      if lastX < 6:
        if self.opponentGrid[self.lastMove[1]][lastX + 1] > 0:
          unclearDirection = "right"
          unclearCount += 1

      if lastY > 0:
        if self.opponentGrid[lastY - 1][self.lastMove[0]] > 0:
          unclearDirection = "above"
          unclearCount += 1

      if lastY < 6:
        if self.opponentGrid[lastY + 1][self.lastMove[0]] > 0:
          unclearDirection = "below"
          unclearCount += 1

      if unclearCount == 1:
        shipLength = self.shipInfo[destroyedShip]
        if unclearDirection == "left":
          for col in range((lastX + 1) - shipLength, lastX + 1):
            self.opponentGrid[lastY][col] = 2
        elif unclearDirection == "right":
          for col in range(lastX, lastX + shipLength):
            self.opponentGrid[lastY][col] = 2
        elif unclearDirection == "above":
          for row in range((lastY + 1) - shipLength, lastY + 1):
            self.opponentGrid[row][lastX] = 2
        elif unclearDirection == "below":
          for row in range(lastY, lastY + shipLength):
            self.opponentGrid[row][lastX] = 2

    #Recursively check connected hit tiles for a sunk tile
    def checkHit(grid, seenHits, position):
      if grid[position[1]][position[0]] == 3:
        return "fail"

      if position in seenHits:
        return "seen"

      if grid[position[1]][position[0]] != 1:
        return "nohit"

      seenHits.append(position)

      positions = [
        [position[0] - 1, position[1]],
        [position[0] + 1, position[1]],
        [position[0], position[1] - 1],
        [position[0], position[1] + 1]
      ]

      path = [position]
      for newPosition in positions:
        if newPosition[0] < 0 or newPosition[0] > 6:
          continue
        if newPosition[1] < 0 or newPosition[1] > 6:
          continue

        value = checkHit(grid, seenHits, newPosition)
        if value == "fail":
          return "fail"
        elif value != "nohit" and value != "seen":
          path += value

      return path

    #If a ship was sunk, remove any connected hits
    if didSink:
      safeHits = []
      for position in self.unsunkHits:
        seenHits = []
        value = checkHit(self.opponentGrid, seenHits, position)
        if value != "seen" and value != "fail" and value != "nohit":
          safeHits += value
      self.unsunkHits = safeHits

    #If last guess was a hit that didn't sink, add it to known unsunk ships
    path = []
    if wasHit and not didSink:
      path.append([self.lastMove[0], self.lastMove[1]])

    #Identify any unsunk patch of ships (when hits touch eachother, with no sunk tiles)
    for rowNum in range(len(self.opponentGrid)):
      for colNum in range(len(self.opponentGrid)):
        if self.opponentGrid[rowNum][colNum] == 1:
          seenHits = []
          value = checkHit(self.opponentGrid, seenHits, [colNum, rowNum])
          if value != "seen" and value != "fail":
            path += value
    self.unsunkHits += path

    temp = []
    for hit in self.unsunkHits:
      if hit not in temp:
        temp.append(hit)
    self.unsunkHits = temp

    #Detect when all ships except known unsunk ships are sunk
    if self.hitsMade - len(self.unsunkHits) == sunkTiles and len(self.unsunkHits) > 0:
      for rowNum in range(len(self.opponentGrid)):
        for colNum in range(len(self.opponentGrid)):
          if self.opponentGrid[rowNum][colNum] == 1:
            failed = False
            for unsunkHit in self.unsunkHits:
              if colNum == unsunkHit[0] and rowNum == unsunkHit[1]:
                failed = True
                break

            if not failed:
              self.opponentGrid[rowNum][colNum] = 2

  def makeMove(self):
    #Create grid of impossible tiles and empty grid for probabilities
    grid = self.opponentGrid
    probs = [[0 for i in range(7)] for j in range(7)]

    #Calculate smallest remaining ship
    minSize = 5
    for identifier in self.remainingIdentifiers:
      if self.shipInfo[identifier] < minSize:
        minSize = self.shipInfo[identifier]

    #If more hits have been made than 17 - smallest ship left, all remaining ships must've been hit
    mustIntersect = False
    if self.hitsMade > 17 - minSize:
      mustIntersect = True

    #If an unsunk ship is present, any ship must intersect it
    mustIntersectUnsunk = False
    if len(self.unsunkHits) != 0:
      mustIntersectUnsunk = True

    #Attempt to identify all possible locations for enemy pieces left
    for ship in self.remainingIdentifiers:
      shipLength = self.shipInfo[ship]
      reducedLength = len(grid) - (shipLength - 1)

      #Try both rotations of a ship
      for flipped in [False, True]:
        rowMax = len(grid)
        colMax = reducedLength
        if flipped:
          rowMax = reducedLength
          colMax = len(grid)

        #Iterate over every grid position
        for rowNum in range(rowMax):
          for colNum in range(colMax):
            #Check if the ship would cross a position known to contain no live ships
            failed = False
            if not flipped:
              for i in range(colNum, colNum + shipLength):
                if grid[rowNum][i] >= 2 or grid[rowNum][i] == -1:
                  failed = True
                  break
              if failed:
                continue
            else:
              for i in range(rowNum, rowNum + shipLength):
                if grid[i][colNum] >= 2 or grid[i][colNum] == -1:
                  failed = True
                  break
              if failed:
                continue

            #If an unsunk hit is present, possible ships must intersect
            boost = 1.0
            if mustIntersectUnsunk:
              passed = False
              if not flipped:
                for i in range(colNum, colNum + shipLength):
                  for unsunkHit in self.unsunkHits:
                    if unsunkHit[0] == i and unsunkHit[1] == rowNum:
                      passed = True
                      boost += 1000
                if not passed:
                  continue
              else:
                for i in range(rowNum, rowNum + shipLength):
                  for unsunkHit in self.unsunkHits:
                    if unsunkHit[0] == colNum and unsunkHit[1] == i:
                      passed = True
                      boost += 1000
                if not passed:
                  continue

            if mustIntersect:
              passed = False
              if not flipped:
                for i in range(colNum, colNum + shipLength):
                  if grid[rowNum][i] == 1:
                    passed = True
                    boost += 1000
                if not passed:
                  continue
              else:
                for i in range(rowNum, rowNum + shipLength):
                  if grid[i][colNum] == 1:
                    passed = True
                    boost += 1000
                if not passed:
                  continue

            #Increment the probability of a ship being in that tile, anywhere the ship would cross
            if not flipped:
              for i in range(colNum, colNum + shipLength):
                prob = probs[rowNum][i] + 1
                probs[rowNum][i] = prob * boost
            else:
              for i in range(rowNum, rowNum + shipLength):
                prob = probs[i][colNum] + 1
                probs[i][colNum] = prob * boost

    #If the tile has already been guessed, set the probability to 0
    for rowNum in range(len(probs)):
      for colNum in range(len(probs[0])):
        if grid[rowNum][colNum] != 0:
          probs[rowNum][colNum] = 0

    #Select the tile with the highest probability of containing a ship
    maxProb = 0
    for rowNum in range(len(probs)):
      for colNum in range(len(probs[0])):
        if probs[rowNum][colNum] > maxProb:
          maxProb = probs[rowNum][colNum]
          [x, y] = [colNum, rowNum]

    self.lastMove = [x, y]
    if self.opponentGrid[y][x] != 0:
      input("Duplicate move, something has gone wrong")
    return [x, y]

  def placeShips(self):
    return gameHelper.generateBoard(7)
