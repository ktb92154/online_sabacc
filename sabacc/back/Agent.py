#!/usr/bin/env python
# Agent class
# Taken from SabaccApp version 0.5 (initial release)
# Written by Joel Cross

# import settings
from settings import INITIAL_CREDITS

from Interfaces import playerInterface

class Agent (object):
	def __init__(self, name, interface=None):
		# Set variables
		self.name = name
		self.inPlay = False
		self.learning = False
		
		if interface == None:
			interface = playerInterface()
		
		self.interface = interface
		
		self.credits=INITIAL_CREDITS
		
	def move(self, cards):
		# Abstract class - Output error, then return -1
		error = "Warning: Agent is an abstract class that is not supposed to be called directly."
		self.interface.writeError(error)
		return -1
		
	def bet(self, cards, mustMatch):
		# Abstract class - Output error, then return -1
		error = "Warning: Agent is an abstract class that is not supposed to be called directly."
		self.interface.writeError(error)
		return -1
		
	def gameOver(self, won, cards):
		# Abstract class - Output error, then return 0
		error = "Warning: Agent is an abstract class that is not supposed to be called directly."
		self.interface.writeError(error)
		return 0
		
	def modCredits(self, credits):
		# Modify credits by given amount
		self.credits+=credits
		return 0
		
	def examineCards(self, cards):
		self.interface.showCards(cards)
		return 0
		
	def shift(self, cards):
		# Performs same effect as self.examineCards for use in a
		# Sabacc Shift
		self.interface.shift(cards)
		return 0
