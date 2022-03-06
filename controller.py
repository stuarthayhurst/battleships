#!/usr/bin/python3

class BaseController:
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.playerNum = playerNum
    self.isComputer = False

  def passHelpers(self, playerHelpers):
    self.playerHelpers = playerHelpers
