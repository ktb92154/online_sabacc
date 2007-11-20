#!/usr/bin/env python
# Interface classes
# Taken from SabaccApp version 0.5 (initial release)
# Written by Joel Cross

import sys

from settings import CARDNAMES, CARDVALUE

# Null Interface class. This class only displays errors.
class nullInterface(object):
	def showCards(self, cards, name):
		return 0
		
	def showNumCards(self, numcards, name):
		return 0
		
	def writeError(self, text):
		sys.stderr.write(text + "\n")
		return 0

# Null Game Interface class. This is an extension of the Null Interface class for games.
class gameInterface(nullInterface):
	def showAllCards(self, players):
		for i in players:
			cards, name = i
			status = self.showCards(cards, name)
			
			if status != 0:
				return status
		return 0
	
	def write(self, text):
		return 0
		
# Null Player Interface class. This is an extension of the Null Interface class for players.
class playerInterface(nullInterface):
	def showCards(self, cards, showall=False):
		return 0
	
	def getMove(self, cards):
		self.writeError("Warning: nullInterface and HumanAgent objects are incompatible!")
		return -1
	
	def getBet(self, cards, mustMatch):
		self.writeError("Warning: nullInterface and HumanAgent objects are incompatible!")
		return -1
	
	def gameStatus(self, won, cards, credits=None):
		self.writeError("Warning: nullInterface and HumanAgent objects are incompatible!")
		return 0

# Extended Interface class. This class prints out all information to the screen.
class txtInterface (gameInterface, playerInterface):
	def showCards(self, cards, showall=False):
		if type(showall) == str:
			name = showall
			showall = False
		else:
			name = None
		# user friendly cards array
		userCards = []
		score = 0
		
		for x in cards:
			userCards.append(CARDNAMES[x])
			score += CARDVALUE[x]
		
		if name==None:
			namehas = "You have"
		else:
			namehas = name + " has"
		
		print namehas + " cards " + str(userCards) + ". Total score = " + str(score) + "."
		return 0
	
	def showNumCards(self, numcards, name):
		print name + " has " + str(numcards) + " cards."
	
	def write(self, text):
		print text
		return 0
		
	def getMove(self, cards):
		prompt = "\n> "
		query = """Which move do you want to make?
Please choose from the following:
	-1:	Pull out of the game
	0:	Draw another card
	1:	Stick"""
		answer = None
		errorq="Sorry. That is not a valid answer. Please try again."
		
		validmoves = [-1, 0, 1]
		
		import Game
		
		if Game.get_callable():
			query +=	"\n	2:	Call the hand"
			validmoves.append(2)
		
		while answer == None:
			try:
				answer=int(raw_input(query + prompt))
			except ValueError: # if input is not numeric
				query=errorq
			
			if answer not in validmoves: # if answer is not a valid move
				query=errorq
				answer=None
		return answer

	def getBet(self, cards, mustMatch):
		prompt = "\n> "
		query = """Please enter the amount that you wish to bet.
You must bet at least """ + str(mustMatch) + """ credits.
Entering -1 will cause you to fold."""
		validmoves = [-1]
		
		import Game
		
		if Game.get_callable():
			query +=	"\nEntering -2 will call the hand."
			validmoves.append(-2)
			
		answer = None
		
		while answer == None:
			try:
				answer=int(raw_input(query+prompt))
			except ValueError: # if input is not numeric
				query="Sorry. That is not a valid answer. Please try again."
			if answer < mustMatch and answer not in validmoves: # if input is not valid
				query="You must bet at least " + str(mustMatch) + " credits. Please try again."
				answer=None
		return answer
		
	def gameStatus(self, won, cards, credits=None):
		if won: # if player won
			message="Congratulations. You have won!"
		else:
			message="Sorry. You didn't win this time."
		
		# Tell user whether won or not, then display cards
		print message
		self.showCards(cards)
		
		if credits != None:
			print "You now have " + str(credits) + " credits."
		
		return 0