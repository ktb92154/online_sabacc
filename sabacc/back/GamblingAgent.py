#!/usr/bin/env python
# GamblingAgent
# Taken from SabaccApp version 0.5 (initial release)
# Written by Joel Cross

from settings import NUM_STATES

# import base class
from RLAgent import RLAgent

class GamblingAgent (RLAgent):
	def __init__(self, XMLFile, interface=None):
		RLAgent.__init__(self, XMLFile, interface)
		self.lastcredmod = 0
		self.raised = False
	
	def updateLearning(self, endgame=False):
		# calculate reward
		if endgame:
			reward = self.lastcredmod
		else: # game still in progress
			reward = 0
		
		return RLAgent.updateLearning(self, reward)
		
	def modCredits(self, credits):
		self.lastcredmod = credits
		return RLAgent.modCredits(self, credits)
		
	def bet(self, cards, mustMatch):
		# Rudimentary betting - if winning bet 10, else match
		if self.credits < mustMatch and mustMatch != 0: # if agent can't match
			# leave game
			self.raised = False
			return -1
		elif self.credits >= mustMatch+10 and self.state >= NUM_STATES and not self.raised:
			self.raised=True
			return mustMatch + 10
		else:
			# Otherwise return minimum possible
			self.raised = False
			return mustMatch
	
	def move(self, cards):
		self.raised = False
		return RLAgent.move(self, cards)
