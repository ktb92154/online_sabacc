#!/usr/bin/env python
# ProbabilityMatrix class version 0.1.
# Written by Joel Cross

from settings import NUM_STATES, STATEVALUE, NUM_CARDS, CARDVALUE

from ProbabilityVector import ProbabilityVector

# numerical data
from numpy import *

# Mapping for negative cards
QUEEN = 16
ENDURANCE = 17
BALANCE = 18
DEMISE = 19
MODERATION = 20
EVILONE = 21
STAR = 22

class ProbabilityMatrix (object):
	def __init__(self, template=None):
		# cards in play
		self.cards = range(NUM_CARDS) #cards = 0 ... 75
		
		# probabilities
		if template == None:
			self.matrix = None
			cardprobs = self.calculateDeck()
			self.updateMatrix(cardprobs)
		else:
			self.matrix = template.copy()
		
	def removeCard(self, card):
		if card > NUM_CARDS: # if card does not exist
			# -2 indicates that card does not exist
			return -2
		
		if card not in self.cards: # if card not in list of cards
			# -1 indicates that card has already been removed
			return -1
		
		# remove card from deck
		self.cards.remove(card)
		
		# calculate new card picking probabilities
		cardprobs = self.calculateDeck()
		
		# update the matrix with the new probabilities
		self.updateMatrix(cardprobs)
		
		return 0
		
	def calculateNextMove(self, currentmove):
		newarray = array(dot(self.matrix, currentmove.vector))
		newmove=ProbabilityVector()
		status = newmove.populateVector(newarray)
		
		return [status, newmove]

	def calculateDeck(self):
		num=[]
		prob=[]
		
		# Number of each card in play initially set to 0
		for i in range(23):
			num.append(0)
			prob.append(0.0)
		
		# get number of each card
		for card in self.cards: # for each card in play
			cardindex = CARDVALUE[card]
			
			# negative cards
			if cardindex == -2:
				cardindex = QUEEN
			elif cardindex == -8:
				cardindex = ENDURANCE
			elif cardindex == -11:
				cardindex = BALANCE
			elif cardindex == -13:
				cardindex = DEMISE
			elif cardindex == -14:
				cardindex = MODERATION
			elif cardindex == -15:
				cardindex = EVILONE
			elif cardindex == -17:
				cardindex = STAR
				
			# one more card of value
			num[cardindex] += 1
			
		# set probability of each card
		for card in range(23): # for each card type
			number = float(num[card])
			
			prob[card] = number / len(self.cards)
			
		return prob
	
	def updateMatrix(self, cardprobs):
		# empty matrix
		newmatrix = matrix(empty([NUM_STATES, NUM_STATES]))
		
		# probability of idiot's array - not exact probability
		# but this is impossible to calculate without
		# knowing exactly which cards are in play
		idiot = (((cardprobs[2] + cardprobs[3])+cardprobs[0])/3)/3
		
		for i in range(NUM_STATES): # top ... bottom
			for j in range(NUM_STATES): # left ... right
				if STATEVALUE[i] < 100 and STATEVALUE[j] < 100: # if both states are normal
					difference = STATEVALUE[i] - STATEVALUE[j]
					if 0 <= difference <= 15: # if transition to numbered card or idiot
						mod = cardprobs[difference]
					elif difference == -2:
						mod = cardprobs[QUEEN]
					elif difference == -8:
						mod = cardprobs[ENDURANCE]
					elif difference == -11:
						mod = cardprobs[BALANCE]
					elif difference == -13:
						mod = cardprobs[DEMISE]
					elif difference == -14:
						mod = cardprobs[MODERATION]
					elif difference == -15:
						mod = cardprobs[EVILONE]
					elif difference == -17:
						mod = cardprobs[STAR]
					else: # if transition impossible
						mod = 0
						
					# transitions from states 5 and 6 (values 2 and 3) to state 8
					# (value 5) slightly less likely because of idiot's array
					if i == 8 and j in [5, 6]:
						mod-=idiot
						
					# update probability
					newmatrix[i, j] = mod
				elif i == 1 and j == 1: # if transition to/from FOLD state
					# set probability to 1
					newmatrix[i, j] = 1
				elif i == 2: # if transition to OVER state
					if j == 2: # if also transition from OVER state
						# set probability to 1
						newmatrix[i, j] = 1
					else:
						# must become more likely as score increases
						current = STATEVALUE[j]
						if current < 9: # 9 minimum score for bombout on next card
							num = 0
						elif current < 100: # if normal hand
							# number of possible bomb out cards
							num = current-8
						else: # if special hand
							num = 0
						
						thisprob = 0
						
						for k in range(num): # for each possible over card
							thisprob+=cardprobs[24-current+k]

						# only numbered cards will go over
						newmatrix[i, j] = thisprob
					
				elif i == 3: # if transition to UNDER state
					if j == 3: # if also transition from UNDER state
						# set probability to 1
						newmatrix[i, j] = 1
					else:
						# must become more likely as score decreases
						current = STATEVALUE[j]
						if current > -7: # -7 maximum score for bombout on next card
							unders = []
						elif current == -7 or current == -8: # only 1 card
							unders = [STAR]
						elif current == -9: # 2 cards
							unders = [STAR, EVILONE]
						elif current == -10: # 3 cards
							unders = [STAR, EVILONE, MODERATION]
						elif current == -11 or current == -12: # 4 cards
							unders = [STAR, EVILONE, MODERATION, DEMISE]
						elif -13 >= current >= -15: # 5 cards
							unders = [STAR, EVILONE, MODERATION, DEMISE,
								BALANCE]
						elif -16 >= current >= -21: # 6 cards
							unders = [STAR, EVILONE, MODERATION, DEMISE,
								BALANCE, ENDURANCE]
						else: # if current is 22 or 23: 7 cards
							unders = [STAR, EVILONE, MODERATION, DEMISE,
								BALANCE, ENDURANCE, QUEEN]
						
						thisprob = 0
						
						for k in unders:
							thisprob += cardprobs[k]

						# only face cards will go under
						newmatrix[i, j] = thisprob
				
				elif i == 50: # if transition to IDIOT state
					if j == 5 or j==6: # if score is 2 or 3
						newmatrix[i,j] = idiot
					else: # otherwise transitions impossible
						newmatrix[i,j] = 0
				elif j == 50: # transitions from IDIOT state
					# emulate score 5
					difference = STATEVALUE[i] - 5
					if 0 <= difference <= 15: # if transition to numbered card or idiot
						mod = cardprobs[difference]
					elif difference == -2:
						mod = cardprobs[QUEEN]
					elif difference == -8:
						mod = cardprobs[ENDURANCE]
					elif difference == -11:
						mod = cardprobs[BALANCE]
					elif difference == -13:
						mod = cardprobs[DEMISE]
					elif difference == -14:
						mod = cardprobs[MODERATION]
					elif difference == -15:
						mod = cardprobs[EVILONE]
					elif difference == -17:
						mod = cardprobs[STAR]
					else: # if transition impossible
						mod = 0
					
					newmatrix[i,j] = mod
					
				else: # if cell not covered by a rule
					newmatrix[i,j] = 0
		
		self.matrix = newmatrix
		return 0
	
	def reset(self):
		self.cards = range(NUM_CARDS) #cards = 0 ... 75
		cardprobs = self.calculateDeck()
		self.updateMatrix(cardprobs)
		
		return 0
