# Sabacc -- an interesting card game similar to Blackjack.
# Copyright (C) 2007-2008 Joel Cross.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""
Interfaces.py (taken from version 0.6 'Ackbar')
This module contains three null interfaces and a text-based
interface for HumanAgent objects.
"""

import sys

from settings import CARDNAMES, CARDVALUE

class nullInterface(object):
	"""
	This is an abstract class containing the basic methods
	shared by all interfaces.
	"""
	def showCards(self, cards, name):
		return 0
		
	def showNumCards(self, numcards, name):
		return 0
		
	def writeError(self, text):
		sys.stderr.write(text + "\n")
		return 0

class gameInterface(nullInterface):
	"""
	This is an abstract class which must be extended for
	any interface designed for the Game class.
	"""
	def showAllCards(self, players):
		for i in players:
			cards, name = i
			status = self.showCards(cards, name)
			
			if status != 0:
				return status
		return 0
	
	def write(self, text):
		return 0
		
class playerInterface(nullInterface):
	"""
	This is an abstract class which must be extended for
	any interface designed for players.
	"""
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
		
	def shift(self, cards):
		# for use during a Sabacc shift
		return self.showCards(cards)

class txtInterface (gameInterface, playerInterface):
	"""
	This is a simple text-based interface.
	"""
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