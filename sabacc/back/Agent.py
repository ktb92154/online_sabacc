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
Agent.py (taken from version 0.6beta1)
This module contains the Agent class.
"""

# import settings
from settings import INITIAL_CREDITS

from Interfaces import playerInterface

class Agent (object):
	"""
	This is an abstract class, which can be extended
	for different types of agent (player) in the game.
	"""
	def __init__(self, name, interface=None):
		# Set variables
		self.name = name
		self.inPlay = False
		self.learning = False
		
		if interface == None:
			interface = playerInterface()
		
		self.interface = interface
		
		self.credits=INITIAL_CREDITS
		
	def move(self, cards):
		# Abstract class - Output error, then return -1
		error = "Warning: Agent is an abstract class that is not supposed to be called directly."
		self.interface.writeError(error)
		return -1
		
	def bet(self, cards, mustMatch):
		# Abstract class - Output error, then return -1
		error = "Warning: Agent is an abstract class that is not supposed to be called directly."
		self.interface.writeError(error)
		return -1
		
	def gameOver(self, won, cards):
		# Abstract class - Output error, then return 0
		error = "Warning: Agent is an abstract class that is not supposed to be called directly."
		self.interface.writeError(error)
		return 0
		
	def modCredits(self, credits):
		# Modify credits by given amount
		self.credits+=credits
		return 0
		
	def examineCards(self, cards):
		self.interface.showCards(cards)
		return 0
		
	def shift(self, cards):
		# Performs same effect as self.examineCards for use in a
		# Sabacc Shift
		self.interface.shift(cards)
		return 0
