#!/usr/bin/env python
# Settings for SabaccApp backend

# SabaccAppXML (SabAX) version
SABAX_VERSION=0.5

# Number of credits initially
INITIAL_CREDITS=500

# Game settings
MIN_PLAYERS = 2
NUM_CARDS = 76
POT_BUILDING_ROUNDS = 4
IDLE_TIME = 10

# LearningAgent values
NUM_STATES = 51
NUM_MP_STATES = 98 # multiplayer states
NUM_ACTIONS = 3
FOLD = 101
OVER = 102
UNDER = 103
IDIOT = 104
STATEVALUE = range(24) # 0 ... 23
STATEVALUE[1:1] = [FOLD, OVER, UNDER] # insert FOLD, OVER, UNDER after 0
counter = -1 # temporary - count to -23
while counter >= -23:
	STATEVALUE.append(counter) # add negative value
	counter-=1
STATEVALUE.append(IDIOT) # insert IDIOT at end

# append 'real' states to STATEVALUE
for i in range(NUM_MP_STATES - NUM_STATES):
	STATEVALUE.append(STATEVALUE[i+4])

# Card values
CARDVALUE = []
numberCards=range(16)
numberCards.remove(0) # numberCards=[1, ..., 15]
faceCards=[0,-2,-8,-11,-13,-14,-15,-17] # values of face cards

# Add numbered cards to array
for i in numberCards:
	for j in range(4): # 4 lots of number cards
		CARDVALUE.append(i)
		
# Add face cards to array
for i in faceCards:
	for j in range(2): # 2 lots of face cards
		CARDVALUE.append(i)

# user friendly card names
CARDNAMES = []
		
numberCards = range(12)
numberCards.remove(0) # numberCards = [1 ... 11]
numberCards.extend(["Commander", "Mistress", "Master", "Ace"])
		
# Names of face cards
faceCards = ["Idiot", "Queen of Air and Darkness", "Endurance",
"Balance", "Demise", "Moderation", "The Evil One", "The Star"]
			
# Add numbered cards to list
for x in numberCards:
	for y in ["Sabers", "Flasks", "Coins", "Staves"]: # for each suit
		# Append card title
		CARDNAMES.append(str(x) + " of " + y)
				
# Add face cards to list
for x in faceCards:
	for i in range(2): # 2 lots of face cards
		CARDNAMES.append(x)
		
# Remove temporary variables
del(numberCards, faceCards, counter, i, x)