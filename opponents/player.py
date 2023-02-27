#!/usr/bin/python3

import random
import gameHelper

class Opponent:
  def __init__(self):
    self.opponentGrid = [[0 for i in range(7)] for j in range(7)]

  def referenceToPosition(self, position):
    try:
      #Split apart grid reference
      if "," in position:
        position = position.split(",")
      else:
        position = position.split(" ")

      #Handle no commas and no spaces
      if len(position) == 1:
        if len(position[0]) >= 2:
          position = [position[0][0], position[0][1:]]

      #Covert x and y into integers
      position[0] = ord(str(position[0]).lower()) - 97
      position[1] = int(position[1]) - 1
    except:
      return False

    return position

  def makeMove(self):
    position = [None, None]
    while True:
      #Take input and attempt to parse
      position = self.referenceToPosition(input("Enter a grid reference to fire at (x, y): "))
      if not position:
        input("Invalid format")
        continue

      #Check the guess is within the board
      if position[0] < 0 or position[0] > len(self.opponentGrid) - 1:
        input("Invalid x-coordinate")
        continue
      elif position[1] < 0 or position[1] > len(self.opponentGrid) - 1:
        input("Invalid y-coordinate")
        continue

      #Check the tile is unguessed
      if self.opponentGrid[position[1]][position[0]] != 0:
        input("Location already fired at!")
        continue

      #Input valid, break the loop
      break

    #Record and return guess
    self.opponentGrid[position[1]][position[0]] = 1
    return position

  def feedbackMove(self, wasHit, didSink, destroyedShip):
    pass

  def placeShips(self):
    #TODO: Manual board placement
    #Could move the drawGrid method to gameHelper, and reuse here
    #Reuse old code as much as possible
    return gameHelper.generateBoard(7)
