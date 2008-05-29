# Game.py from Sabacc 0.6
#! This package has been rewritten as sabacc.back.Game
#! Please use that package instead of this one!

from sabacc.back import Game
import sys

sys.stderr.write('back.Game: This class has been obsoleted! Please use sabacc.back.Game instead.\n')

#! 'Dummified' methods
def setInterface(interface=None):
	Game.interface = interface
	
def addPlayer(playername, learning=False):		
	sys.stderr.write('Error: This method does nothing! Please use Sabacc.back.Game.add_player instead!\n')
	return False

removePlayer = Game.remove_player
startGame = Game.start_game
bettingRound = Game.betting_round
drawingRound = Game.drawing_round
endGame=Game.end_game
reset=Game.reset
bettingRound = Game.betting_round
drawingRound = Game.drawing_round
dealCard = Game.deal_card

def get_callable():
	return Game.callable
	
def get_players():
	return Game.loaded[:]
	
def get_num_cards():
	numcards = []
	for player_tuple in Game.loaded:
		numcards.append(len(player_tuple[1]))
	return numcards
	
def get_gameInProgress():
	return Game.game_in_progress
	
def get_pots():
	return (Game.hand_pot, Game.sabacc_pot)
	
def set_removeNext(removeNext):
	sys.stderr.write('Error: This method does nothing!\n')
	return False
