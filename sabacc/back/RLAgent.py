#!/usr/bin/env python
# RLAgent class version 0.1.
# Written by Joel Cross

# import base class
from AgentFromXML import AgentFromXML

# probability matrix and vector
from ProbabilityMatrix import ProbabilityMatrix
from ProbabilityVector import ProbabilityVector

# random action picking
import random

# import settings
from settings import NUM_STATES, STATEVALUE, NUM_MP_STATES, CARDVALUE

# for checking opponents
import Game

DISCOUNT_RATE = 0.9 # gamma
TRACE_DECAY = 0.5 # lambda
STEP_SIZE = 0.2 # alpha
EPSILON = 0.05 # epsilon

BOMB_UPDATE = 0.01
PROB_UPDATE = 0.0125

class RLAgent (AgentFromXML):
	def __init__(self, XMLFile, interface=None):
		# call parent class
		AgentFromXML.__init__(self, XMLFile, interface)
		
		# All state values set to 0
		self.value = []
		self.visited = []
		
		for state in range(NUM_MP_STATES):
			self.visited.append(0)
			self.value.append([0.0, 0.0, 0.0])
		
		# probability matrix
		self.probmatrix = ProbabilityMatrix()
		
		# last state and action, and maximum bombout probability to draw
		self.laststate = self.lastaction = self.bombthreshold = self.probthreshold = self.eststate = None
		self.state = 0
		
	def move(self, cards):
		if self.name == None: # if XML not yet loaded
			self.interface.writeError("Warning: The file '"+str(self.XMLFile.filename)+"' is not yet loaded.")
			# -1 indicates that the agent is leaving the game
			return -1
		
		state = self.state # real state
		
		# get action from policy
		action = self.getAction(state)
		
		self.lastaction = action
		self.laststate = state
		
		return action
	
	def bet(self, cards, mustMatch):
		# Betting disabled, so return mustMatch or -1, depending on number of credits
		if self.credits < mustMatch and mustMatch != 0: # if agent can't match
			# leave game
			return -1
		else:
			# Otherwise return minimum possible
			return mustMatch
	
	def loadFromXML(self):
		# call parent class
		type = AgentFromXML.loadFromXML(self)
		
		if type != 2: # if type is not 'learning agent'
			if type < 0:  # if error occurred with parent class
				return type
			else:
				# -3 indicates wrong type of agent
				return -3
		
		type = self.XMLFile.getLearningType()
		
		status=[None, None]
		
		status[0], visited = self.XMLFile.getStateVisited()
		status[1], value = self.XMLFile.getStateValue()
			
		if -2 in status: # if file not found
			# -1 indicates file not found
			return -1
		elif status[0] < 0 or status[1] < 0: # if other error
			# -2 indicates file is badly formatted
			return -2
		
		self.visited = visited
		self.value = value
		
		bombthreshold, probthreshold = self.XMLFile.getThresholds()
		
		if bombthreshold == -2: # if file not found
			# -1 indicates file not found
			return -1
		elif bombthreshold in [-1, -3]: # if element not found or file not parsing
			# -2 indicates file is badly formatted
			return -2
			
		self.bombthreshold = bombthreshold
		self.probthreshold = probthreshold
		
		return 0
	
	def saveToXML(self, statsonly=False):
		# call parent class
		type = AgentFromXML.saveToXML(self)
		
		if type != 2: # if type is not 'learning agent'
			if type < 0:  # if error occurred with parent class
				return type
			else:
				# -3 indicates wrong type of agent
				return -3
		
		if statsonly:
			return 0
		
		# save threshold
		status = self.XMLFile.setThresholds(self.bombthreshold, self.probthreshold)
		
		# check status is OK
		if status in [-1, -3]: # if file not found or not parsing properly
			# -1 indicates file did not write properly
			return -1
		elif status == -2: # if i/o error
			# -2 indicates i/o error occurred
			return -2
		
		status=[None, None]
		status[0]=self.XMLFile.setStateVisited(self.visited)
		status[1]=self.XMLFile.setStateValue(self.value)
		
		# check status
		for i in status:
			if i in [-1, -3, -4]: # if file not found or badly formatted or state not found
				# -1 indicates file did not write properly
				return -1
			elif i == -2: # if i/o error
				# -2 indicates i/o error
				return -2
		
		return 0
	
	def gameOver(self, won, cards):
		# call parent class
		AgentFromXML.gameOver(self, won, cards)
		
		# find state
		state = self.findState(cards)
		
		# find real state
		if won:
			realstate = state + (NUM_MP_STATES-NUM_STATES)
		else:
			realstate = state
			
		self.eststate = self.state # previous estimate
		
		if self.state != realstate:
			self.visited[realstate] += 1
		
		self.state = realstate
		
		if self.learning:
			self.updateLearning(True)
			self.updateThresholds()
		
		self.laststate = self.lastaction = self.eststate = None
		self.probmatrix.reset()
		
		return 0
		
	
	def updateLearning(self, endgame=False):
		if type(endgame) == bool:
			self.interface.writeError("Error: "+str(self.name)+" has no type. Learning not updated.")
			return 0

		reward = endgame
		realstate = self.state
		
		if reward == 0:
			endgame = False
		else:
			endgame = True
		
		if self.laststate == None: # no update needed if first move
			return 0
		
		if endgame:
			# deal with previous move
			# choose next action
			nextaction = self.getAction(realstate)
		
			if nextaction == -1: # no update needed if agent is backing out
				return 0
			td_error = reward + DISCOUNT_RATE * self.value[realstate][nextaction] - \
				self.value[self.laststate][self.lastaction] # delta
			##print "td error is "+str(td_error)
		else:
			td_error = 0
		
		self.eligible[self.laststate][self.lastaction] += 1
		
		for s in range(NUM_MP_STATES): # for all states
			for a in range(3): # for all actions
				if self.eligible[s][a] != 0.0:
					if endgame:
						self.value[s][a] += STEP_SIZE * td_error * self.eligible[s][a]
					else:
						self.eligible[s][a] = DISCOUNT_RATE * TRACE_DECAY * self.eligible[s][a]
		
		return 0
	
	def examineCards(self, cards):
		AgentFromXML.examineCards(self, cards)
		
		# remove cards from matrix
		for card in cards:
			if card in self.probmatrix.cards: # if card is in the matrix
				self.probmatrix.removeCard(card)
		
		# find state
		state = self.findState(cards)
		realstate = self.calcRealState(state)
		
		if realstate < 0: # problem occurred
			if self.state != state:
				self.visited[state] += 1
			
			self.state = state
			return 0
		else:
			if self.state != realstate:
				self.visited[realstate] += 1
			self.state = realstate
	
		if self.learning:
			if self.laststate != None: # if not first move
				self.updateLearning()
		
			else: # first move and learning
				'''import os##
				os.system("clear")##
				print "Game beginning..."##'''
				
				self.eligible = []
			
				for state in range(NUM_MP_STATES):
					self.eligible.append([0,0,0])
		
		return 0
	
	def findState(self, cards):
		score = 0
		idiot = [False, False, False]
		
		for card in cards: # for each card in hand
			score += CARDVALUE[card]
			if CARDVALUE[card] == 0:
				idiot[0] = True
			elif CARDVALUE[card] == 2:
				idiot[1] = True
			elif CARDVALUE[card] == 3:
				idiot[2] = True
			
		# idiot's array
		if idiot == [True, True, True] and len(cards) == 3:
			# 50 means idiot's array
			state = 50
		elif score == 0:
			state = 0
		elif score > 23: # OVER state
			state = 2
		elif score < -23: # UNDER state
			state = 3
		elif 1 <= score <= 23: # positive states
			state = score + 3
		else: # negative states
			state = -score + 26
		
		return state
			
	def getAction(self, state):
		if self.value == []:
			self.interface.writeError("Error: Agent is not loaded!")
			return -1
		
		# find observable state
		if state >= NUM_STATES:
			obstate = state - (NUM_MP_STATES - NUM_STATES)
		else:
			obstate = state
		##print "state: "+str(state)+"\tobstate: "+str(obstate)
		
		if obstate in [2, 3]: # bomb out
			return -1
		v = ProbabilityVector(obstate)
		
		status, newprob = self.probmatrix.calculateNextMove(v)
		
		if status == -1: # if new vector is not correct size
			self.interface.writeError("Error: New ProbabilityVector is not correct size!")
			return -1
		elif status == -2: # if new vector does not sum to 1
			self.interface.writeError("Error: New ProbabilityVector does not sum to 1.0!")
			return -1
		
		rannum = random.random()
		
		if self.learning and rannum < EPSILON: # random action chosen
			# 'highest' move number, for random picking
			if Game.get_callable():
				highest = 2
			else:
				highest = 1
			bestmove=random.randint(0, highest)
			##print "EXPLORE: Move "+str(bestmove)+" chosen."
		else:
			##print "EXPLOIT: ",
			# get highest scoring move
			bestmove = 0
			
			for i in range(3)[1:]: # for each action (1, 2)
				if self.value[state][i] > self.value[state][bestmove]: # if chosen value better than current best
					bestmove = i
			##print "Move "+str(bestmove)+" chosen."
				
			if not Game.get_callable() and bestmove == 2: # if agent trying to call unsuccessfully
				##print "game not callable. changing move to 1"
				bestmove = 1
		
		if bestmove == 0: # if 'hit' chosen
			pv = newprob.vector
			
			# probability of bombing out
			bomboutprob = pv[2] + pv[3] # over+under
			
			if bomboutprob > self.bombthreshold:
				if Game.get_callable():
					if self.learning and rannum < EPSILON:
						bestmove=random.randint(1, 2)
					else:
						if self.value[state][1] > self.value[state][2]:
							bestmove = 1
						else:
							bestmove = 2
				else:
					bestmove = 1 # best to stick
				##print "likely to bomb out! changing move to "+str(bestmove)
		
		##print "taking action "+str(bestmove)+"\n"
		return bestmove
	
	def calcRealState(self, state):
		# estimate opponent scores
		opponentstates = []
		
		for i in range(len(Game.get_players())):
			player = Game.get_players()[i]
			handsize = Game.get_num_cards()[i] # no cheating - number of cards only!
			if player != self:
				probs = ProbabilityVector()
				
				for j in range(handsize):# for each card in hand
					status, probs = self.probmatrix.calculateNextMove(probs)
				
					if status == -1: # if new vector is not correct size
						self.interface.writeError("Error: New ProbabilityVector is not correct size!")
						return -1
					elif status == -2: # if new vector does not sum to 1
						self.interface.writeError("Error: New ProbabilityVector does not sum to 1.0!")
						return -1
					probs.removeTerminals()
				
				# assume opponent has an average score
				ostate = 19
				
				for j in range(len(probs.vector)):
					if probs.vector[j] > self.probthreshold and probs.vector[j] > probs.vector[ostate]:
						ostate = j
						
				opponentstates.append(ostate)
		
		# are we likely to be winning?
		for ostate in opponentstates:
			if STATEVALUE[ostate] > STATEVALUE[state] or state < 3:
				# if someone is beating us or we are in a losing state
				realstate = state
				break
		else: # if no better opponent found
			# enter 'winning' state
			realstate = state + (NUM_MP_STATES-NUM_STATES)
		
		return realstate
	
	def updateThresholds(self):
		if None in [self.bombthreshold, self.probthreshold]:
			# -1 indicates that the agent is not loaded
			return -1
		
		# bomb threshold
		if self.state in [0, 2, 3]:
			# lower the threshold by 4b
			self.bombthreshold -= (self.bombthreshold*BOMB_UPDATE)*4
		elif self.state <= 50: # if we lost
			# raise the threshold by 3b
			self.bombthreshold += (self.bombthreshold*BOMB_UPDATE)*3
			
		# probability threshold
		if self.state > 50 and self.eststate <= 50:
			# lower the threshold by 1p
			self.probthreshold -= self.probthreshold*PROB_UPDATE
		elif self.state <= 50 and self.eststate > 50:
			# raise the threshold by 10p
			self.probthreshold += (self.probthreshold*PROB_UPDATE)*10
		
		self.eststate = None
		
		'''import os##
		os.system("clear")##
		print str(self.bombthreshold)+"\t"+str(self.probthreshold)'''
		
		return 0
