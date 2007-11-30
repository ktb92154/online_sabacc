#!/usr/bin/env python
# This is the agent window, showing one particular agent's status in the game.
# Taken from SabaccApp version 0.5 (initial release)

import sys, threading, gobject

# import locals
import wndGame
from gtkPlayerInterface import gtkPlayerInterface
from settings import CARDSET, CARDIMAGES

# import from back end
from back.settings import CARDNAMES, CARDVALUE
from back import Players, Game

try:
	import pygtk
	pygtk.require('2.0')
except:
	pass
try:
	import gtk
	import gtk.glade
except:
	sys.exit(1)
	
class wndPlayer (gtkPlayerInterface):
	def __init__(self, playername, human):
		gtkPlayerInterface.__init__(self)
		
		# set variables
		self.name = playername
		self.human = human
		
		gladefile = "front/sabaccapp.glade"
		self.windowname = "wndPlayer"
		self.wTree = gtk.glade.XML(gladefile,self.windowname)
		dic = {"on_wndPlayer_destroy": self.windowClosing}
		self.wTree.signal_autoconnect(dic)
		
		# Name of window
		self.window = self.wTree.get_widget("wndPlayer")
		self.window.set_title(playername)
		
		# Get agent object
		for agent in Players.loaded:
			if agent.name == self.name:
				self.agent = agent
				agent.interface = self
				break
		
		# Init buttons
		spbBet = self.wTree.get_widget("spbBet")
		button1 = self.wTree.get_widget("btnMove1")
		button2 = self.wTree.get_widget("btnMove2")
		button3 = self.wTree.get_widget("btnMove3")
		
		if human:
			spbBet.show()
			button1.set_label("Bet")
			button2.set_label("Leave game")
			button3.set_label("Call the hand")
		else:
			button1.hide()
			button2.hide()
			button3.hide()
		
		# Labels
		self.lblStatus = self.wTree.get_widget("lblStatus")
		self.lblScore = self.wTree.get_widget("lblScore")
		self.lblScoreType = self.wTree.get_widget("lblScoreType")
		self.lblCredits = self.wTree.get_widget("lblCredits")
		
		self.status = 0
		self.chosen = None
		self.buttonSignals = [None, None, None]
		
		self.setStatus(self.status)
		self.setCredits()
		
		# Sort out card layout
		self.cardLayout = self.wTree.get_widget("cardLayout")
		self.cards = []
		self.showCards([-1, -1])
	
	def showCards(self, cards, showall=False):
		if type(showall) == str:
			showall = False
		
		# bugfix for if player could not afford ante
		if cards == []:
			cards=[-1, -1]
		
		# hide computer's cards, but show number
		if not (self.human or showall):
			cards = cards[:] # copy of original
			for i in range(len(cards)):
				cards[i] = -1
		
		if cards == self.cards:
			return
		else:
			self.cards = cards[:]
		
		smallcards = False
		
		if len(cards) <= 5:
			rows = 2
			columns = len(cards)
		elif len(cards) <= 10:
			rows = 4
			columns = (len(cards) / 2 + len(cards) % 2)
		else:
			smallcards = True
			if len(cards) % 8 >= 1:
				mod = 1
			else:
				mod = 0
			rows = len(cards) / 8 + mod
			columns = 8
		
		# remove current cards from table
		for w in self.cardLayout.get_children():
			self.cardLayout.remove(w)
		
		self.cardLayout.resize(rows, columns)
		
		i = 0
		score = 0
		idiot = [False, False, False]
		unknown = False
		
		for row in range(rows):
			for col in range(columns):
				if not smallcards and row % 2 == 1: # odd rows
					break
				try:
					im = gtk.Image()
					filename = "cardsets/"+CARDSET+"/"+CARDIMAGES[cards[i]]
					if smallcards:
						im.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file(
							filename).scale_simple(62, 89,
							gtk.gdk.INTERP_BILINEAR))
					else:
						im.set_from_file(filename)
					im.show()
					self.cardLayout.attach(im, col,col+1,row,row+1)
					if not smallcards:
						if cards[i] == -1:
							text = "Unknown card"
						else:
							text = CARDNAMES[cards[i]] + " (value "\
								+ str(CARDVALUE[cards[i]]) + ")"
						lbl = gtk.Label(text)
						lbl.show()
						self.cardLayout.attach(lbl, col, col+1, row+1, row+2, xpadding=3)
					# calculate score
					if cards[i] != -1:
						score += CARDVALUE[cards[i]]
						
						if CARDVALUE[cards[i]] == 0:
							idiot[0] = True
						elif CARDVALUE[cards[i]] == 2:
							idiot[1] = True
						elif CARDVALUE[cards[i]] == 3:
							idiot[2] = True
					else:
						unknown = True
					i+=1
				except IndexError: # occurs when odd number of cards
					pass
		
		# resize window to minimum possible
		if self.window.get_property("visible"):
			minwidth, minheight = self.window.size_request()
			self.window.resize(minwidth, minheight)
		
		
		# Score type
		scoretype = None
		
		if idiot == [True, True, True] and len(cards) == 3:
			scoretype = "Idiot's Array"
		elif score in [23, -23]:
			scoretype = "Pure Sabacc"
		elif score == 0 or score > 23 or score < -23:
			scoretype = "Bomb out"
			
		if unknown:
			self.lblScore.set_text("Unknown")
			self.lblScoreType.set_text("")
		else:
			self.lblScore.set_text(str(score))
			if scoretype == None:
				self.lblScoreType.set_text("")
			else:
				self.lblScoreType.set_text(" ("+scoretype+")")
		
	def setStatus(self, status):
		if status == 0:
			# Previous status
			if self.status == 3:
				self.errors = False
				text = self.lblStatus.get_text()
			else:
				text = "Waiting for game to begin..."
			self.active = False
		elif status == 1:
			text = "In game"
			self.active = True
		elif status == 2:
			text = "Waiting for game to end..."
			self.active = False
		elif status == 3:
			text = "Errors reported!"
			self.active = True
		
		self.lblStatus.set_text(text)
		self.status = status
	
	def setCredits(self, credits=None):
		if credits == None:
			credits = self.agent.credits
		self.lblCredits.set_text(str(credits))
	
	def windowClosing(self, window):
		ac=(self.active and self.human)
		if self.active:
			if self.human:
				self.chosen = -1
				self.wait = False
			else:
				Game.set_removeNext(self.name)
				wndGame.endWait()
			wndGame.updatePlayers(len(Game.get_players())-1)
			
		wndGame.removePlayer(self.name, self.active)
		
	def show(self):
		self.window.show()
		
	def make_inactive(self):
		self.setStatus(3)
		
	def getMove(self, cards):
		thread = threading.currentThread()
		
		if thread != self.mainThread:
			self.wait = True
			gobject.idle_add(self.getMove, cards)
			while self.wait:
				pass
			
			return self.chosen
		else:
			# show pots
			wndGame.updatePots()
			wndGame.updatePlayers()
			
			self.setStatus(1)
			callable = Game.get_callable()
			spbBet = self.wTree.get_widget("spbBet")
			btnDraw = self.wTree.get_widget("btnMove1")
			btnStick = self.wTree.get_widget("btnMove2")
			btnCall = self.wTree.get_widget("btnMove3")
			spbBet.hide()
			btnDraw.set_label("Draw a card")
			btnDraw.set_sensitive(True)
			self.buttonSignals[0] = btnDraw.connect("clicked", self.makeMove, 0)
			btnStick.set_label("Stick")
			btnStick.set_sensitive(True)
			self.buttonSignals[1] = btnStick.connect("clicked", self.makeMove, 1)
			
			if callable:
				btnCall.set_sensitive(True)
				self.buttonSignals[2] = btnCall.connect("clicked", self.makeMove, 2)
	
	def getBet(self, cards, mustMatch):
		thread = threading.currentThread()
		
		if thread != self.mainThread:
			self.wait = True
			gobject.idle_add(self.getBet, cards, mustMatch)
			while self.wait:
				pass
			
			return self.chosen
		else:
			# show pots
			wndGame.updatePots()
			wndGame.updatePlayers()
			
			self.setStatus(1)
			callable = Game.get_callable()
			spbBet = self.wTree.get_widget("spbBet")
			btnBet = self.wTree.get_widget("btnMove1")
			btnFold = self.wTree.get_widget("btnMove2")
			btnCall = self.wTree.get_widget("btnMove3")
			spbBet.set_sensitive(True)
			adj = spbBet.get_adjustment()
			adj.set_all(mustMatch, mustMatch, self.agent.credits, 1, 1, 1)
			spbBet.show()
			btnBet.set_label("Bet")
			self.buttonSignals[0] = btnBet.connect("clicked", self.makeBet)
			btnBet.set_sensitive(True)
			btnFold.set_label("Leave Game")
			self.buttonSignals[1] = btnFold.connect("clicked", self.makeMove, -1)
			btnFold.set_sensitive(True)
			
			if callable:
				btnCall.set_sensitive(True)
				self.buttonSignals[2] = btnCall.connect("clicked", self.makeMove, -2)
	
	def gameStatus(self, won, cards, credits=None):
		thread = threading.currentThread()
		if thread != self.mainThread:
			self.wait=True
			gobject.idle_add(self.gameStatus, won, cards, credits)
			while self.wait:
				pass
			
		else:
			self.showCards(cards)
			self.setCredits(credits)
			
			title = "Game over"
			if won:
				text = "Congratulations. You have won!"
			else:
				text = "Sorry. You didn't win this time."
				
			dialog = gtk.Dialog(title, self.window, gtk.DIALOG_MODAL,
				(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
			dialog.connect("response", self.dialog_destroy)
			hbox = gtk.HBox()
			icon = gtk.Image()
			icon.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
			label = gtk.Label(text)
			hbox.add(icon)
			hbox.add(label)
			dialog.vbox.pack_start(hbox, True, True, 0)
			dialog.show_all()
		return 0
		
	def makeMove(self, button, chosen):
		self.chosen = chosen
		
		buttons=[]
		
		buttons.append(self.wTree.get_widget("btnMove1"))
		buttons.append(self.wTree.get_widget("btnMove2"))
		buttons.append(self.wTree.get_widget("btnMove3"))
		
		for i in range(3): # [0, 1, 2]
			if self.buttonSignals[i] != None:
				buttons[i].disconnect(self.buttonSignals[i])
				buttons[i].set_sensitive(False)
				self.buttonSignals[i] = None
		
		spinner = self.wTree.get_widget("spbBet")
		spinner.set_sensitive(False)
		
		self.wait = False
	
	def makeBet(self, button):
		spinner = self.wTree.get_widget("spbBet")
		bet = int(spinner.get_value())
		self.setCredits(self.agent.credits-bet)
		self.makeMove(None, bet)
