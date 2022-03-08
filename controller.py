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
