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
settings.py (taken from version 0.6beta1)
This module contains settings for the application's front end.

It will eventually be replaced by a standard config file.
"""

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
