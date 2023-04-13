#!/usr/bin/python3

import os, random
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

  def placeShips(self, pieceInfo):
    userBoard = [[0 for i in range(7)] for j in range(7)]

    remainingShips = list(pieceInfo.keys())

    for piece in remainingShips:
      flipped = False
      while True:
        os.system("clear")
        gameHelper.drawGrid(userBoard, False, ["c", "b", "d", "s", "p"])

        #Display ship to place
        print(f"\nPlacing {pieceInfo[piece][0]}:")
        if not flipped:
          print(piece * pieceInfo[piece][1])
        else:
          for i in range(pieceInfo[piece][1]):
            print(piece)
        print()

        action = input("Enter r to rotate the piece, or a grid reference (x, y): ")
        if action == "f" or action == "r":
          flipped = not flipped
        else:
          #Parse input reference
          position = self.referenceToPosition(action)

          #Check the guess is within the board
          if position[0] < 0 or position[0] > len(userBoard) - 1:
            input("Invalid x-coordinate")
            continue
          elif position[1] < 0 or position[1] > len(userBoard) - 1:
            input("Invalid y-coordinate")
            continue

          #Check ship would fit in the board
          length = pieceInfo[piece][1]
          maxIndex = len(userBoard) - length
          if not flipped:
            if position[0] > maxIndex:
              input("Invalid location, the ship won't fit here")
              continue
          else:
            if position[1] > maxIndex:
              input("Invalid location, the ship won't fit here")
              continue

          #Attempt to place the piece
          if gameHelper.placePiece(userBoard, piece, length, position[0], position[1], flipped):
            break
          else:
            input("Invalid location, the ship would collide with another")

    return userBoard
