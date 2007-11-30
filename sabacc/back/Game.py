#!/usr/bin/env python
# Game class
# Taken from SabaccApp version 0.5 (initial release)
# Written by Joel Cross

# Players class to deal with loading of agents
import Players

# Simple interface
from Interfaces import gameInterface

# Random class for shuffling
import random

# Import settings
from settings import MIN_PLAYERS, NUM_CARDS, POT_BUILDING_ROUNDS, IDLE_TIME, CARDVALUE

class Game (object):
	def __init__(self):
		self.players = []
		self.deck = []
		self.hands = []
		self.gameInProgress = False
		self.callable = False
		self.handPot = 0
		self.sabaccPot = 0
		self.removeNext = None
		self.idles = 0
		# set interface to default
		self.setInterface()
		
	def setInterface(self, interface=None):
		# Default interface
		if interface==None:
			interface=gameInterface()
		
		# Set interface
		self.interface=interface
		
		return 0
		
	def addPlayer(self, playername, learning=False):		
		if not self.gameInProgress: # if game is not in progress
			for x in Players.loaded: # every loaded player
				if x.name == playername: # if player found
					if not x.inPlay: # if player is not in a game
						# add player to game
						self.players.append(x)
						self.hands.append([]) # no cards in hand
						x.inPlay=True
						
						#tell player whether it is learning or not
						x.learning=learning
						
						return 0
					else: # if player is already in a game
						return -2
					break
			else: # If loop terminates without finding playername
				# -1 indicates player does not exist/not loaded
				return -1
		else: # if game is in progress
			return -3 # -3 indicates that a game is in progress
	
	def removePlayer(self, playername):
		i = 0 # counter for card resetting
		for x in self.players: # every player in the game
			if x.name == playername: # if player found
				if self.gameInProgress: # if game in progress
					# tell player that game is over
					status = x.gameOver(False, self.hands[i])
					if status != 0: # if gameOver() not successful
						# -2 indicates an unknown error with x.gameOver
						return -2
				# remove the player and his hand from the game
				x.inPlay=False
				
				# fixes bug with threading
				if x in self.players:
					self.players.remove(x)
					del self.hands[i]
				
				# if only one player left, end game
				if len(self.players) == 1:
					self.gameInProgress = False
				
				return 0
				break
			# add 1 to the counter
			i+=1
		else: # if loop terminates without finding playername
			# -1 indicates player is not in game
			return -1
		
	def startGame(self, ante=0):
		if not self.gameInProgress:
			self.logtext = []
				
			if len(self.players) >= MIN_PLAYERS:
				self.gameInProgress = True
				self.idles = 0
				# reset deck and hands
				self.deck = []
				
				for i in range(len(self.hands)):
					self.hands[i]=[]
				
				for i in range(NUM_CARDS):
					self.deck.append(i)
				
				# shuffle deck
				random.shuffle(self.deck)
				
				# Move first player to end of list
				firstPlayer = self.players[0]
				self.players.remove(firstPlayer)
				self.players.append(firstPlayer)
				
				# Collect Ante
				i=0
				while True:
					player=self.players[i]
					# player can't afford game so is kicked out
					if player.credits < ante*2:
						self.removePlayer(player.name)
						self.interface.write(player.name + " could not afford the buy into the game")
					else: # place ante into hand and sabacc pots
						player.credits -= ante*2
						self.handPot += ante
						self.sabaccPot += ante
						i+=1
					if i==len(self.players):
						break
				
				# Deal two cards to each player
				for i in range(len(self.players)):
					self.hands[i].append(self.dealCard())
					self.hands[i].append(self.dealCard())
					self.players[i].examineCards(self.hands[i])
					
					# Calculate score
					posScore = 0
					for card in self.hands[i]:
						posScore += CARDVALUE[card]
					if posScore < 0:
						posScore = -posScore
					
					if posScore > 23 or posScore == 0:
						log=3
					else:
						log=0
					
					self.logtext.append([self.players[i].name, log, posScore])
				
				
				# variables used for pot-building phase
				self.callable=False
				visible = True
				rounds=0
				
				# Repeat betting and drawing rounds until hand is called or a winner is declared
				while self.gameInProgress:
					if self.bettingRound(0) != 0: #if a player called during a betting round
						break
					if not self.gameInProgress: # if only 1 player remaining
						visible = False
						break
					if self.drawingRound() != 0: # if a player called during a drawing round
						break
					if not self.gameInProgress: # if only 1 player remaining
						visible = False
						break
					
					if rounds < POT_BUILDING_ROUNDS: # if pot-building phase in progress
						rounds += 1
					else:
						self.callable = True
				
				# Calling of hands
				endGame(visible)
				return 0
			else:
				# -1 indicates that not enough players are in the game
				return -1
		else:
			# -2 indicates that a game is already in progress
			return -2

	def bettingRound(self, starter):
		# determine order of array
		if starter == 0: # if normal order
			betPlayers = self.players
			betHands = self.hands
		else: # if abnormal order
			betPlayers = []
			betHands = []
			for i in range(len(self.players))[starter:]: # for starter and all players after starter
				# append player
				betPlayers.append(self.players[i])
				betHands.append(self.hands[i])
			for i in range(len(self.players))[:starter]: # for all players before starter
				# append player
				betPlayers.append(self.players[i])
				betHands.append(self.hands[i])
		
		mustMatch = 0 # will increase as players bet
		status = 0 # used for final return
		alreadyBet = [] # used for raising
		
		for x in betPlayers: # for each player
			# no player has bet this round
			alreadyBet.append(0)
		
		while True: # loop will repeat until all players have matched
			# used to ensure that every player bets enough
			lowestBet = mustMatch
			
			i = 0
			
			for player in betPlayers: # for each player
				name = player.name
				legalMove = False
				stillInGame = True
				
				#perform bet
				while not legalMove:
					# ask player for bet
					thisMatch = mustMatch-alreadyBet[i] # player-specific mustMatch
					
					if self.removeNext == name:
						self.removeNext = None
						bet = -1
					else:
						bet = player.bet(betHands[i], thisMatch)
					
					if bet == -1: #if player backing out of game
						legalMove = True
						self.removePlayer(name)
						self.interface.write(name + " left the game")
						
						for p in self.logtext:
							if p[0] == name:
								p[1] = 2
								break
						
						# remove player from all local lists
						del alreadyBet[i]
						
						# player may or may not still be in lists
						# depending on how list was constructed
						if player in betPlayers:
							betPlayers.remove(player)
							del betHands[i]
						
						stillInGame = False
						
					elif bet == -2 and self.callable: # if player is calling the hand
						legalMove = True
						self.interface.write(name + " called the hand")
						# Calling no longer allowed
						self.callable = False
						# 1 indicates the game has been called
						status = 1
					elif bet == thisMatch: # if player is matching
						legalMove = True
						self.handPot += bet
						if bet > 0: # if player bet more than 0, tell the user
							self.interface.write(name + " matched the bet")
							alreadyBet[i] += bet
							player.modCredits(-bet)
					elif bet > thisMatch: #if player is raising
						legalMove = True
						self.handPot += bet
						alreadyBet[i] += bet
						raisedBy = bet - thisMatch
						mustMatch = alreadyBet[i]
						self.interface.write(name + " raised the bet by " + str(raisedBy))
						player.modCredits(-bet)
				
				# add 1 to counter unless player has been removed
				if stillInGame:
					if alreadyBet[i] < lowestBet: # if bet lower than other bets
						lowestBet = alreadyBet[i]
					i+=1
				
				if not self.gameInProgress: # if only 1 player left
					break
			
			if not self.gameInProgress: # if only 1 player left
				break
			
			# if betting complete, end loop
			if lowestBet == mustMatch:
				break
			
		# status will be 0 if the game has not been called, or 1 if it has
		return status
		
		
	def drawingRound(self):
		i = 0 # counter
		
		final = 0
		
		for player in self.players: # for each player
			name = player.name
			legalMove = False
			stillInGame = True
			
			#perform move
			while not legalMove:
				if self.removeNext == name:
					self.removeNext = None
					move = -1
				elif self.idles >= IDLE_TIME and self.callable:
					# force the game to be called
					self.idles = 0
					move = 2
				else:
					# ask player for move
					move = player.move(self.hands[i])
				
				if move == -1: # if player backing out of game
					legalMove = True
					self.idles = 0
					self.removePlayer(name)
					self.interface.write(name + " left the game")
					stillInGame = False
					
					for p in self.logtext:
						if p[0] == name:
							p[1] = 2
							break
					
				elif move == 0: # if player drawing
					legalMove = True
					self.idles = 0
					self.hands[i].append(self.dealCard())
					
					# calculate player's new hand
					handTotal = 0
					for j in self.hands[i]: # for each card in the current player's hand
						handTotal += CARDVALUE[j]
					
					if handTotal < 0:
						posTotal = -handTotal
					else:
						posTotal = handTotal
					
					for p in self.logtext:
						if p[0] == name:
							p[2] = posTotal
							break
					
					if posTotal > 23: # if player bombed out
						self.interface.write(name + " bombed out")
						self.interface.showCards(self.hands[i], name)
						self.removePlayer(name)
						
						# bombing out penalty
						self.sabaccPot+=self.handPot
						player.modCredits(-self.handPot)
						
						stillInGame = False
						
						for p in self.logtext:
							if p[0] == name:
								p[1] = 3
								break
						
					else: # if player still in game
						self.interface.write(name + " drew a card")
						self.interface.showNumCards(len(self.hands[i]), name)
				elif move == 1: # if player is sticking
					legalMove = True
					self.idles += 1
				elif move == 2 and self.callable: # if player is calling the hand
					legalMove = True
					self.idles = 0
					self.callable = False
					self.interface.write(name + " called the hand")
					self.bettingRound(i) # final round of betting
					# 1 indicates the game has been called
					final = 1
			
			if final == 1: # if game has been called
				break
			
			# add 1 to counter unless player has been removed
			if stillInGame:
				# tell player the result of their move
				player.examineCards(self.hands[i])
				i += 1
			
			if not self.gameInProgress: # if only 1 player left
				break
		return final

	def dealCard(self):
		if len(self.deck) >=1: # if there are cards in the deck
			# pick first card from deck
			card = self.deck[0]
		
			# remove card from deck
			self.deck.remove(card)
		
			return card
		else: # if deck is empty
			# -1 indicates that the deck is empty
			return -1
		
	def endGame(self, visible):
		self.gameInProgress = False
		
		handValues=[] # takes form [value, numcards, idiot] for each player
		bestScore=0
		cardsToShow = []
		
		i = 0
		
		# remove any players who should have already left
		if self.removeNext != None:
			for player in self.players:
				if player.name == self.removeNext:
					self.removePlayer(player.name)
					self.removeNext = None
					self.interface.write(player.name + " left the game")
					self.interface.updatePlayers()
					
					for p in self.logtext:
						if p[0] == player.name:
							p[1] = 2
							break
					
					break
		
		for player in self.players: # for every player
			thisName=player.name
			thisHand=self.hands[i]
			if visible:
				# show player x's cards
				cardsToShow.append([thisHand, thisName])
			
			# calculate hand
			thisHand=0
			numCards=len(self.hands[i])
			idiot=False
			bomb = False
			
			for card in self.hands[i]: # each card in current hand
				thisHand += CARDVALUE[card] # add value of current card to total
			
			if thisHand > 23 or thisHand < -23 or thisHand == 0: # if player bombed out
				thisHand = 0 # set score to 0
				self.interface.write(thisName + " bombed out")
						
				# bombing out penalty
				self.sabaccPot+=self.handPot
				player.modCredits(-self.handPot)
				bomb = True
				
				for p in self.logtext:
					if p[0] == thisName:
						p[1] = 3
						break
				
			elif thisHand == 5 and len(self.hands[i]) == 3: # check for possible Idiot's array
				idiotCards=[False, False, False] # used to count number of idiot's array cards
				for card in self.hands[i]: #each card in current hand
					if CARDVALUE[card] == 0:
						idiotCards[0] = True
					elif CARDVALUE[card] == 2:
						idiotCards[1] = True
					elif CARDVALUE[card] == 3:
						idiotCards[2] = True
					
				if idiotCards == [True, True, True]: # idiot's array!
					idiot=True
					thisHand=23
			
			# add hand values to list
			handValues.append([thisHand, numCards, idiot])
			
			# make score positive
			if thisHand < 0:
				thisHand = -thisHand
			
			# rough winner estimation
			if thisHand > bestScore:
				bestScore=thisHand
				
			if bomb:
				self.interface.showCards(self.hands[i], thisName)
				self.removePlayer(thisName)
			else:
				i += 1
		
		# show all visible cards
		self.interface.showAllCards(cardsToShow)
		
		# find winner using bestScore
		winners = [] # will take the form [player number, negative, numcards] for each player
		
		for i in range(len(handValues)): # for every player
			# load appropriate values
			thisHand = handValues[i][0]
			idiot = handValues[i][2]
			
			negative=False
			numCards = handValues[i][1]

			# negative cards
			if thisHand < 0:
				negative = True
				
			# ensure idiot's array always wins
			if idiot:
				numCards = 0

			if thisHand == bestScore or thisHand == -bestScore:
				winners.append([i, negative, numCards])
		
		if len(winners) > 1: # if more than 1 winner
			# remove negative winners
			poswinners = []
			for x in winners:
				if not x[1]: # if score is positive
					poswinners.append(x)
			
			if len(poswinners) > 0: # if 1 or more positive winner
				# remove all negative winners
				winners = poswinners
			
			if len(winners) > 1: #if still more than 1 winner
				# calculate winner with least cards
				leastCards = NUM_CARDS # maximum number of cards
				leastCardsWinners = []
				
				for x in winners:
					numCards = x[2]
					# set correct value for leastCards
					if numCards < leastCards:
						leastCards = numCards
				
				# find players with least cards
				for x in winners:
					if x[2] == leastCards:
						leastCardsWinners.append(x)
				
				winners = leastCardsWinners
			
		# create new, simpler winner list
		winner=[]
		
		for x in winners:
			# append player number
			winner.append(x[0])
		
		if len(winner) >= 1:
			# calculate winnings
			winnings = self.handPot / len(winner)
		
			# remainder returns to pot
			self.handPot = self.handPot % len(winner)
		else:
			winnings = 0
		
		# if won with pure Sabacc, award Sabacc pot as well
		if bestScore == 23:
			winnings += self.sabaccPot / len(winner)
			# remainder returns to pot
			self.sabaccPot = self.sabaccPot % len(winner)
		
		# declare game outcome to all players
		# if still more than 1 winner then pot will be split
		winnertext=""
		
		for i in range(len(self.players)): # for all players
			won = False
			if i in winner: # if current player is a winner
				won = True
				# award winnings
				self.players[i].modCredits(winnings)
			
				if i == winner[0]:
					winnertext += self.players[i].name
				elif i == winner[-1]:
					winnertext += " and "+self.players[i].name
				else:
					winnertext += ", "+self.players[i].name
					
				for player in self.logtext:
					if player[0] == self.players[i].name:
						player[1] = 1
						break
			
			# tell player that game is over
			self.players[i].gameOver(won, self.hands[i])	
		
		if len(winner) > 0:
			if len(winner) == len(self.players) and len(winner) > 1:
				self.interface.write("The game was a draw.")
			else:
				self.interface.write("The game was won by "+winnertext+".")
		
		return 0
		
	def reset(self):
		if not self.gameInProgress:
			# remove all players from game
			for player in self.players:
				player.inPlay = False
			
			self.players = []
			self.hands=[]
			self.deck = []
			self.callable = False
			
			# reset pots to 0
			self.handPot=0
			self.sabaccPot=0
			
			return 0
		else:
			# -1 indicates a game is in progress
			return -1
	
	def get_callable(self):
		return self.callable
		
	def get_players(self):
		return self.players[:]
		
	def get_num_cards(self):
		numcards = []
		for hand in self.hands:
			numcards.append(len(hand))
		return numcards
		
	def get_gameInProgress(self):
		return self.gameInProgress
		
	def get_pots(self):
		return [self.handPot, self.sabaccPot]
		
	def set_removeNext(self, removeNext):
		self.removeNext = removeNext
		
	def getLog(self):
		return self.logtext

# Make object 'static'
_inst=Game()

# Public methods
setInterface=_inst.setInterface
addPlayer=_inst.addPlayer
removePlayer=_inst.removePlayer
startGame=_inst.startGame
endGame=_inst.endGame
reset=_inst.reset
bettingRound = _inst.bettingRound
drawingRound = _inst.drawingRound
dealCard = _inst.dealCard
get_callable=_inst.get_callable
get_players = _inst.get_players
get_num_cards = _inst.get_num_cards
get_gameInProgress = _inst.get_gameInProgress
get_pots = _inst.get_pots
set_removeNext = _inst.set_removeNext
getLog = _inst.getLog
