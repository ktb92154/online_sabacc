#!/usr/bin/env python
# RuleBasedAgent class version 0.3.
# Written by Joel Cross

# import base class
from AgentFromXML import AgentFromXML

# Game class
import Game

# random action picking
import random

# import settings
from settings import CARDVALUE

class RuleBasedAgent (AgentFromXML):
	def __init__(self, XMLFile, interface=None):		
		# call parent class
		AgentFromXML.__init__(self, XMLFile, interface)
		
		# Empty rule set
		self.rules = []
		
	def move(self, cards):
		# Get value of hand
		value=0
		
		for i in cards: # for each card in hand
			# add to value
			value+=CARDVALUE[i]
		
		defaultAction = None
		validActions = []
		
		for x in self.rules: # for each defined rule
			if x.type == "default": # if rule is default rule
				# pick a default action at random from actions
				defaultAction = x.actions[random.randint(0, len(x.actions)-1)]
			else: # conditional types
				cond=[]
				# are conditions true or false?
				for y in x.conditions: # for each condition of x
					if y.function == "<": # less-than conditions
						if value < y.score:
							cond.append(True)
						else:
							cond.append(False)
					elif y.function == "=": # equals conditions
						if value == y.score:
							cond.append(True)
						else:
							cond.append(False)
					elif y.function == ">": # greater than conditions
						if value > y.score:
							cond.append(True)
						else:
							cond.append(False)
					else: # malformed conditions
						cond.append(False)
				
				if x.type == "and": # 'and' rules
					valid = True
					for i in cond: # for all conditions
						if not i: # if condition is false
							# x is not valid
							valid = False
							break
				elif x.type == "or": # 'or' rules
					valid = False
					for i in cond: # for all conditions
						if i: # if condition is true
							# x is valid
							valid = True
							break
				else: # malformed rules
					valid = False
					
				# if x is valid, add actions to list
				if valid:
					for i in x.actions: # for each action of x
						# is action already in list?
						if i not in validActions:
							validActions.append(i)
		
		# If no actions are valid, go with default. If no default then choose randomly
		if len(validActions) == 0:
			if defaultAction == None: # if no default action
				# all actions become valid
				validActions = [-1, 0, 1, 2]
			else:
				# only the default action becomes valid
				validActions = [defaultAction]
		
		# Choose an action randomly from valid actions, and return it
		action = validActions[random.randint(0, len(validActions)-1)]
		
		# If action is call but game is not callable, action becomes stick
		if action == 2 and not Game.get_callable():
			action = 1
		
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
		
		if type != 1: # if type is not 'rule based agent'
			if type < 0:  # if error occurred with parent class
				return type
			else:
				# -3 indicates wrong type of agent
				return -3
		
		# load rules
		rules, ruleStatus = self.XMLFile.getRules()
		
		# check status is OK
		if ruleStatus == -1: # if file not found
			# -1 indicates file not found
			return -1
		elif ruleStatus == -2: # if file not parsing
			# -2 indicates that XML is badly formatted
			return -2
			
		# update rules
		self.rules = rules
		
		return 0
		
	def saveToXML(self, statsonly=False):
		# call parent class
		type = AgentFromXML.saveToXML(self)
		
		if type != 1: # if type is not 'rule based agent'
			if type < 0:  # if error occurred with parent class
				return type
			else:
				# -3 indicates wrong type of agent
				return -3
		
		if statsonly:
			return 0
		
		# save rules
		ruleStatus = self.XMLFile.saveRules(self.rules)
		
		# check status is OK
		if ruleStatus in [-1, -3]: # if file not found or not parsing properly
			# -1 indicates file did not write properly
			return -1
		elif ruleStatus == -2: # if i/o error
			# -2 indicates i/o error occurred
			return -2

		
		return 0