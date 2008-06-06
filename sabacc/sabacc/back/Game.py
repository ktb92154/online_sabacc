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
Game.py (rewrite of back.Game and back.Players from 0.6 'Ackbar')
This module contains the code for the game of Sabacc, including
adding players, starting and finishing the game.
"""

import sys

# Initialise variables
players_in_game = 0
names = [] # Names of loaded players
loaded = [] # Player objects and their hands
deck = [] # All cards in the deck
callable = False # Can game be called right now?
hand_pot = 0 # Contents of hand pot
sabacc_pot = 0 # Contents of Sabacc pot
shift_timer = None # Time until the next Sabacc shift
interface = None # Interface with the user
idle_moves = 0 # Number of idle moves taken - Used for automatically declaring a draw.
game_in_progress = False

def add_player(name, interface=None, human=True):
	'''Creates an agent with the specified name (or from the specified
	filename) and adds to the game.'''
	if game_in_progress:
		sys.stderr.write('Error: A game is already in progress!\n')
		return False
	
	already_in_game = False
	if human:
		if name not in names:
			from Agents import HumanAgent
			agent = HumanAgent(name, interface)
		else:
			already_in_game = True
	else:
		filename = name
		
		from Agents import RuleBasedAgent
		agent = RuleBasedAgent(filename, interface)
		
		if not agent.loaded:
			return False
		
		name = agent.name
		if name in names:
			already_in_game = True
	
	if already_in_game:
		sys.stderr.write("Error: A player with the name '%s' is already in the game.\n" %name)
		return False
	else:
		# add agent to list of agents
		names.append(name)
		loaded.append((agent, [], True)) # ([], True) means empty hand and player is in the game
		global players_in_game
		players_in_game += 1
		return True

def remove_player(name):
	'''Removes the given player from the game, alerting them if necessary.
	If a game is running, the player will be added at the end of the game,
	otherwise the player will be unloaded and will remain out of the game.'''
	global game_in_progress, players_in_game
	
	if name in names:
		index = names.index(name)
		agent, hand, in_game = loaded[index]
		
		if game_in_progress:
			agent.game_over(won=False, cards=hand)
			players_in_game -= 1
			loaded[index] = (agent, hand, False)
		else:
			# unload player
			del loaded[index]
			names.remove(name)
			
		# if only one player left, end game
		if players_in_game == 1:
			game_in_progress = False
		
		return True
	else: 
		sys.stderr.write("Error: Player '%s' not found!\n" %name)
		return False

def start_game(ante=0):
	'''Start the game if possible, then run through betting and drawing
	rounds until the game is called or runs out of players, then call the
	end_game method.'''
	global game_in_progress, shift_timer
	
	if game_in_progress:
		sys.stderr.write('Error: A game is already in progress!\n')
		return False
	from back.settings import MIN_PLAYERS#!
	if len(loaded) < MIN_PLAYERS:
		sys.stderr.write('Error: A minimum of %s players must be in the game!\n' %MIN_PLAYERS)
		return False
	
	game_in_progress = True
	from back.settings import SABACCSHIFT_ON, SABACCSHIFT_TIME_MIN, SABACCSHIFT_TIME_MAX#!
	
	# initialise Sabacc Shift timer
	if SABACCSHIFT_ON:
		from random import uniform
		from threading import Timer
		time_until_shift = round(uniform(SABACCSHIFT_TIME_MIN,  SABACCSHIFT_TIME_MAX),2)
		shift_timer = Timer(time_until_shift, start_shift)
		shift_timer.start()
	
	global idle_moves, deck
	idle_moves = 0
	deck = []
	
	# reset deck and hands
	for player_tuple in loaded:
		player, hand, in_game = player_tuple
		loaded[loaded.index(player_tuple)] = (player, [], True)
	
	from back.settings import NUM_CARDS#!
	for card in range(NUM_CARDS):
		deck.append(card)
	
	from random import shuffle
	shuffle(deck)
	
	# Collect Ante
	for player, hand, in_game in loaded:
		# make sure player doesn't see his previous set of cards
		player.examine_cards([])
		
		# player can't afford game so is kicked out
		if player.credits < ante*2:
			remove_player(player.name)
			interface.write("%s could not afford the buy into the game") %player.name
			in_game = False
		else: # place ante into hand and sabacc pots
			global hand_pot, sabacc_pot
			player.credits -= ante*2
			hand_pot += ante
			sabacc_pot += ante
	
	# If only 1 player left, do not start game
	if not game_in_progress:
		# Refund credits and reset pots
		loaded[0][0].credits += hand_pot*2
		
		sabacc_pot -= hand_pot
		hand_pot = 0
		
		# End game manually
		end_game(show_all_cards=False)
		return False
	
	# Initial betting
	betting_round()
	
	# Deal two cards to each player
	for player, hand, in_game in loaded:
		card1 = deal_card()
		card2 = deal_card()
		if card1 and card2:
			hand.append(card1)
			hand.append(card2)
		else:
			return False
		
		player.examine_cards(hand)
	
	# variables used for pot-building phase
	global callable
	callable = False
	show_all_cards = True
	current_round = 0
	
	# Repeat betting and drawing rounds until hand is called or a winner is declared
	while game_in_progress:
		# Perform betting round
		if betting_round(): #if a player called
			break
		if not game_in_progress: # if only 1 player remaining
			show_all_cards = False
			break
			
		# Perform drawing round
		if drawing_round(): # if a player called
			break
		if not game_in_progress: # if only 1 player remaining
			show_all_cards = False
			break
		
		from back.settings import POT_BUILDING_ROUNDS#!
		if current_round < POT_BUILDING_ROUNDS: # if pot-building phase in progress
			current_round += 1
		else:
			callable = True
	
	# Calling of hands
	end_game(show_all_cards)
	return True
	
def betting_round(starting_player=0):
	'''Perform one round of betting (two if called), starting with
	the given player.'''
	
	# determine order of play
	if starting_player == 0: # normal order
		loaded_copy = loaded[:]
	else:
		loaded_copy = loaded[starting_player:] + loaded[:starting_player]
	
	must_match = 0 # will increase as players bet
	called = False # has the game been called?
	already_bet = [] # how much has each player already bet?
	from settings import moves # mapping of move names to numbers
	
	for index in range(len(loaded_copy)): # for each player
		# no player has bet this round
		already_bet.append(0)
	
	while True: # loop will repeat until all players have matched
		# used to ensure that every player bets enough
		lowest_bet = must_match
		
		index = 0
		
		global hand_pot, callable
		
		for player, hand, in_game in loaded_copy:
			legal_move = False
			
			#perform bet
			while in_game and not legal_move:
				# ask player for bet
				this_player_must_match = must_match - already_bet[index]
				
				bet = player.bet(hand, this_player_must_match)
				
				if bet == moves['fold']:
					legal_move = True
					remove_player(player.name)
					interface.write("%s left the game" %player.name)
					in_game = False
					
				elif bet == moves['bet_call'] and callable:
					interface.write("%s called the hand" %player.name)
					
					# Calling no longer allowed
					callable = False
					if this_player_must_match == 0:
						# if betting is over, repeat the round.
						# Otherwise the round will repeat anyway
						betting_round(index)
						legal_move = True
					
					called = True
					
				elif bet == this_player_must_match:
					legal_move = True
					hand_pot += bet
					if bet > 0: # if player bet more than 0, tell the user
						interface.write("%s matched the bet" %player.name)
						already_bet[index] += bet
						player.credits -= bet
				
				elif bet > this_player_must_match: #if player is raising
					legal_move = True
					hand_pot += bet
					already_bet[index] += bet
					raised_by = bet - this_player_must_match
					must_match = already_bet[index]
					interface.write("%s raised the bet by %i" % (player.name, raised_by))
					player.credits -= bet
			
			# lower lowest_bet if necessary
			if in_game and already_bet[index] < lowest_bet:
				lowest_bet = already_bet[index]
			
			index += 1
			
			if not game_in_progress: # if only 1 player left
				break
		
		if not game_in_progress: # if only 1 player left
			break
		
		if lowest_bet == must_match: # if betting complete
			break
		
	return called

def drawing_round():
	'''Perform one round of drawing, starting with player 0.'''
	
	from settings import moves
	global callable
	
	called = False
	index = 0
	
	for player, hand, in_game in loaded: # for each player
		legal_move = False
		
		#perform move
		while in_game and not legal_move:
			from back.settings import IDLE_TIME
			global idle_moves
			if idle_moves >= IDLE_TIME and callable:
				# force the game to be called
				idle_moves = 0
				move = moves['move_call']
			else:
				# ask player for move
				move = player.move(hand)
			
			if move == moves['fold']:
				legal_move = True
				idle_moves = 0
				remove_player(player.name)
				interface.write("%s left the game" %player.name)
				in_game = False
				
			elif move == moves['draw']:
				legal_move = True
				idle_moves = 0
				card = deal_card()
				if card:
					hand.append(card)
					interface.write("%s drew a card" %player.name)
					interface.show_num_cards(len(hand), player.name)
				
			elif move == moves['stick']:
				legal_move = True
				idle_moves += 1
				
			elif move == moves['move_call'] and callable:
				legal_move = True
				idle_moves = 0
				callable = False
				interface.write("%s called the hand" %player.name)
				betting_round(index) # final round of betting
				called = True
		
		if in_game:
			player.examine_cards(hand)
		index += 1
		
		if called or not game_in_progress:
			break
	
	return called

def deal_card():
	'''Take the first card from the deck and return it, or
	return False if the deck is empty.'''
	
	if len(deck) >=1:
		return deck.pop(0)
		
	else: # if deck is empty
		sys.stderr.write('Error: The deck is empty!\n')
		return False

def end_game(show_all_cards):
	'''Calculates the winner(s) of the game and dishes
	out any winnings owed.'''
	
	if shift_timer != None:
		shift_timer.cancel()
	
	hand_types = dict(positive=0, negative=1, idiot=2, bomb=3)
	hand_values = [] # takes form (player name, value, num cards, hand type) for each player
	best_score = 0 # best recorded score so far
	cards_to_show = [] # takes form (player, hand) for all relevant players
	
	global players_in_game, hand_pot, sabacc_pot, game_in_progress
	
	# if only one player, he wins by default
	if players_in_game == 1:
		win_by_default = True
	else:
		win_by_default = False
	
	for player, hand, in_game in loaded:
		if in_game:
			if show_all_cards:
				cards_to_show.append((player, hand))
			
			# calculate hand
			hand_value = get_value(hand)
			
			if hand_value == False:
				sys.stderr.write('Error calculating value of hand for player %s!\n' %player.name)
				hand_value = 0
			
			if hand_value < 0:
				hand_type = hand_types['negative']
			else:
				hand_type = hand_types['positive']
			
			if not win_by_default:
				# did player bomb out?
				if hand_value > 23 or hand_value < -23 or hand_value == 0: 
					hand_type = hand_types['bomb']
					interface.write("%s bombed out" %player.name)
					
					# bombing out penalty
					sabacc_pot += hand_pot
					player.credits -= hand_pot
			
			# check for possible Idiot's array
			if hand_value == 5 and len(hand) == 3:
				idiot_cards = (False, False, False) # used to count number of idiot's array cards
				for card in hand:
					from back.settings import CARDVALUE#!
					if CARDVALUE[card] == 0:
						idiot_cards[0] = True
					elif CARDVALUE[card] == 2:
						idiot_cards[1] = True
					elif CARDVALUE[card] == 3:
						idiot_cards[2] = True
				
				if idiot_cards == [True, True, True]: # idiot's array!
					hand_type = hand_types['idiot']
					# 24 here represents the Idiot's Array, as an
					# actual score of 24 is a bomb out!
					best_score = 24
			
			if hand_type == hand_types['bomb']:
				interface.show_cards(hand, player.name)
				remove_player(player.name)
				in_game = False
			else:
				# add hand values to list
				hand_values.append((player.name, hand_value, len(hand), hand_type))
				
				# make score positive for purposes of winner estimation
				if hand_type == hand_types['negative']:
					hand_value = -hand_value
				
				# rough winner estimation
				if hand_value > best_score:
					best_score = hand_value
	
	# show all visible cards
	interface.show_all_cards(cards_to_show)
	
	# find winner using best_score
	winners = [] # will take the form (player name, hand value, num cards, hand type) for each player
	
	for player_name, hand_value, num_cards, hand_type in hand_values:
		# ensure idiot's array always wins
		if best_score == 24:
			if hand_type == hand_types['idiot']:
				hand_value = best_score

		if hand_value in (best_score, -best_score):
			winners.append((player_name, hand_value, num_cards, hand_type))
	
	# There can only be one winner! Find out who it is...
	if len(winners) > 1:
		# remove negative winners if possible
		positive_winners = []
		for winner_tuple in winners:
			if winner_tuple[3] == hand_types['positive']:
				positive_winners.append(winner_tuple)
		
		if len(positive_winners) >= 1:
			# remove all negative winners
			winners = positive_winners
		
	#Let's try a sudden demise/card count
	if len(winners) > 1:
		from back.settings import SUDDENDEMISE#!
		if SUDDENDEMISE:
			text="A sudden demise was enacted between "
			for winner_tuple in winners:
				name = winner_tuple[0]
				if winner_tuple == winners[0]:
					text += name
				elif winner_tuple == winners[-1]:
					text += " and %s." %name
				else:
					text += ", %s" %name
			interface.write(text)
			
			card_error = False
			
			# Keep drawing cards until all competition has been eliminated
			while True:
				best_score = 0
				cards_to_show = [] # takes form (cards, name)
				
				for player_name, hand_value, num_cards, hand_type in winners:
					player_index = names.index(player_name)
					player, hand, in_game = loaded[player_index]
					
					card = deal_card()
					
					if card:
						hand.append(card)
					else:
						card_error = True
						break
						
					cards_to_show.append((hand, player_name))
					
					# calculate player's new hand
					hand_value = get_value(hand)
					
					if hand_value < 0:
						hand_type = hand_types['negative']
						positive_value = -hand_value
					else:
						hand_type = hand_types['positive']
						positive_value = hand_value
					
					if positive_value > 23: # if player bombed out
						hand_type = hand_types['bomb']
						interface.write("%s bombed out" %player_name)
						
					elif positive_value > best_score:
						best_score = positive_total
				
				interface.show_all_cards(cards_to_show)
				
				if card_error: # No cards left in deck!
					break
				
				if best_score == 0: # everyone bombed out
					winners = []
					break
				
				new_winners = [] # takes form (player name, hand value, num cards, hand type)
				
				# Who won the round?
				for winner_tuple in winners:
					if winner_tuple[1] == best_score:
						new_winners.append(winner_tuple)
				
				if len(new_winners) > 1:
					# positive only
					positive_winners = []
					for winner_tuple in new_winners:
						if winner_tuple[3] == hand_types['positive']:
							positive_winners.append(winner_tuple)
					
					if len(positive_winners) >= 1:
						new_winners = positive_winners
				
				winners = new_winners
				
				if len(winners) <= 1:
					# Finally! The decision is made!
					break
			
		# Don't like sudden demise? Do a card count instead.
		else:
			# calculate winner with least cards
			from back.settings import NUM_CARDS
			least_cards = NUM_CARDS # maximum number of cards
			least_cards_winners = []
			
			for winner_tuple in winners:
				num_cards = winner_tuple[2]
				
				if num_cards < least_cards:
					least_cards = num_cards
			
			# find players with least cards
			for winner_tuple in winners:
				if winner_tuple[2] == least_cards:
					least_cards_winners.append(winner_tuple)
			
			winners = least_cards_winners
	
	game_in_progress = False
	
	winner_names = []
	for winner_tuple in winners:
		winner_names.append(winner_tuple[0])
	
	# We finally have a winner! Let's give him his prize...
	if len(winners) >= 1:
		# calculate winnings - if still more than 1 winner
		# then pot will be split
		winnings = hand_pot / len(winners)
		hand_pot % len(winners)
		
		hand_value = winners[0][1]
		hand_type = winners[0][3]
	else: # avoid divide-by-zero
		winnings = 0
		hand_value = hand_type = None
	
	# Let's find out if the winner deserves the Sabacc pot as well
	if hand_type == hand_types['idiot'] or hand_value in (23, -23):
		winnings += sabacc_pot / len(winners)
		sabacc_pot %= len(winners)
	
	# declare game outcome to all players
	text = ''
	
	for player, hand, in_game in loaded:
		if in_game:
			won = False
			if player.name in winner_names:
				won = True
				# award winnings
				player.credits += winnings
				
				if player.name == winner_names[0]:
					text += player.name
				elif player.name == winner_names[-1]:
					text += " and %s." %player.name
				else:
					text += ", %s" %player.name
			
			# tell player that game is over
			player.game_over(won, hand)
	
	if len(winners) >= 1:
		if len(winners) == len(loaded) and len(winners) > 1:
			interface.write("The game was a draw.")
		else:
			interface.write("The game was won by %s." %text)
	
	else: # Looks like nobody won. The house wins today.
		sabacc_pot += hand_pot
		hand_pot = 0
		interface.write("No winners found")
	
	# Add all 'out' players back into the game
	for player, hand, in_play in loaded:
		if not in_play:
			interface.write("%s re-entered the game" %player.name)
			players_in_game += 1
	
	# Change the order of players ready for the next round
	first_player = loaded[0]
	loaded.remove(first_player)
	loaded.append(first_player)
	
	return True

def get_value(cards):
	'''Returns the value of the given list of cards.'''
	
	from back.settings import CARDVALUE
	hand_total = 0
	for card in cards:
		hand_total += CARDVALUE[card]
	
	return hand_total

def start_shift():
	'''Randomly swaps certain cards for others, then resets
	the timer for the next shift.'''
	
	from random import seed, randint, uniform
	seed()
	
	from back.settings import NUM_CARDS, SABACCSHIFT_NUM_MIN,\
		SABACCSHIFT_NUM_MAX, SABACCSHIFT_TIME_MIN,\
		SABACCSHIFT_TIME_MAX #!
	num_to_shift = randint(SABACCSHIFT_NUM_MIN, SABACCSHIFT_NUM_MAX)
	
	# A player is more likely to be shifted if he has more cards
	cards_in_play = []
	
	for player, hand, in_play in loaded:
		if in_play:
			cards_in_play += hand
	
	# Don't shift more cards than there are available!
	if num_to_shift > len(cards_in_play):
		num_to_shift = len(cards_in_play)
	
	if num_to_shift >= 1:
		interface.write("A Sabacc Shift occurred!")
	
	for count in range(num_to_shift):
		# Pick a card to shift
		orig_pos = randint(0, len(cards_in_play)-1)
		new_card = randint(0, NUM_CARDS-1)
		
		# Card must be swapped with another card,
		# otherwise chaos will ensue
		for index in range(len(cards_in_play)):
			if cards_in_play[index] == new_card: # Another player holds the new card
				cards_in_play[index] = cards_in_play[orig_pos]
				cards_in_play[orig_pos] = new_card
				break
		
		else: # Card is still in deck
			for index in range(len(deck)):
				if deck[index] == new_card:
					deck[index] = cards_in_play[orig_pos]
					cards_in_play[orig_pos] = new_card
					break
	
	# Replace players' cards
	for player, hand, in_play in loaded:
		if in_play:
			new_hand = cards_in_play[:len(hand)]
			cards_in_play = cards_in_play[len(hand):]
			if new_hand != hand:
				hand = new_hand
				player.shift(new_hand)
	
	# Start new timer
	if game_in_progress:
		time_until_shift = round(uniform(SABACCSHIFT_TIME_MIN,  SABACCSHIFT_TIME_MAX),2)
		
		from threading import Timer
		global shift_timer
		shift_timer = Timer(time_until_shift, start_shift)
		shift_timer.start()

def reset():
	'''Resets all game variables to their original settings'''
	
	if game_in_progress:
		sys.stdout.write('Error: A game is currently running!\n')
		return False
	
	global players_in_game, names, loaded, deck, callable, hand_pot, \
		sabacc_pot, shift_timer, idle_moves
	
	players_in_game = 0
	names = []
	loaded = []
	deck = []
	callable = False
	hand_pot=0
	sabacc_pot=0
	shift_timer = None
	idle_moves = 0
	
	return True

#! Old function names
addPlayer=add_player
removePlayer=remove_player
startGame=start_game
endGame=end_game
bettingRound = betting_round
drawingRound = drawing_round
dealCard = deal_card
