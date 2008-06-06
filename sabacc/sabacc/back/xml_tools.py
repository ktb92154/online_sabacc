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
xml_tools.py (rewrite of back.XML{,rule}Agent from 0.6 'Ackbar')
This module contains code for dealing with Sabacc XML files.
"""

import sys

# Keeping the document here means we don't need to save unnecessarily
doc = None
agent_file = None

def create_agent(filename, agent_name, ruleset):
	'''Creates a blank agent and saves to the given filename.'''
	
	from xml.dom.ext.reader import Sax2
	from sabacc import __major_version__
	reader = Sax2.Reader()
	
	# Generate template file
	template_file = '''<?xml version='1.0' encoding='UTF-8'?>
<sabacc version='%s'>
	<agent name='%s' ruleset='%s'>
		<stats>
			<stat name='games'>0</stat>
			<stat name='wins'>0</stat>
			<stat name='losses'>0</stat>
			<stat name='bomb_outs'>0</stat>
			<stat name='pure_sabaccs'>0</stat>
		</stats>
	</agent>
</sabacc>''' %(__major_version__, agent_name, ruleset)
	global doc, agent_file
	agent_file = filename
	doc = reader.fromString(template_file)
	
	return save_file(filename)

def save_file(filename):
	'''Saves the current document to the given file.'''
	
	try:
		# Create file object for writing
		file = open(filename, 'w')
	except IOError:
		sys.stderr.write("An I/O Error occurred while attempting to write file\n'%s'\n" %filename)
		return False
		
	# Write XML to file, then close
	global doc
	from xml.dom.ext import PrettyPrint
	PrettyPrint(doc, file)
	file.close()
	return True

def get_child(parent_node, child_name):
	'''Searches the children of the specified node for one
	with the given name.'''
	from xml.dom import Node
	
	for node in parent_node.childNodes:
		if node.nodeType == Node.ELEMENT_NODE and \
		node.nodeName == child_name:
			child_node = node
			break
	else:
		child_node = None
	
	return child_node

def get_name(filename):
	'''Loads the document if necessary, then returns
	the agent's name'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(get_child(doc, 'sabacc'), 'agent')
	
	if not agent:
		sys.stderr.write("Error: No agent found in file '%s'!\n" %filename)
		return
	
	# Get 'name' attribute
	name = str(agent.getAttribute('name'))
	
	return name

def load_file(filename):
	'''Loads the XML document into memory, checking that
	it is a compatible version.'''
	
	global agent_file, doc
	
	# We don't want to load the doc if it's already loaded!
	if agent_file != filename:
		from xml.dom.ext.reader import Sax2
		reader = Sax2.Reader()
		
		try:
			# load DOM for file
			doc = reader.fromStream(filename)
		except ValueError: # if file not found
			sys.stderr.write("Error: The file '%s' was not found!\n" %filename)
			return False
		except SAXParseException: # if file not parsing correctly
			sys.stderr.write("Error: The file '%s' is not formatted correctly!\n" %filename)
			return False
		
		# Check that version is OK
		if get_child(doc, 'SabaccAppXML'):
			xml_version = 0
		else:
			sabacc = get_child(doc, 'sabacc')
			if sabacc:
				xml_version = int(sabacc.getAttribute('version'))
			else:
				sys.stderr.write("Error: The file '%s' is not a Sabacc file!\n" %filename)
				return False
		
		from settings import LOWEST_XML_VERSION
		from sabacc import __major_version__
		
		if xml_version < LOWEST_XML_VERSION or xml_version > __major_version__:
			sys.stderr.write("Error: The file '%s' was made using an\nincompatible version of Sabacc!\n" %filename)
			return False
		
	return True

def get_stats(filename):
	'''Loads the document if necessary, then returns
	the agent's statistics.'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(get_child(doc, 'sabacc'), 'agent')
	
	if not agent:
		sys.stderr.write("Error: No agent found in file '%s'!\n" %filename)
		return
	
	stats = get_child(agent, 'stats')
	
	if not stats:
		# No error needed - stats can just stay at 0
		return
	
	from xml.dom import Node
	
	# Initialise variables
	final_stats = dict(games=0, wins=0, losses=0,
		bomb_outs=0, pure_sabaccs=0)
	
	for stat in stats.childNodes:
		if stat.nodeType == Node.ELEMENT_NODE and \
		stat.nodeName == 'stat':
			stat_name = str(stat.getAttribute('name'))
			
			if final_stats.has_key(stat_name):
				try:
					stat_value = int(stat.firstChild.nodeValue)
				except ValueError: # not numeric
					stat_value = 0
				final_stats[stat_name] = stat_value
			else:
				sys.stderr.write("Warning: Unknown stat '%s' in file '%s'\n" %(stat_name, filename))
	
	return final_stats

def save_stats(filename, stats_to_save):
	'''Loads the document if necessary, then sets the agent's
	statistics to the specified values.'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(get_child(doc, 'sabacc'), 'agent')
	
	if not agent:
		sys.stderr.write("Error: No agent found in file '%s'!\n" %filename)
		return
	
	stats = get_child(agent, 'stats')
	
	if not stats:
		stats = doc.createElement('stats')
		agent.appendChild(stats)
	
	for name, value in stats_to_save.iteritems():
		# Is the stat there already?
		for stat in stats.getElementsByTagName('stat'):
			# Find correct stat
			if stat.getAttribute('name') == name:
				stat.firstChild.nodeValue = unicode(value)
				break
		else:
			# create new element and add to tree
			new_stat = doc.createElement('stat')
			new_stat.setAttribute('name', name)
			stat_value = doc.createTextNode(unicode(value))
			new_stat.appendChild(stat_value)
			stats.appendChild(new_stat)
	
	return True

def get_ruleset(filename):
	'''Loads the document if necessary, then returns
	the agent's rule set'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(get_child(doc, 'sabacc'), 'agent')
	
	if not agent:
		sys.stderr.write("Error: No agent found in file '%s'!\n" %filename)
		return
	
	# Get 'ruleset' attribute
	ruleset = str(agent.getAttribute('ruleset'))
	
	return ruleset
	
def save_ruleset(filename, ruleset):
	'''Loads the document if necessary, then sets the agent's
	rule set to the specified value.'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(get_child(doc, 'sabacc'), 'agent')
	
	if not agent:
		sys.stderr.write("Error: No agent found in file '%s'!\n" %filename)
		return
	
	agent.setAttribute('ruleset', unicode(ruleset))
	return True
