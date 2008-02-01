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
wndGame.py (taken from version 0.6beta1)
This module contains the wndGame class and methods to
call it without having to instantiate it first.
"""

# Import locals
from wndPlayer import wndPlayer
import wndApp

# import from back end
from sabacc.back import Game, Players
from sabacc.back.Interfaces import gameInterface

# Import from libraries
import sys, threading, time, gobject, os.path, gtk
import gtk.glade
from datetime import datetime
	
class wndGame (gameInterface):
	"""
	This class contains the testing window, where any number
	of agents can be loaded up (using wndPlayer) to play a game.
	"""
	def __init__(self):
		# Initialise variables
		self.players = []
		self.mainThread = threading.currentThread()
		self.lastante=5
		self.humans=0
		self.showMsgs = True # bugfix for messages
		
		from __init__ import gladefile
		self.windowname = "wndGame"
		self.wTree = gtk.glade.XML(gladefile,self.windowname)
		dic = {"on_btnHuman_clicked": self.btnHuman_click,
			"on_btnComputer_clicked": self.btnComputer_click,
			"on_btnStart_clicked": self.btnStart_click,
			"on_btnEndGame_clicked": self.btnEndGame_click}
		self.wTree.signal_autoconnect(dic)
		
		self.window = self.wTree.get_widget("wndGame")
		
		Game.setInterface(self)
		
		#Set up GUI
		self.lblNumPlayers = self.wTree.get_widget("lblNumPlayers")
		self.lblHandPot = self.wTree.get_widget("lblHandPot")
		self.lblSabaccPot = self.wTree.get_widget("lblSabaccPot")
		self.updatePlayers()
		self.updatePots()
		
		#create status object
		self.lblStatus = gtk.Label()
		self.lblStatus.set_alignment(0.0,0.0)
		
		statusScroller = self.wTree.get_widget("statusScroller")
		statusScroller.add_with_viewport(self.lblStatus)
		self.lblStatus.show()
		
	def btnHuman_click(self,widget):
		self.addPlayer(True)
		
	def btnComputer_click(self,widget):
		self.addPlayer(False)
		
	def btnStart_click(self, button):
		# Set up dialog
		message = "Please enter a buy-in price:"
		d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
		gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, message)
		adj=gtk.Adjustment(self.lastante, 0, 500, 1, 1, 1)
		textEntry = gtk.SpinButton(adj)
		d.vbox.add(textEntry)
		textEntry.show()
		resp=d.run()
		d.destroy()
		
		if resp == gtk.RESPONSE_OK:
			self.lastante=int(textEntry.get_text())
			button.set_sensitive(False)
		
			for player in self.players:
				player.setStatus(1)
		
			t = threading.Thread(target=self.playGame, name="playGame")
			t.setDaemon(True)
			t.start()
		
		
	def btnEndGame_click(self,widget):
		# Destroy current window
		btnTest = wndApp.wTree.get_widget("btnTest")
		btnTest.set_sensitive(True)
		self.window.destroy()
		self.showMsgs = False

	def write(self, text):
		now = datetime.today().strftime("(%H:%M:%S) ")
		finaltext = now + text + "\n" + self.lblStatus.get_text()
		self.lblStatus.set_text(finaltext)
		
		name=None
		if text[-13:] == "left the game":
			name = text[:-14]
		elif text[-10:] == "bombed out":
			name = text[:-11]
				
		if name != None:
			# Find agent
			for player in self.players:
				if player.name == name:
					player.setStatus(2)
					break

	def show(self):
		#Move window to bottom of screen and resize
		width, height = self.window.get_size()
		newwidth=gtk.gdk.screen_width()
		newheight = height+100
		self.window.resize(newwidth, newheight)
		self.window.move(0, gtk.gdk.screen_height() - newheight)
		
		#Show window
		self.window.show()
		
	def writeError(self, text, title=None, parent=None):
		thread = threading.currentThread()
		if thread != self.mainThread:
			gobject.idle_add(self.writeError, text, title, parent)
			time.sleep(5)
			
		else:
			if title==None:
				title = text
			if parent==None:
				parent=self.window
			dialog = gtk.Dialog(title, parent, gtk.DIALOG_MODAL,
				(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
			dialog.connect("response", self.error_destroy)
			hbox = gtk.HBox()
			icon = gtk.Image()
			icon.set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_DIALOG)
			label = gtk.Label(text)
			hbox.add(icon)
			hbox.add(label)
			dialog.vbox.pack_start(hbox, True, True, 0)
			dialog.show_all()
			
	def error_destroy(self, dialog, response):
		dialog.destroy()
		
	def addPlayer(self, human):
		btnStart = self.wTree.get_widget("btnStart")

		if human:
			# Set up dialog
			message = "What is your name?"
			d = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
			gtk.MESSAGE_QUESTION, gtk.BUTTONS_OK_CANCEL, message)
			textEntry = gtk.Entry()
			d.vbox.add(textEntry)
			textEntry.show()
			resp=d.run()
			d.destroy()
			
			if resp == gtk.RESPONSE_CANCEL:
				name=""
			else:
				name=textEntry.get_text()
				if name != "":
					# add player to game
					status = Players.addHuman(name, self)
			
					if status != 0: # name already taken
						self.writeError("Error: A player called "+name+" is already loaded!")
						name=""
					else:
						self.humans += 1
		else:
			# Create dialog
			message = "Please select the agent file"
			d = gtk.FileChooserDialog(title=message, parent=self.window,
			buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
			gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
			
			from __init__ import basedir, sharedir
			agentdir = os.path.join(basedir, "agents")
			if not os.path.exists(agentdir):
				agentdir = os.path.join(sharedir, "sabacc", "agents")
			
			# Create filters
			xmlfilter = gtk.FileFilter()
			xmlfilter.add_pattern("*.xml")
			xmlfilter.set_name("XML Files")
			anyfilter = gtk.FileFilter()
			anyfilter.add_pattern("*")
			anyfilter.set_name("All Files")
			d.add_filter(xmlfilter)
			d.set_filter(xmlfilter)
			d.add_filter(anyfilter)
			d.set_current_folder(os.path.abspath(agentdir))
			
			# Show dialog
			resp=d.run()
			filename = d.get_filename()
			d.destroy()
			if resp == gtk.RESPONSE_REJECT:
				name=""
			else:
				t = threading.Thread(target=self.loadAgent, args=[filename], name="loadAgent")
				t.setDaemon(True)
				t.start()
				
				title = "Loading..."
				text = "Please wait. Loading data..."
				dialog = gtk.Dialog(title, self.window, gtk.DIALOG_MODAL,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_DELETE_EVENT))
				label = gtk.Label(text)
				dialog.vbox.pack_start(label, True, True, 0)
				dialog.show_all()
				self.loading = dialog
				resp = dialog.run()
				
				if resp == gtk.RESPONSE_DELETE_EVENT: # 'cancel' clicked
					dialog.destroy()
					name = ""
				else:
					name = self.loadedName
				
		
		if name != "":
			# add player to game
			status = Game.addPlayer(name)
			
			if status == -3: # game already in progres
				self.writeError("Error: Game in progress. Please try again later.", "Game in progress")
				Players.unload(name)
				name=""
		
		if name != "":
			# open player window
			number = len(self.players)
			player = wndPlayer(name, human)
			player.window.set_transient_for(self.window)
			self.players.append(player)
			player.show()
		
			# update number of players
			self.updatePlayers()
		
			# 2 players minimum!
			if len(Game.get_players()) == 2:
				btnStart.set_sensitive(True)
		
			status = name + " entered the game"
			self.write(status)
		
	def removePlayer(self, name, active=False):
		btnComputer = self.wTree.get_widget("btnComputer")
		btnStart = self.wTree.get_widget("btnStart")
		
		if not active:
			gamestatus = Game.removePlayer(name)
			self.updatePlayers()
		else:
			# Player already about to be removed
			gamestatus = -1
		
		playerstatus = Players.unload(name)
		
		if playerstatus == -1: # if agent not loaded
			self.writeError("Error: Player "+name+" not found!")
			return
		
		for x in self.players:
			if x.name == name:
				player = x
				self.players.remove(x)
				break
		
		# 2 players min
		if len(Game.get_players()) < 2:
			btnStart.set_sensitive(False)
		
		if player.human:
			self.humans -= 1
		
		if gamestatus == 0:
			# print to status bar
			status = name + " left the game"
			self.write(status)
		
	def updatePlayers(self, players=None):
		if players == None:
			players = len(Game.get_players())
		
		self.lblNumPlayers.set_text(str(players))
		
	def updatePots(self):
		handPot, sabaccPot = Game.get_pots()
		self.lblHandPot.set_text(str(handPot))
		self.lblSabaccPot.set_text(str(sabaccPot))
		
		# show correct credits for all players
		for player in self.players:
			player.setCredits()
	
	def loadAgent(self, filename):
		status, name = Players.addXML(filename, self)
		error=None
		if status == -1: # name already taken
			error=["Error: A player called "+name+" is already loaded!", "Agent already loaded"]
		elif status == -2: # XML file not exist
			error=["Error: The file "+filename+" was not found!", "File not found"]
		elif status == -3: # XML error
			error=["Error loading file " +filename+".", "File error"]
		elif status == -4: # incompatible version
			error=["Error: Wrong SabaacAppXML version!", "Version error"]
		elif status == -5: # unknown agent type
			error=["Error: Unknown agent type.", "Type error"]
		
		
		if error != None:
			self.loadedName = ""
			# Workaround for GUI threading problem on Windows
			gobject.idle_add(self.loading.destroy)
			gobject.idle_add(self.writeError,error[0], error[1])
		else:
			self.loadedName = name
			try:
				# Workaround for GUI threading problem on Windows
				gobject.idle_add(self.loading.destroy)
			except AttributeError: # loading window already gone
				pass
		
		time.sleep(1)
		try:
			del(self.loadedName)
			del(self.loading)
		except:
			pass
	
	def showCards(self, cards, name):
		# find player by name
		for player in self.players:
			if player.name == name:
				# wndPlayer doesn't need name, but needs true or false
				player.showCards(cards, True)
				return 0
		else:
			return -1
	
	def playGame(self):
		Game.startGame(self.lastante)
		self.updatePots()
		
		status = []
		
		for player in self.players:
			if not player.human:
				status.append(player.agent.saveToXML(True))
			player.setStatus(0)
			# add losers back into game
			if player.agent not in Game.get_players():
				Game.addPlayer(player.name)
				self.write(player.name + " re-entered the game")
		
		msg = None
		
		if -1 in status:
			msg = ["Error: File did not write properly!", "Write error"]
		elif -2 in status:
			msg = ["I/O Error occurred while attempting to write file.", "I/O Error"]
		elif -3 in status:
			msg = ["Agent is of incorrect type!", "Type error"]
		elif -4 in status:
			msg = ["Wrong SabaacAppXML version!", "Version error"]
			
		if msg != None:
			self.writeError(msg[0], msg[1])
		
		btnStart = self.wTree.get_widget("btnStart")
		if len(Game.get_players()) >= 2:
			btnStart.set_sensitive(True)
	
	def endWait(self):
		if len(self.players) == 2:
			for player in self.players:
				if player.wait:
					player.makeMove(None, -3) # changes to a stick or minimum bet
					break
	
	def promptHumans(self):
	# Should we hide the humans from one another, or not?
		if self.humans >= 2:
			answer=True
		else:
			answer=False
		
		return answer
	
# Make object 'static'
_inst=wndGame()
def showMsgs():
	return _inst.showMsgs

write = _inst.write
show = _inst.show
addPlayer = _inst.addPlayer
removePlayer = _inst.removePlayer
endWait = _inst.endWait
updatePlayers = _inst.updatePlayers
updatePots = _inst.updatePots
promptHumans = _inst.promptHumans