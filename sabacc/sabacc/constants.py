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
constants.py (partial rewrite of the various settings files from 0.6 'Ackbar')
This module contains all shared constants for the game.
"""

# Methods to calculate certain constants
def get_agent_dir():
	'''Find agent dir, creating it if necessary, then return'''
	
	import os.path
	if os.path.exists(share_dir):
		global_agent_dir = os.path.join(share_dir, 'sabacc', 'agents')
		
		agent_dir = os.path.join(home_dir, 'agents')
		
		# Create dir and copy files if necessary
		if not os.path.exists(agent_dir):
			print "Creating agent directory..."
			from shutil import copytree
			copytree(global_agent_dir, agent_dir)
		
	else:  # Root of source distribution.
		agent_dir = os.path.join(base_dir, 'agents')
	
	return os.path.abspath(agent_dir)

def get_base_share_home_dirs():
	'''Find base dir, share dir and home dir'''
	
	import sys, os.path
	if hasattr(sys, 'frozen'):  # If py2exe distribution.
		current_dir = os.path.dirname(sys.executable)
		base_dir = os.path.abspath(current_dir)
	else:
		current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
		base_dir = os.path.normpath(os.path.join(current_dir, '..'))
	
	share_dir = os.path.join(base_dir, 'share')
	
	# Find home dir
	if sys.platform == 'win32':
		# PyWin32 is the best way, but we may not have it
		try:
			from win32com.shell import shellcon, shell
			user_home = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
		except ImportError:
			sys.stderr.write('Warning: PyWin32 not found - falling back to built-in method...\n')
			user_home = os.path.join(os.path.expanduser('~'), 'Application Data')
		
		sabacc_home = os.path.join(user_home, 'Sabacc')
	else:
		user_home = os.path.expanduser('~')
		sabacc_home = os.path.join(user_home, '.sabacc')
		
	# Create home dir if necessary
	if os.path.exists(share_dir) and not os.path.exists(sabacc_home):
		print "Creating directory %s" %sabacc_home
		from os import makedirs
		makedirs(sabacc_home)
	
	return base_dir, share_dir, sabacc_home

def get_card_images():
	'''Returns a list of image file locations for all cards in the deck'''
	
	card_images = []

	number_cards = range(1, 12) # number_cards = [1 ... 11]
	number_cards.extend(["com", "mis", "mas", "ace"])
			
	# Names of face cards
	face_cards = ["idiot", "queen", "endurance",
	"balance", "demise", "moderation", "evilone", "star"]

	card_number = 0

	# Add numbered cards to list
	for value in number_cards:
		for suit in "sabers", "flasks", "coins", "staves": # for each suit
			# Append card title (eg '42coins_11.png')
			card_images.append("%.2d%s_%s.png" %(card_number, suit, value))
			card_number += 1
					
	# Add face cards to list
	for card_name in face_cards:
		for counter in range(2): # 2 lots of face cards
			# Append card title (eg '68_69demise.png')
			card_images.append("%i_%i%s.png" %(card_number, card_number+1, card_name))
		card_number += 2

	# Add a blank card at the end
	card_images.append("%icardback.png" %card_number)
	
	return card_images

def get_card_names():
	'''Returns a list of card names for every card in the deck'''
	
	card_names = []
			
	number_cards = range(1, 12) # number_cards = [1 ... 11]
	number_cards.extend(["Commander", "Mistress", "Master", "Ace"])
			
	# Names of face cards
	face_cards = "Idiot", "Queen of Air and Darkness", "Endurance", \
	"Balance", "Demise", "Moderation", "The Evil One", "The Star"
	
	# Add numbered cards to list
	for value in number_cards:
		for suit in ["Sabers", "Flasks", "Coins", "Staves"]:
			# Append card title
			card_names.append("%s of %s" %(value, suit))
					
	# Add face cards to list
	for card_name in face_cards:
		for counter in range(2): # 2 lots of face cards
			card_names.append(card_name)
	return card_names

def get_card_values():
	'''Returns a list of values of all cards in the deck'''
	
	card_values = []
	number_cards=range(1, 16) # number_cards=[1, ..., 15] 
	face_cards=0,-2,-8,-11,-13,-14,-15,-17 # values of face cards

	# Add numbered cards to list
	for value in number_cards:
		for counter in range(4): # 4 lots of number cards
			card_values.append(value)
			
	# Add face cards to list
	for value in face_cards:
		for counter in range(2): # 2 lots of face cards
			card_values.append(value)
	
	return card_values

def get_cards_dir():
	'''Find location of card images for cardset and return'''
	
	import os.path
	from sabacc.get_settings import card_set
	
	if os.path.exists(share_dir):
		global_cards_dir = os.path.join(share_dir, 'sabacc', 'cardsets', card_set)
		
		# Create dir and copy files if necessary
		if not os.path.exists(os.path.join(home_dir, 'cardsets')):
			print "Creating cardsets directory..."
			from os import mkdir
			mkdir(os.path.join(home_dir, 'cardsets'))
			
		user_cards_dir = os.path.join(home_dir, 'cardsets', card_set)
		
		# Local takes priority
		if os.path.exists(user_cards_dir):
			cards_dir = user_cards_dir
		else:
			cards_dir = global_cards_dir
		
	else:  # Root of source distribution.
		cards_dir = os.path.join(base_dir, 'cardsets', card_set)
	
	if not os.path.exists(cards_dir):
		import sys
		sys.stderr.write("Warning: Cardset '%s' not found!\n" %card_set)
	return cards_dir

def get_glade_filename():
	'''Discover Glade filename and return'''
	
	import os.path
	name = "sabacc.glade"
	
	if os.path.exists(share_dir):
		glade_filename = os.path.join(share_dir, 'sabacc', 'glade', name)
	else:  # Root of source distribution.
		glade_filename = os.path.join(base_dir, 'glade', name)
	
	return glade_filename

def get_icon_filename():
	'''Locate icon filename and return'''
	
	import sys, os.path
	
	if sys.platform == 'win32':  # Win32 should use the ICO icon.
	    name = 'sabacc.ico'
	else:  # All other platforms should use the PNG icon.
	    name = 'sabacc.png'
	    
	if os.path.exists(share_dir):
		icon_filename = os.path.join(share_dir, 'pixmaps', name)
	else:
		icon_filename = os.path.join(base_dir, 'pixmaps', name)
		
	return icon_filename
	
def get_local_settings_file():
	'''Return the filename of the local settings.xml file,
	creating it if necessary.'''
	import os.path
	
	filename = "settings.xml"
	
	if os.path.exists(share_dir):
		local_settings_file = os.path.join(home_dir, filename)
		
		if not os.path.exists(local_settings_file):
			# Copy the global file here...
			global_settings_file = os.path.join(share_dir, "sabacc", filename)
			
			if not os.path.exists(global_settings_file):
				import sys
				sys.exit('Error! Could not locate default settings file %s!' %global_settings_file)
				
			# Create dir and copy files if necessary
			print "Creating local settings file..."
			from shutil import copyfile
			copyfile(global_settings_file, local_settings_file)
	else:
		local_settings_file = os.path.join(base_dir, filename)
	
	return os.path.abspath(local_settings_file)

# Important settings must come first!
base_dir, share_dir, home_dir = get_base_share_home_dirs()
local_settings_file = get_local_settings_file()
lowest_xml_version = 1

agent_dir = get_agent_dir()
card_images = get_card_images()
card_names = get_card_names()
card_values = get_card_values()
cards_dir = get_cards_dir()
glade_filename = get_glade_filename()
icon_filename = get_icon_filename()
moves = dict(draw=0, stick=1, move_call=2, fold=-1, bet_call=-2)
number_of_cards = 76
