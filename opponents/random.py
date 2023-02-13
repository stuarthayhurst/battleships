#!/usr/bin/python3

import random

class Opponent:
  def __init__(self):
    self.opponentGrid = [[0 for i in range(7)] for j in range(7)]

  def makeMove(self):
    valid = False
    while not valid:
      x, y = random.randint(0, 6), random.randint(0, 6)

      valid = self.opponentGrid[y][x] == 0

    self.opponentGrid[y][x] = 1
    return [x, y]

  def feedbackMove(self, wasHit, didSink, destroyedShip):
    pass
