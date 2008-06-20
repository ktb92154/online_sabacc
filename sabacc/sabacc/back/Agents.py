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
Agents.py (rewrite of back.{,Human,RuleBased}Agent{,FromXML} from 0.6 'Ackbar')
This module contains code for all the agent and XML related objects.
"""

import sys

class HumanAgent (object):
	"""
	This is a dummy class whose methods all point
	to various methods in its interface.
	"""
	
	def __init__(self, name, interface=None):
		self.name = name
		
		if interface == None:
			from sabacc.front.nullInterface import playerInterface
			interface = playerInterface(name)
		
		self.interface = interface
		self.quit_next_turn = False # player will leave game at next opportunity
		
		from back.settings import INITIAL_CREDITS #!
		self.credits=INITIAL_CREDITS
		
	def move(self, cards):
		'''Gets a move from the player and returns it.'''
		
		if self.quit_next_turn:
			from settings import moves
			move = moves['fold']
		else:
			move = self.interface.get_move(cards)
			
		return move
		
	def bet(self, cards, must_match):
		'''Gets a bet from the player and returns it.'''
		if self.quit_next_turn:
			from settings import moves
			bet = moves['fold']
		else:
			bet = self.interface.get_bet(cards, must_match)
			
		return bet
		
	def game_over(self, won, cards):
		'''Informs the user that the game is over and the result.'''
		
		if not self.quit_next_turn:
			self.interface.game_status(won, cards, self.credits)
		
	def examine_cards(self, cards):
		'''Shows the player his cards'''
		
		if not self.quit_next_turn:
			self.interface.show_cards(cards)
		
	def shift(self, cards):
		'''Shows the player his correct details after a Sabacc shift'''
		
		if not self.quit_next_turn:
			self.interface.shift(cards)

class RuleBasedAgent (HumanAgent):
	"""
	This class contains methods for deciding how a rule-based
	agent will act in a given situation.
	"""
	def __init__(self, filename, interface=None):
		self.filename = filename
		self.loaded = False
		
		# Initialise attributes
		HumanAgent.__init__(self, None, interface)
		self.stats = dict(games=0, wins=0, losses=0, bomb_outs=0, pure_sabaccs=0)
		
		self.raised = False
		self.ruleset = None
		
		if self.load_from_xml():
			self.loaded = True
		
	def load_from_xml(self):
		'''Loads name, statistics and ruleset from XML file.'''
		
		from os.path import exists
		import xml_tools
		
		if not exists(self.filename):
			self.interface.write_error('Error: The file %s could not be found!' %self.filename)
			return False

		# Load game statistics
		name = xml_tools.get_name(self.filename)
		stats = xml_tools.get_stats(self.filename)
		
		if name and stats:
			self.name = name
			self.stats = stats
		else:
			self.interface.write_error('Error loading data from XML!')
			return False
		
		# Load rule set
		ruleset = xml_tools.get_ruleset(self.filename)
		
		if not ruleset:
			return False
		else:
			self.ruleset = ruleset
			
		return True
		
	def save_to_xml(self, stats=False):
		'''Saves statistics and ruleset (if modified) to the XML file.'''
		
		import xml_tools
		
		if stats:
			# save game statistics
			if not xml_tools.save_stats(self.filename, self.stats):
				return False
		
		else:
			# save rule set
			if not xml_tools.save_ruleset(self.filename, self.ruleset):
				return False
		
		# Actually save changes to XML file
		if not xml_tools.save_file(self.filename):
			return False
		
		return True
	
	def move(self, cards):
		'''Uses ruleset to decide what move to make and returns it.
		If there is an error, the move will always be 'fold'.'''
		
		if self.quit_next_turn:
			from settings import moves
			return moves['fold']
		
		self.raised = False
		from back.settings import CARDVALUE#!
		
		# Get value of hand
		score = 0
		
		for card in cards:
			score += CARDVALUE[card]
		
		from settings import rule_sets, moves
		
		if rule_sets.has_key(self.ruleset):
			threshold = rule_sets[self.ruleset]
		else:
			self.interface.write_error("Error: '%s' is not a valid rule set!" %self.ruleset)
			return moves['fold']
		
		from Game import callable
		
		# Main drawing cards rule - only if score is between thresholds
		if score > threshold['lower'] and score < threshold['upper']:
			action = moves['draw']
		
		# Call on a Pure Sabacc if you can!
		elif score in (23,-23) and callable:
			action = moves['move_call']
		
		# Our score is so bad we might as well give up hope!
		elif score > 30 or score < -30:
			action = moves['stick']
		
		# We're out, but we might be able to get back in...
		elif score >= 24 or score <= -24:
			action = moves['draw']
		
		# default action for when the others don't apply
		else:
			if callable:
				# Do we call this turn? Let's use the power of random to find out...
				from random import choice
				action = choice((moves['stick'], moves['move_call']))
			else:
				action = moves['stick']
		
		return action
	
	def bet(self, cards, must_match):
		'''Calculates the bet based on  the value of the hand.'''
		
		if self.quit_next_turn:
			from settings import moves
			return moves['fold']
		
		from back.settings import CARDVALUE#!
		
		# Get value of hand
		score = 0
		
		for card in cards:
			score += CARDVALUE[card]
		
		# Make sure score is positive
		if score < 0:
			score = -score
		
		# Simple betting. Does not lie.
		# Either pure sabacc, good, average, bad or out
		score_types = dict(sabacc=0, good=1, average=2, bad=3, out=4)
		
		if score == 23:
			score_type = score_types['sabacc']
		elif 18 <= score <= 22:
			score_type = score_types['good']
		elif 10 <= score <= 17:
			score_type = score_types['average']
		elif score <= 9 or score in (24, 25):
			score_type = score_types['bad']
		else:
			score_type = score_types['out']
		
		from random import randint
		from back.settings import MIN_BET, MAX_BET#!
		from settings import moves
		
		if score_type in (score_types['sabacc'], score_types['good']):
			if not self.raised:
				bet = randint(MIN_BET, MAX_BET)
				if score_type == score_types['sabacc']:
					bet *= 5
			else:
				bet = 0
		
		elif score_type == score_types['average']:
			# Bet 1/3 of the time
			if not self.raised and randint(0,2) == 1:
				bet = randint(MIN_BET, MAX_BET)
			else:
				bet = 0
		elif score_type == score_types['bad']:
			bet = 0
			
		else: # player is out
			if must_match == 0:
				bet = 0
			else:
				bet = moves['fold']
		
		## Betting more than another player can afford shouldn't be allowed!!
		# Calculate final
		if self.credits < must_match and must_match != 0: # if agent can't match
			# leave game
			final = moves['fold']
		elif bet == moves['fold']:
			final = bet
		else:
			final = bet + must_match
		
		# Don't bet more than you have!
		if final > self.credits:
			final = self.credits
		
		# Have we raised?
		if final > must_match:
			self.raised = True
			
		return final
	
	def game_over(self, won, cards):
		'''Updates the player's statistics depending
		on the outsome of the game,'''
		
		from back.settings import CARDVALUE#!
		
		# Get value of hand
		score = 0
		idiot_cards = [False, False, False]
		
		for card in cards:
			score += CARDVALUE[card]
			
			if len(cards) == 3:
				if CARDVALUE[card] == 0:
					idiot_cards[0] = True
				elif CARDVALUE[card] == 2:
					idiot_cards[1] = True
				elif CARDVALUE[card] == 3:
					idiot_cards[2] = True
		
		# in case of Idiot's aray
		if idiot_cards == [True, True, True]:
			# set score to 23 - Pure Sabacc
			score = 23
		
		# make score positive
		if score < 0:
			score = -score
		
		# bomb outs - set score to 0
		if score > 23:
			score = 0
		
		# update statistics
		self.stats['games'] += 1
		
		if won:
			self.stats['wins'] += 1
		else:
			self.stats['losses'] += 1
			
		if score == 23:
			self.stats['pure_sabaccs'] += 1
		elif score == 0:
			self.stats['bomb_outs'] += 1
