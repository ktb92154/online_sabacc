"""
This module contains all shared constants for the game.
"""
import gettext; _=gettext.gettext # gettext for translations

# Methods to calculate certain constants
def get_agent_dir():
	'''Find agent dir, creating it if necessary, then return'''
	
	import os.path
	if os.path.exists(share_dir):
		global_agent_dir = os.path.join(share_dir, 'sabacc', 'agents')
		
		agent_dir = os.path.join(home_dir, 'agents')
		
		# Create dir and copy files if necessary
		if not os.path.exists(agent_dir):
			print _("Creating agent directory...")
			from shutil import copytree
			copytree(global_agent_dir, agent_dir)
		
	else:  # Root of source distribution.
		agent_dir = os.path.join(base_dir, 'agents')
	
	return os.path.abspath(agent_dir)

def get_base_share_home_dirs():
	'''Find base dir, share dir and home dir'''
	
	import sys, os.path
	current_dir = os.path.dirname(__file__)
	base_dir = os.path.realpath(os.path.join(current_dir, '..'))
	
	share_dir = os.path.join(base_dir, 'share')
	
	# Find home dir
	if sys.platform == 'win32':
		sabacc_dir = "Sabacc"
	else:
		sabacc_dir = ".sabacc"
	sabacc_home = os.path.join(os.path.expanduser("~"), sabacc_dir)
		
	# Create home dir if necessary
	if os.path.exists(share_dir) and not os.path.exists(sabacc_home):
		print _("Creating directory %s") %sabacc_home
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
	number_cards.extend([_("Commander"), _("Mistress"), _("Master"), _("Ace")])
			
	# Names of face cards
	face_cards = _("Idiot"), _("Queen of Air and Darkness"), _("Endurance"), \
	_("Balance"), _("Demise"), _("Moderation"), _("The Evil One"), _("The Star")
	
	# Add numbered cards to list
	for value in number_cards:
		for suit in [_("Sabers"), _("Flasks"), _("Coins"), _("Staves")]:
			# Append card title
			card_names.append(_("%s of %s") %(value, suit))
					
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
	
	
# Important settings must come first!
base_dir, share_dir, home_dir = get_base_share_home_dirs()
lowest_xml_version = 1

agent_dir = get_agent_dir()
card_images = get_card_images()
card_names = get_card_names()
card_values = get_card_values()
glade_filename = get_glade_filename()
icon_filename = get_icon_filename()
moves = dict(draw=0, stick=1, move_call=2, fold=-1, bet_call=-2)
number_of_cards = 76
