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
AgentFromXML.py (taken from version 0.6 'Ackbar')
This module contains the AgentFromXML class.
"""

# import base class
from Agent import Agent

# import settings
from settings import SABAX_VERSION, CARDVALUE

class AgentFromXML (Agent):
	"""
	This is an abstract class for every type of agent that is
	loaded from an XML file.
	"""
	def __init__(self, XMLFile, interface=None):
		self.XMLFile = XMLFile
		
		# call parent class
		Agent.__init__(self, None, interface)
		
		# Set all game statistics to 0
		self.played = self.won = self.lost = self.bombouts = self.pureSabacc = 0

	def loadFromXML(self):
		# Ensure that file exists
		if not self.XMLFile.exists():
			# -1 indicates that the file does not exist
			return -1
		
		# Ensure that file is of correct type and version
		version, agenttype = self.XMLFile.getType()
		
		if agenttype not in [1, 2]: # if type is not 'rule agent' or 'learning agent'
			if agenttype == -1: # if file is badly formatted
				# -2 indicates that the file is badly formatted
				return -2
			else: # wrong type
				# -3 indicates wrong type of agent
				return -3
		
		if version > SABAX_VERSION: # if version is incorrect
			# -4 indicates incompatible SabAX version
			return -4

		# Load game statistics
		status = [] # status list so only 1 check is required
		
		for i in ["played", "won", "lost", "bombouts", "puresabacc"]:
		# for each element
			# get element from XML file, then add status to list
			s = self.XMLFile.getElement(i)
			status.append(s)
			
		# check that everything loaded OK
		for i in range(len(status)):
			if status[i] == -2: # if file not found
				# -1 indicates file not found
				return -1
			elif status[i] == -3: # if file not parsing
				# -2 indicates that XML is badly formatted
				return -2
			elif status[i] == -1: # if element does not exist
				if i == 0: # played
					status[i] = self.played
					errorwith="Games played"
				elif i == 1: # won
					status[i] = self.won
					errorwith="Games won"
				elif i == 2: # lost
					status[i] = self.lost
					errorwith="Games lost"
				elif i == 3: # bomb out
					status[i] = self.bombouts
					errorwith="Bomb outs"
				else: # pure sabaccs
					status[i] = self.pureSabacc
					errorwith="Pure Sabaccs"
				
				errormsg = "Warning: " + errorwith +" not loaded properly." + \
				" Retaining original value."
				self.interface.writeError(errormsg)
				
		
		# update statistics
		self.name = self.XMLFile.getName()
		self.played = status[0]
		self.won = status[1]
		self.lost = status[2]
		self.bombouts = status[3]
		self.pureSabacc = status[4]
		
		return agenttype
		
	def saveToXML(self):
		# Ensure that file is of correct type and version
		version, agenttype = self.XMLFile.getType()
		
		resetfile = False # determine whether file needs resetting or not
		
		if agenttype not in [1, 2]: # if type is not 'rule agent' or 'learning agent'
			if agenttype == -2: # if file not found
				# create file
				status = self.XMLFile.createFile(self.name)
				
				# check that file wrote OK
				if status != 0:
					# -1 indicates that the file did not write properly
					return -1
				else:
					version, agenttype = self.XMLFile.getType()
				
			if agenttype == -1: # if file is badly formatted
				warning = "Warning: XML file is not parsing correctly. Resetting file:"
				resetfile = True
			elif agenttype >= 2: # wrong type
				# -3 indicates file is of wrong type
				return -3
		
		if version > SABAX_VERSION: # if XML is newer version than agent
			# -4 indicates incompatible SabAX version
			return -4
		elif version < SABAX_VERSION and version > 0: # if XML is older version than agent
			warning = "Warning: XML file is an old version (" + str(version) + "). Updating to version " + str(SABAX_VERSION) + ":"
			resetfile = True
			
		# reset file if need be
		if resetfile:
			self.interface.writeError(warning)
			if "XMLLearningAgent" in str(type(self.XMLFile)):
				newfn, status = self.XMLFile.resetFile(self.name, self.learning)
			else:
				newfn, status = self.XMLFile.resetFile(self.name)
			
			if status != 0: # if file does not exist or i/o error occurred
				# -1 indicates that file did not write properly
				return -1
			self.interface.writeError("Old file successfully saved as " + newfn + ".")
		
		# save game statistics
		status = [] # status list so only 1 check is required
		
		elemlist = [["played", self.played], ["won", self.won], ["lost", self.lost],
			["bombouts", self.bombouts], ["puresabacc", self.pureSabacc]]
		
		for i in elemlist: # for each element
			# set element in XML file, then add status to list
			s = self.XMLFile.setElement(i[0], i[1])
			status.append(s)
		
		# check that everything loaded OK
		for i in status:
			if i in [-1,-3]: # if file not found or not parsing properly
				# -1 indicates file did not write properly
				return -1
			elif i == -2: # if i/o error
				# -2 indicates i/o error occurred
				return -2
		return agenttype
		
	def gameOver(self, won, cards):
		# calculate total score
		score=0
		idiotCards = [False, False, False]
		
		for i in cards: # for each card in hand
			# add to score
			score+=CARDVALUE[i]
			
			if CARDVALUE[i] == 0:
				idiotCards[0] = True
			elif CARDVALUE[i] == 2:
				idiotCards[1] = True
			elif CARDVALUE[i] == 3:
				idiotCards[2] = True
		
		# in case of Idiot's aray
		if idiotCards == [True, True, True]:
			# set score to 23 - Pure Sabacc
			score=23
		
		# make score positive
		if score < 0:
			score = -score
		
		# bomb outs - set score to 0
		if score > 23:
			score = 0
		
		# update games played
		self.played += 1
		
		if won: # if the game was won
			# update games won
			self.won += 1
		else: # if the game was lost
			# update games lost
			self.lost += 1
			
		if score == 23: # if player has Pure Sabacc
			self.pureSabacc += 1
		elif score == 0: # if player bombed out
			self.bombouts += 1
		
		return 0
			
		
