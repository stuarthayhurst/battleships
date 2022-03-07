#!/usr/bin/python3
import random

class BaseController:
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.playerNum = playerNum
    self.isComputer = False

  def passHelpers(self, playerHelpers):
    self.playerHelpers = playerHelpers

def getFreeSpace(x, y, usedMoves):
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

def cutGrid(usedMoves):
  optimalLength = 0
  optimalTargets = []

  #Identify the largest free spaces
  for rowNum in range(0, len(usedMoves)):
    for colNum in range(0, len(usedMoves[0])):
      if usedMoves[rowNum][colNum] == "0":
        #Get number of free spaces in line with the coord
        freeLength = getFreeSpace(colNum, rowNum, usedMoves)
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
