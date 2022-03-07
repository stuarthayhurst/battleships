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

def cutGrid(usedMoves):
  #Hold start and end of each continuous space
  largestSpaces = [[], []]
  maxLength = 0
  freeLength = 0

  #Identify the largest free spaces
  for rowNum, row in enumerate(usedMoves):
    for colNum, col in enumerate(row):
      if col == "0":
        freeLength += 1
      else:
        if freeLength > maxLength:
          maxLength = freeLength
        freeLength = 0
    if freeLength > maxLength:
      maxLength = freeLength
    freeLength = 0

  for colNum in range(0, len(usedMoves[0])):
    for rowNum, row in enumerate(usedMoves):
      col = row[colNum]
      if col == "0":
        freeLength += 1
      else:
        if freeLength > maxLength:
          maxLength = freeLength
        freeLength = 0
    if freeLength > maxLength:
      maxLength = freeLength
    freeLength = 0

  #Save those free spaces
  for rowNum, row in enumerate(usedMoves):
    freeStart = [0, rowNum]
    for colNum, col in enumerate(row):
      if col == "0":
        freeLength += 1
      else:
        if freeLength == maxLength:
          largestSpaces[0].append(freeStart)
          largestSpaces[1].append([colNum - 1, rowNum])
        freeLength = 0
        freeStart = [colNum + 1, rowNum]
    if freeLength == maxLength:
      largestSpaces[0].append(freeStart)
      largestSpaces[1].append([len(row) - 1, rowNum])
    freeLength = 0

  for colNum in range(0, len(usedMoves[0])):
    freeStart = [colNum, 0]
    for rowNum, row in enumerate(usedMoves):
      col = row[colNum]
      if col == "0":
        freeLength += 1
      else:
        if freeLength == maxLength:
          largestSpaces[0].append(freeStart)
          largestSpaces[1].append([colNum, rowNum - 1])
        freeLength = 0
        freeStart = [colNum, rowNum + 1]
    if freeLength == maxLength:
      largestSpaces[0].append(freeStart)
      largestSpaces[1].append([colNum, len(usedMoves) - 1])
    freeLength = 0

  i = random.randint(0, len(largestSpaces[0]) - 1)
  target = [int((largestSpaces[0][i][0] + largestSpaces[1][i][0]) / 2), int((largestSpaces[0][i][1] + largestSpaces[1][i][1]) / 2)]

  return target
