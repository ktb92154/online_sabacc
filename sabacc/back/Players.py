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
Players.py (taken from version 0.6beta1)
This module contains the Players class and methods to
call it without having to instantiate it first.
"""

# import settings
from settings import SABAX_VERSION

# import XML types
from XMLAgent import XMLAgent

class Players (object):
	"""
	This class contains methods for loading and unloading
	human and XML agents from memory.
	"""
	def __init__(self):
		self.loaded = []
	
	def addHuman(self, name, interface=None):
		from HumanAgent import HumanAgent
		if not alreadyExists(name):
			agent = HumanAgent(name, interface)
			self.loaded.append(agent)
			return 0
		else:
			# -1 indicates agent name already taken
			return -1
	
	def addXML(self, filename, interface=None):
		xml = XMLAgent(filename)
		if not xml.exists(): # if XML file does not exist
			# -2 indicates that XML file does not exist
			return [-2, None]
		
		name = xml.getName()
		if alreadyExists(name): # if name already taken
			# -1 indicates agent name already taken
			return [-1, name]
		
		# get version and type from xml
		version, type = xml.getType()
		
		# check version is compatible
		if version > SABAX_VERSION:
			# -4 indicates incompatible version
			return [-4, None]
		elif version < 0: # if error
			# -3 indicates error with XML
			return [-3, None]
			
		if type < 0: # if error
			# -3 indicates error with XML
			return [-3, None]
		elif type == 1: # if type is rule based agent
			from XMLRuleAgent import XMLRuleAgent
			from RuleBasedAgent import RuleBasedAgent
			# new xml object
			xml = XMLRuleAgent(filename)
			
			# create agent object
			agent = RuleBasedAgent(xml, interface)
		else: # if type is learningAgent or other
			# -5 indicates unknown type
			return [-5, None]
		
		# load agent's details
		if agent.loadFromXML() == -2: # file badly formatted
			# -3 indicates error with XML
			return [-3, None]
		
		# add agent to list of agents
		self.loaded.append(agent)
		return [0, name]
	
	def addLoaded(self, agent):
		name = agent.name
		
		if not alreadyExists(name):
			self.loaded.append(agent)
			return 0
		else:
			# -1 indicates agent name already taken
			return -1
	
	def alreadyExists(self, name):
		for x in self.loaded: # for every loaded agent
			thisName = x.name
			if thisName == name: # if names match up
				return True
		else:
			return False

	def unload(self, name):
		for x in self.loaded:
			if x.name == name:
				self.loaded.remove(x)
				return 0
		else: # if agent not found in list
			return -1
			
# Make object 'static'
_inst=Players()

# Public methods
addHuman = _inst.addHuman
addXML = _inst.addXML
addLoaded = _inst.addLoaded
alreadyExists = _inst.alreadyExists
unload = _inst.unload

# loaded
loaded = _inst.loaded