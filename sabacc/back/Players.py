# Players.py from Sabacc 0.6
#! This package has been rewritten as sabacc.back.Game
#! Please use that package instead of this one!

from sabacc.back import Game
import sys
loaded = Game.loaded

sys.stderr.write('back.Players: This class has been obsoleted! Please use sabacc.back.Game instead.\n')

#! 'Dummified' methods
def addHuman(name, interface=None):
	return Game.add_player(name, interface, True)

def addXML(filename, interface=None):
	return (Game.add_player(filename, interface, False), None)

def addLoaded(agent):
	sys.stderr.write('Error: This method does nothing!\n')
	return False

def alreadyExists(name):
	sys.stderr.write('Error: This method does nothing!\n')
	return False

def unload(name):
	sys.stderr.write('Error: This method does nothing! Please use sabacc.back.Game.remove_player instead!\n')
	return False
