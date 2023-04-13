#!/usr/bin/python3

import sys
import gameHelper

if len(sys.argv) > 1:
  if sys.argv[1] == "random":
    import opponents.random as opponent
  elif sys.argv[1] == "computer":
    import opponents.computer as opponent
else:
  print("Opponent required [random, computer]")
  exit(1)

sampleSize = 1000
totalGuesses = 0
minGuesses = 49
for sample in range(sampleSize):
  shipMarkers = gameHelper.generateBoard(7)
  remainingShips = [[(1 if col != 0 else 0) for col in row] for row in shipMarkers]
  controller = opponent.Opponent()

  currentGuesses = 0
  currentHits = 0
  while currentHits < 17:
    guess = controller.makeMove()
    currentGuesses += 1

    didSink = False
    destroyedShip = None
    didHit = remainingShips[guess[1]][guess[0]] == 1
    if didHit:
      #Check for a destroyed ship
      identifier = shipMarkers[guess[1]][guess[0]]
      shipMarkers[guess[1]][guess[0]] = 0
      didSink = not gameHelper.searchGrid(shipMarkers, identifier)
      if didSink:
        destroyedShip = identifier

      #Mark off hit
      remainingShips[guess[1]][guess[0]] = 0
      currentHits += 1
    controller.feedbackMove(didHit, didSink, destroyedShip)

  totalGuesses += currentGuesses
  if currentGuesses < minGuesses:
    minGuesses = currentGuesses

print(f"Average guesses: {totalGuesses / sampleSize}")
print(f"Best game      : {minGuesses}")
