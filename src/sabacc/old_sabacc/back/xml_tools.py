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
xml_tools.py (taken from Sabacc version 1.0-beta1)
This module contains code for dealing with Sabacc XML files.
"""

import sys
import gettext; _=gettext.gettext # gettext for translations

# Keeping the document here means we don't need to save unnecessarily
doc = None
agent_file = None

def create_agent(filename, agent_name, ruleset):
	'''Creates a blank agent and saves to the given filename.'''
	
	from lxml import etree
	from old_sabacc import __major_version__
	
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
	doc = etree.fromstring(template_file)
	
	return save_file(filename)

def save_file(filename):
	'''Saves the current document to the given file.'''
	
	try:
		# Create file object for writing
		file = open(filename, 'w')
	except IOError:
		sys.stderr.write(_("An I/O Error occurred while attempting to write file\n'%s'\n") %filename)
		return False
		
	# Write XML to file, then close
	global doc
	from lxml import etree
	doc_str = etree.tostring(doc, pretty_print=True)
	file.write(doc_str)
	file.close()
	return True

def get_child(parent_node, child_name):
	'''Searches the children of the specified node for one
	with the given name.'''
	
	for node in parent_node.getchildren():
		if node.tag == child_name:
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
	agent = get_child(doc, 'agent')
	
	if agent is None:
		sys.stderr.write(_("Error: No agent found in file '%s'!\n") %filename)
		return
	
	# Get 'name' attribute
	name = str(agent.get('name'))
	
	return name

def load_file(filename):
	'''Loads the XML document into memory, checking that
	it is a compatible version.'''
	
	global agent_file, doc
	
	# We don't want to load the doc if it's already loaded!
	if agent_file != filename:
		from lxml import etree
		
		try:
			# load DOM for file
			tree = etree.parse(filename)
		except IOError: # if file not found
			sys.stderr.write(_("Error: The file '%s' was not found!\n") %filename)
			return False
		except etree.XMLSyntaxError: # if file not parsing correctly
			sys.stderr.write(_("Error: The file '%s' is not formatted correctly!\n") %filename)
			return False
		
		doc = tree.getroot()
		agent_file = filename
		
		# Check that version is OK
		if doc.tag == 'SabaccAppXML':
			xml_version = 0
		elif doc.tag == 'sabacc':
			xml_version = int(doc.get('version'))
		else:
			sys.stderr.write(_("Error: The file '%s' is not a Sabacc file!\n") %filename)
			return False
		
		from old_sabacc.constants import lowest_xml_version
		from old_sabacc import __major_version__
		
		if xml_version < lowest_xml_version or xml_version > __major_version__:
			sys.stderr.write(_("Error: The file '%s' was made using an\nincompatible version of Sabacc!\n") %filename)
			return False
		
	return True

def get_stats(filename):
	'''Loads the document if necessary, then returns
	the agent's statistics.'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(doc, 'agent')
	
	if agent is None:
		sys.stderr.write(_("Error: No agent found in file '%s'!\n") %filename)
		return
	
	stats = get_child(agent, 'stats')
	
	if stats is None:
		# No error needed - stats can just stay at 0
		return
	
	# Initialise variables
	final_stats = dict(games=0, wins=0, losses=0,
		bomb_outs=0, pure_sabaccs=0)
	
	for stat in stats.getchildren():
		if stat.tag == 'stat':
			stat_name = str(stat.get('name'))
			
			if final_stats.has_key(stat_name):
				try:
					stat_value = int(stat.text)
				except ValueError: # not numeric
					stat_value = 0
				final_stats[stat_name] = stat_value
			else:
				sys.stderr.write(_("Warning: Unknown stat '%s' in file '%s'\n") %(stat_name, filename))
	
	return final_stats

def save_stats(filename, stats_to_save):
	'''Loads the document if necessary, then sets the agent's
	statistics to the specified values.'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(doc, 'agent')
	
	if agent is None:
		sys.stderr.write(_("Error: No agent found in file '%s'!\n") %filename)
		return
	
	stats = get_child(agent, 'stats')
	
	if stats is None:
		from lxml import etree
		stats = etree.SubElement(agent, 'stats')
	
	for name, value in stats_to_save.iteritems():
		# Is the stat there already?
		for stat in stats:
			# Find correct stat
			if stat.tag == 'stat' and stat.get('name') == name:
				stat.text = unicode(value)
				break
		else:
			# create new element and add to tree
			from lxml import etree
			new_stat = etree.SubElement(stats, 'stat')
			new_stat.set('name', name)
			new_stat.text = unicode(value)
	
	return True

def get_ruleset(filename):
	'''Loads the document if necessary, then returns
	the agent's rule set'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(doc, 'agent')
	
	if agent is None:
		sys.stderr.write(_("Error: No agent found in file '%s'!\n") %filename)
		return
	
	# Get 'ruleset' attribute
	ruleset = str(agent.get('ruleset'))
	
	return ruleset
	
def save_ruleset(filename, ruleset):
	'''Loads the document if necessary, then sets the agent's
	rule set to the specified value.'''
	
	if not load_file(filename):
		return
	
	# Get 'agent' element
	agent = get_child(doc, 'agent')
	
	if agent is None:
		sys.stderr.write(_("Error: No agent found in file '%s'!\n") %filename)
		return
	
	agent.set('ruleset', unicode(ruleset))
	return True
