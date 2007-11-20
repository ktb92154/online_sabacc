#!/usr/bin/env python
# WinLossAgent class version 0.1.
# Written by Joel Cross

from settings import NUM_STATES

# import base class
from RLAgent import RLAgent

class WinLossAgent (RLAgent):
	def updateLearning(self, endgame=False):
		realstate = self.state
		
		# calculate reward
		if endgame:
			if realstate >= NUM_STATES: # win
				reward = 1
			else: # loss
				reward = -1
		else: # game still in progress
			reward = 0
		
		return RLAgent.updateLearning(self, reward)
