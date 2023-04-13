#!/usr/bin/python3

import random
import gameHelper

class Opponent:
  def __init__(self, boardSize):
    self.boardSize = boardSize
    self.opponentGrid = [[0 for i in range(boardSize)] for j in range(boardSize)]

  def makeMove(self):
    valid = False
    while not valid:
      x, y = random.randint(0, self.boardSize - 1), random.randint(0, self.boardSize - 1)

      valid = self.opponentGrid[y][x] == 0

    self.opponentGrid[y][x] = 1
    return [x, y]

  def feedbackMove(self, wasHit, didSink, destroyedShip):
    pass

  def placeShips(self, pieceInfo):
    return gameHelper.generateBoard(self.boardSize)
