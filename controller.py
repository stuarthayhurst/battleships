#!/usr/bin/python3

class BaseController:
  def __init__(self, pieceIdentifiers, pieceInfo, playerNum):
    self.pieceIdentifiers = pieceIdentifiers
    self.pieceInfo = pieceInfo
    self.playerNum = playerNum

  def passHelpers(self, playerHelpers):
    self.playerHelpers = playerHelpers
