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
nullInterface.py (rewrite of back.Interfaces.{null,game,player}Interface from 0.6 'Ackbar')
This module contains three null interfaces for extending by other classes.
"""

class nullInterface(object):
	"""
	This is an abstract class containing the basic methods
	shared by all interfaces.
	"""
	def show_cards(self, cards, name=None, show_all=False):
		'''This method does nothing, but can be extended to show
		a player's cards.'''
		pass
		
	def show_num_cards(self, numcards, name):
		'''This method does nothing, but can be extended to show
		a the number of cards belonging to the given player.'''
		pass
		
	def write_error(self, text):
		'''This method writes the given message to the stderr.'''
		sys.stderr.write(text + "\n")
		
	#! Old function names
	showCards = show_cards
	showNumCards = show_num_cards
	writeError = write_error

class gameInterface(nullInterface):
	"""
	This is an abstract class which must be extended for
	any interface designed for the Game class.
	"""
	def show_all_cards(self, player_cards):
		'''Takes in a list of tuples of cards and player names, then
		passes these to show_cards.'''
		for cards, name in player_cards:
			self.show_cards(cards, name=name)
	
	def write(self, text):
		'''This method does nothing, but may be extended to display
		the given message.'''
		pass
		
	#! Old function names
	showAllCards = show_all_cards
		
class playerInterface(nullInterface):
	"""
	This is an abstract class which must be extended for
	any interface designed for players.
	"""
	def __init__(self, name=None):#!name should not be optional!
		self.name = name
		self.null_error = 'Warning: Interface for player %s is not correctly set up!' %name
	
	def get_move(self, cards):
		'''This method prints a warning to the screen, then causes
		the player to back out of the game.'''
		self.write_error(self.null_error)
		return -1
	
	def get_bet(self, cards, must_match):
		'''This method prints a warning to the screen, then causes
		the player to back out of the game.'''
		self.write_error(self.null_error)
		return -1
	
	def game_status(self, won, cards, credits=None):
		'''This method prints a warning to the screen, and nothing else.'''
		self.write_error(self.null_error)
		
	def shift(self, cards):
		'''This method is used during a Sabacc shift. For now,
		it simply calls show_cards.'''
		return self.show_cards(cards)
		
	#! Old function names
	getMove = get_move
	getBet = get_bet
	gameStatus = game_status
