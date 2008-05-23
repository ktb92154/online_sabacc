# Interfaces.py from Sabacc 0.6
#! This package has been rewritten as sabacc.front.nullInterface and
#! sabacc.front.txtInterface. Please use those packages instead of this one!

from sabacc.front.nullInterface import nullInterface, gameInterface, playerInterface

#! txtInterface has been retained, as it is not compatible with new versions of the class
class txtInterface (gameInterface, playerInterface):
	"""
	This is a simple text-based interface.
	"""
	replaced_error = '''Please note: This class has been replaced by the gameInterface
	and playerInterface classes in the sabacc.front.txtInterface package.
	Please use these instead.\n'''
	def showCards(self, cards, showall=False):
		sys.stderr.write(txtInterface.replaced_error)
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
		sys.stderr.write(txtInterface.replaced_error)
		print name + " has " + str(numcards) + " cards."
	
	def write(self, text):
		sys.stderr.write(txtInterface.replaced_error)
		print text
		return 0
		
	def getMove(self, cards):
		sys.stderr.write(txtInterface.replaced_error)
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
		sys.stderr.write(txtInterface.replaced_error)
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
		sys.stderr.write(txtInterface.replaced_error)
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