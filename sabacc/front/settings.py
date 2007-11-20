#!/usr/bin/env python
# Front-end settings
# Taken from SabaccApp version 0.5 (initial release)

CARDSET = "swag"

CARDIMAGES = []

numberCards = range(12)
numberCards.remove(0) # numberCards = [1 ... 11]
numberCards.extend(["com", "mis", "mas", "ace"])
		
# Names of face cards
faceCards = ["idiot", "queen", "endurance",
"balance", "demise", "moderation", "evilone", "star"]

cardnum = 0

# Add numbered cards to list
for value in numberCards:
	for suit in ["sabers", "flasks", "coins", "staves"]: # for each suit
		# Append card title (eg '42coins_11.png')
		CARDIMAGES.append("%.2d" %cardnum+suit+"_"+str(value)+".png")
		cardnum += 1
				
# Add face cards to list
for card in faceCards:
	for i in range(2): # 2 lots of face cards
		# Append card title (eg '68_69demise.png')
		CARDIMAGES.append(str(cardnum)+"_"+str(cardnum+1)+card+".png")
	cardnum += 2

# Blank card
CARDIMAGES.append(str(cardnum)+"cardback.png")

# Remove temporary variables
del (numberCards, faceCards, cardnum, value, suit, card, i)
