#!/usr/bin/env python
# HumanAgent class
# Taken from SabaccApp version 0.5 (initial release)
# Written by Joel Cross

# import base class
from Agent import Agent

class HumanAgent (Agent):
	def move(self, cards):
		move = self.interface.getMove(cards)
		return move
		
	def bet(self, cards, mustMatch):
		bet = self.interface.getBet(cards, mustMatch)
		return bet
		
	def gameOver(self, won, cards):
		self.interface.gameStatus(won, cards, self.credits)
		return 0
