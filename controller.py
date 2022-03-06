#!/usr/bin/python3

class BaseController:
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.playerNum = playerNum
    self.isComputer = False

  def passHelpers(self, playerHelpers):
    self.playerHelpers = playerHelpers

#TODO this is begging for optimisation
def cutGrid(usedMoves):
  maxLength = 0
  freeLength = 0

  freeStart = [0, 0]
  largestSpaceStart = [0, 0]
  largestSpaceEnd = [len(usedMoves[0]), len(usedMoves)]

  for rowNum, row in enumerate(usedMoves):
    freeStart = [0, rowNum]
    for colNum, col in enumerate(row):
      if col == "0":
        freeLength += 1
      else:
        if freeLength > maxLength:
          largestSpaceStart = freeStart
          largestSpaceEnd = [colNum - 1, rowNum]
          maxLength = freeLength
        freeLength = 0
        freeStart = [colNum + 1, rowNum]
    if freeLength > maxLength:
      largestSpaceStart = freeStart
      largestSpaceEnd = [len(row) - 1, rowNum]
      maxLength = freeLength
    freeLength = 0

  for colNum in range(0, len(usedMoves[0])):
    freeStart = [colNum, 0]
    for rowNum, row in enumerate(usedMoves):
      col = row[colNum]
      if col == "0":
        freeLength += 1
      else:
        if freeLength > maxLength:
          largestSpaceStart = freeStart
          largestSpaceEnd = [colNum, rowNum - 1]
          maxLength = freeLength
        freeLength = 0
        freeStart = [colNum, rowNum + 1]
    if freeLength > maxLength:
      largestSpaceStart = freeStart
      largestSpaceEnd = [colNum, len(usedMoves) - 1]
      maxLength = freeLength
    freeLength = 0

  return [int((largestSpaceStart[0] + largestSpaceEnd[0]) / 2), int((largestSpaceStart[1] + largestSpaceEnd[1]) / 2)]
