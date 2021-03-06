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
get_settings.py (taken from Sabacc version 1.0-beta1)
This module contains code to retrieve settings for the game.
"""

from lxml import etree # xml parser
import gettext; _=gettext.gettext # gettext for translations

import old_sabacc.constants as constants

def get_rule_sets():
	'''Find the list of rule sets and their data and return it as a dictionary'''
	
	# Get 'rule_sets' element
	for node in settings_doc.getchildren():
		if node.tag == 'rule_sets':
			rule_sets = node
			break
	else:
		import sys
		sys.exit(_("Error: No rule_sets element found in file '%s'!\n") %filename)
	
	# Get all rulesets
	final = {}
	for node in rule_sets.getchildren():
		if node.tag == 'rule_set':
			upper_value = node.get('upper')
			lower_value = node.get('lower')
			
			final[node.get('name')] = dict(upper=upper_value, lower=lower_value)
	
	return final

def get_setting(setting_name):
	'''Find the given setting and return its value'''
	
	# Get 'settings' element
	for node in settings_doc.getchildren():
		if node.tag == 'settings':
			settings = node
			break
	else:
		import sys
		sys.exit(_("Error: No settings element found in file '%s'!\n") %filename)
	
	# Get required setting
	for node in settings.getchildren():
		if node.tag == 'setting' and node.get('name') == setting_name:
			required_setting = node
			break
	else:
		import sys
		sys.stderr.write(_("Error: '%s' was not found in the settings file!\n") %setting_name)
		return None
	
	setting_value = get_setting_data(required_setting)
	
	return setting_value

def get_setting_data(required_setting):
	'''Get the data from the given setting and return it
	in the correct format'''
	
	data_type = required_setting.get('type')
	raw_setting_value = required_setting.get('value')
	
	if data_type == 'bool':
		setting_value = bool(raw_setting_value)
	elif data_type == 'str':
		setting_value = str(raw_setting_value)
	else:
		setting_value = float(raw_setting_value)
		setting_value_int = int(setting_value)
		
		# If data type is an integer
		if setting_value == setting_value_int:
			setting_value = setting_value_int
	return setting_value

def get_setting_group(group_name):
	'''Find the given setting group and return its contents
	as a dictionary'''
	
	# Get 'settings' element
	for node in settings_doc.getchildren():
		if node.tag == 'settings':
			settings = node
			break
	else:
		import sys
		sys.exit(_("Error: No settings element found in file '%s'!\n") %filename)
	
	# Get required group
	for node in settings.getchildren():
		if node.tag == 'group' and node.get('name') == group_name:
			required_group = node
			break
	else:
		import sys
		sys.stderr.write(_("Error: '%s' was not found in the settings file!\n") %group_name)
		return None
	
	# Get all settings from the group
	final = {}
	for node in required_group.getchildren():
		if node.tag == 'setting':
			setting_value = get_setting_data(node)
			final[node.get('name')] = setting_value
	
	return final
	
	
def get_local_settings_file():
	'''Return the filename of the local settings.xml file,
	creating it if necessary.'''
	import os.path
	
	filename = "settings.xml"
	
	if os.path.exists(constants.share_dir):
		local_settings_file = os.path.join(constants.home_dir, filename)
		
		if not os.path.exists(local_settings_file):
			# Copy the global file here...
			global_settings_file = os.path.join(constants.share_dir, "sabacc",
												filename)
			
			if not os.path.exists(global_settings_file):
				import sys
				sys.exit(_('Error! Could not locate default settings file %s!')
					% global_settings_file)
				
			# Create dir and copy files if necessary
			print _("Creating local settings file...")
			from shutil import copyfile
			copyfile(global_settings_file, local_settings_file)
	else:
		local_settings_file = os.path.join(constants.base_dir, filename)
	
	return os.path.abspath(local_settings_file)

	
def load_settings_file():
	'''Load the settings file into memory, ensuring that it
	parses correctly and is of the right format'''
	
	local_settings_file = get_local_settings_file()
	
	try:
		# load DOM for file
		tree = etree.parse(local_settings_file)
	except IOError: # if file not found
		import sys
		sys.exit(_("Error: The file '%s' was not found!\n") %local_settings_file)
		
	except etree.XMLSyntaxError: # if file not parsing correctly
		import sys
		sys.exit(_("Error: The file '%s' is not formatted correctly!\n") %local_settings_file)
	
	doc = tree.getroot()
	
	# Check that version is OK
	if doc.tag == 'SabaccAppXML':
		xml_version = 0
	elif doc.tag == 'sabacc':
		xml_version = int(doc.get('version'))
	else:
		import sys
		sys.exit(_("Error: The file '%s' is not a Sabacc file!\n") %filename)
	
	from old_sabacc import __major_version__
	
	if (xml_version < constants.lowest_xml_version
			or xml_version > __major_version__):
		import sys
		sys.exit(_("Error: The file '%s' was made using an\nincompatible version of Sabacc!\n") %filename)
	
	return doc


def get_cards_dir():
	'''Find location of card images for cardset and return'''
	
	import os.path
	global card_set
	
	if os.path.exists(constants.share_dir):
		global_cards_dir = os.path.join(constants.share_dir, 'sabacc',
									    'cardsets', card_set)
		
		# Create dir and copy files if necessary
		if not os.path.exists(os.path.join(constants.home_dir, 'cardsets')):
			print _("Creating cardsets directory...")
			from os import mkdir
			mkdir(os.path.join(constants.home_dir, 'cardsets'))
			
		user_cards_dir = os.path.join(constants.home_dir, 'cardsets', card_set)
		
		# Local takes priority
		if os.path.exists(user_cards_dir):
			cards_dir = user_cards_dir
		else:
			cards_dir = global_cards_dir
		
	else:  # Root of source distribution.
		cards_dir = os.path.join(constants.base_dir, 'cardsets', card_set)
	
	if not os.path.exists(cards_dir):
		import sys
		sys.stderr.write(_("Warning: Cardset '%s' not found!\n") %card_set)
	return cards_dir


settings_doc = load_settings_file()

# Setting groups
agent_betting = get_setting_group('agent_betting')
game_settings = get_setting_group('game_settings')
sabacc_shift = get_setting_group('sabacc_shift')

# Individual settings
initial_credits = get_setting('initial_credits')
card_set = get_setting('card_set')
rule_sets = get_rule_sets()
cards_dir = get_cards_dir()
