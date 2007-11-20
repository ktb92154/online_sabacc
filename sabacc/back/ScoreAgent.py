#!/usr/bin/env python
# ScoreAgent class version 0.1.
# Written by Joel Cross

from settings import NUM_STATES

# import base class
from RLAgent import RLAgent

class ScoreAgent (RLAgent):
	def updateLearning(self, endgame=False):
		realstate = self.state
		
		# calculate reward
		if endgame:
			if realstate in [73, 96, 97]: # winning pure sabacc or idiot's array
				reward = 5
			elif realstate in [0, 2, 3]: # bomb out
				reward = -5
			elif realstate >= NUM_STATES: # other win
				reward = 1
			else: # other loss
				reward = -1
		else: # game still in progress
			reward = 0
		
		return RLAgent.updateLearning(self, reward)
