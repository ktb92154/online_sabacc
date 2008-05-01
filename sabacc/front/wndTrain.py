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
wndTrain.py (taken from version 0.6 'Ackbar')
This module contains the wndTrain class.
"""

# import locals
import wndApp
from gtkPlayerInterface import gtkPlayerInterface

# import from back end
from sabacc.back import Players, Game
from sabacc.back.settings import NUM_MP_STATES, NUM_ACTIONS
from sabacc.back.XMLRuleAgent import Rule, Condition

import sys, os.path, threading, gtk, gobject
import gtk.glade

loaded_for_training = []
from __init__ import iconpath

class wndTrain (gtkPlayerInterface):
	"""
	This class contains the training window, where one particular
	agent may be trained against any other agents.
	
	Since the removal of the LearningAgent class, this class has
	become mostly obsolete, and is due to be replaced by a more
	functional 'agent status' class.
	"""
	def __init__(self, agent):
		gtkPlayerInterface.__init__(self)
		
		from __init__ import gladefile
		
		self.windowname = "wndTrain"
		self.wTree = gtk.glade.XML(gladefile,self.windowname)
		dic = {"on_wndTrain_delete": self.windowClosing,
			"on_btnData_clicked": self.btnData_click,
			"on_btnSaveStatus_clicked": self.btnSave_click,
			"on_btnRevert_clicked": self.btnRevert_click}
		self.wTree.signal_autoconnect(dic)
		
		btnTrain = self.wTree.get_widget("btnTrainStop")
		self.trainStopSig = btnTrain.connect("clicked", self.start_training)
		
		# all labels
		self.status_img = self.wTree.get_widget("imgStatus")
		self.status = self.wTree.get_widget("lblStatus")
		self.bombouts = self.wTree.get_widget("lblBombOuts")
		self.lost = self.wTree.get_widget("lblGamesLost")
		self.won = self.wTree.get_widget("lblGamesWon")
		self.played = self.wTree.get_widget("lblGamesPlayed")
		self.filename = self.wTree.get_widget("lblFilename")
		self.runs = self.wTree.get_widget("lblRunCount")
		self.puresabacc = self.wTree.get_widget("lblPureSabacc")
		
		self.window = self.wTree.get_widget("wndTrain")
		self.window.set_icon_from_file(iconpath)
		self.modified = False
		
		title = "Loading..."
		text = "Please wait. Loading data..."
		dialog = gtk.Dialog(title, wndApp.window, gtk.DIALOG_MODAL,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_DELETE_EVENT))
		label = gtk.Label(text)
		dialog.vbox.pack_start(label, True, True, 0)
		dialog.show_all()
		self.loading = dialog
		
		self.showwin = True
		t = threading.Thread(target=self.loadData, args=[agent], name="loadData")
		t.setDaemon(True)
		t.start()
		
		resp = dialog.run()
		
		if resp == gtk.RESPONSE_DELETE_EVENT: # 'cancel' clicked
			self.showwin = False
			dialog.destroy()
		
	def loadData(self, agent):
		if type(agent) == str:
			filename=agent
			agent=None
		else:
			filename=agent.XMLFile.filename
			
		if agent != None:
			if agent.loadFromXML() == -2: # file badly formatted
				# Workaround for GUI threading problem on Windows
				gobject.idle_add(self.writeError,"Error loading file " +filename+".", "File error", wndApp.window)
				gobject.idle_add(self.window.destroy)
				gobject.idle_add(self.loading.destroy)
				name = ""
			else:
				# add player to back end list
				agent.interface = self
				status = Players.addLoaded(agent)
				name = agent.name
				
				if status != 0: # name already taken
					# Workaround for GUI threading problem on Windows
					gobject.idle_add(self.writeError,"Error: A player called "+name+" is already loaded!", "Agent already loaded", wndApp.window)
					gobject.idle_add(self.window.destroy)
					gobject.idle_add(self.loading.destroy)
					name = ""
			
			if name != "":
				self.agent = agent
		else:
			# load player
			status, name = Players.addXML(filename, self)
			errors=None
			if status == -1: # name already taken
				errors=["Error: A player called "+name+" is already loaded!", "Agent already loaded"]
			elif status == -2: # XML file not exist
				errors=["Error: The file "+filename+" was not found!", "File not found"]
			elif status == -3: # XML error
				errors=["Error loading file " +filename+".", "File error"]
			elif status == -4: # incompatible version
				errors=["Wrong SabaacAppXML version!", "Version error"]
			elif status == -5: # unknown agent type
				errors=["Error: Unknown agent type.", "Type error"]
			
			if errors != None:
				# Workaround for GUI threading problem on Windows
				gobject.idle_add(self.window.destroy)
				gobject.idle_add(self.loading.destroy)
				gobject.idle_add(self.writeError,errors[0], errors[1], wndApp.window)
				name = ""
			else:
				for x in Players.loaded:
					if x.name == name:
						self.agent = x
						break
				else:
					name = ""
		
		if self.showwin:
			# Workaround for GUI threading problem on Windows
			gobject.idle_add(self.loading.destroy)
			if name != "":
				loaded_for_training.append(self.agent)
				self.name = name
				self.window.set_title(name)
				self.status.set_label(" (inactive)")
				self.runs.set_label("0")
				self.filename.set_label(os.path.basename(filename))
				
				# set agent variables
				self.setVars()
				gobject.idle_add(self.window.show)
		elif name != "":
			Players.unload(name)
		
		del(self.showwin)
		del(self.loading)
		
	def windowClosing(self, widget, event):
		if self.modified:
			title = "Save Changes?"
			text = "The current agent has been modified. Do you want to save changes?"
			dialog = gtk.Dialog(title, self.window, gtk.DIALOG_MODAL,
				(gtk.STOCK_YES, gtk.RESPONSE_ACCEPT,
				gtk.STOCK_NO, gtk.RESPONSE_REJECT,
				gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
			hbox = gtk.HBox()
			icon = gtk.Image()
			icon.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
			label = gtk.Label(text)
			hbox.add(icon)
			hbox.add(label)
			dialog.vbox.pack_start(hbox, True, True, 0)
			dialog.show_all()
			resp = dialog.run()
			dialog.destroy()
			if resp == gtk.RESPONSE_ACCEPT: # yes
				self.btnSave_click()
				final = False
			elif resp == gtk.RESPONSE_REJECT: # no
				final = False
			else: # cancel
				final = True
		else:
			final = False
		
		if not final:
			if self.active:
				self.stop_training()
			# unload agent
			Players.unload(self.name)
			loaded_for_training.remove(self.agent)
		return final
		
	def start_training(self, button):
		if len(loaded_for_training) > 1:
			# question dialog
			title="Train Agents"
			text = "Please select the agents to train..."
			dialog = gtk.Dialog(title, self.window, gtk.DIALOG_MODAL,
				(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
				gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
			dialog.set_default_size(-1, 300)
			dialog.vbox.set_spacing(10)
			label = gtk.Label(text)
			dialog.vbox.pack_start(label, False, False, 0)
			sc = gtk.ScrolledWindow()
			sc.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
			data = gtk.ListStore(str)
			for agent in loaded_for_training:
				if agent.name != self.name:
					data.append([agent.name])
			
			tv = gtk.TreeView(data)
			tvc=gtk.TreeViewColumn("Agent Name")
			cell=gtk.CellRendererText()
			tvc.pack_start(cell)
			tvc.set_attributes(cell, text=0)
			tv.append_column(tvc)
			selection = tv.get_selection()
			selection.set_mode(gtk.SELECTION_MULTIPLE)
			sc.add_with_viewport(tv)
			dialog.vbox.pack_start(sc, True, True, 0)
			
			hbox = gtk.HBox()
			lblRuns = gtk.Label("Runs: ")
			hbox.add(lblRuns)
			adj = gtk.Adjustment(100, 1, 65535, 100)
			spbRuns = gtk.SpinButton(adj, digits=0)
			spbRuns.set_numeric(True)
			spbRuns.set_update_policy(gtk.UPDATE_IF_VALID)
			hbox.add(spbRuns)
			dialog.vbox.pack_start(hbox, False, False, 0)
			dialog.show_all()
			
			cont=True
			while True:
				playernames=[self.name]
				resp = dialog.run()
				if resp == gtk.RESPONSE_ACCEPT:
					rows = selection.get_selected_rows()[1]
					runs = int(spbRuns.get_value())
					for x in rows:
						row=x[0]
						playernames.append(data[row][0])
					if len(playernames) > 1:
						break
					else:
						label.set_text("Please select at least one player!")
				else:
					cont=False
					break
			dialog.destroy()
			
			if cont:
				status = Game.reset()
				if status == 0:
					# Set variables and add players to game
					for agent in loaded_for_training:
						if agent.name in playernames:
							agent.interface.joinGame()
					
					# Play game in other thread
					t = threading.Thread(target=self.playGame, args=[runs], name="playGame")
					t.setDaemon(True)
					t.start()
				else:
					self.writeError("Error: Game in progress. Please try again later.", "Game in progress")
		else:
			self.writeError("Not enough players are loaded!", "Not enough players")
	
	def stop_training(self, button=None):
		if Game.get_gameInProgress():
			Game.endGame(False)
		
		for agent in Game.get_players():
			agent.interface.leaveGame()
		
		Game.reset()
	
	def btnData_click(self,widget):
		# is agent RL or rule based?
		if "RuleBasedAgent" in str(type(self.agent)):
			learning = False
		else:
			learning = True
		
		datawindow = gtk.Window()
		datawindow.set_icon_from_file(iconpath)
		datawindow.set_title("Agent Data")
		datawindow.set_modal(True)
		datawindow.set_transient_for(self.window)
		datawindow.set_default_size(-1, 300)
		mainLayout = gtk.VBox()
		lblName = gtk.Label("Name: "+self.name)
		mainLayout.pack_start(lblName, False, False, 0)
		btnOK = gtk.Button(stock=gtk.STOCK_OK)
		
		if learning: # LearningAgent settings
			## change these!
			lower = -1.0
			upper = 1.0
			
			line = gtk.HSeparator()
			mainLayout.pack_start(line, False, False, 0)
			bombLayout = gtk.HBox()
			lblBomb = gtk.Label("Bomb Threshold:")
			bombLayout.add(lblBomb)
			adj = gtk.Adjustment(self.agent.bombthreshold, 0.0, 1.0, 0.001)
			spbBomb = gtk.SpinButton(adj, digits=3)
			spbBomb.set_numeric(True)
			spbBomb.set_update_policy(gtk.UPDATE_IF_VALID)
			spbBomb.connect("value-changed", self.valueChanged, btnOK)
			bombLayout.add(spbBomb)
			mainLayout.pack_start(bombLayout, False, False, 0)
			probLayout = gtk.HBox()
			lblProb = gtk.Label("Probability Threshold:")
			probLayout.add(lblProb)
			adj = gtk.Adjustment(self.agent.probthreshold, 0.0, 1.0, 0.001)
			spbProb = gtk.SpinButton(adj, digits=3)
			spbProb.set_numeric(True)
			spbProb.set_update_policy(gtk.UPDATE_IF_VALID)
			spbProb.connect("value-changed", self.valueChanged, btnOK)
			probLayout.add(spbProb)
			mainLayout.pack_start(probLayout, False, False, 0)
		
		sc = gtk.ScrolledWindow()
		sc.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
		
		if learning:
			data = gtk.ListStore(int, int, float, float, float)
			
			for state in range(NUM_MP_STATES):
				visited = self.agent.visited[state]
				value = self.agent.value[state]
				data.append([state, visited]+value)
		else:
			# create ruledata list
			self.ruledata = []
			data = gtk.ListStore(str, str)
			
			for rule in self.agent.rules:
				n = rule.name
				t = rule.type
				conditions = gtk.ListStore(str, int)
				for cond in rule.conditions:
					conditions.append([cond.function, cond.score])
				actions = gtk.ListStore(int)
				for action in rule.actions:
					actions.append([action])
				self.ruledata.append([n, t, conditions, actions])
			
				if n != "default": # default rule dealt with elsewhere
					data.append([n, t])
			
		tv = gtk.TreeView(data)
		
		if learning:
			i=0
			for text in ["State", "Visited", "Draw Value", "Stick Value", "Call Value"]:
				tvc=gtk.TreeViewColumn(text)
				if i >= 2: # states
					adj = gtk.Adjustment(0.0, lower, upper, 0.001)
					cell=gtk.CellRendererSpin()
					cell.set_property("adjustment", adj)
					cell.set_property("climb-rate", 0.001)
					cell.set_property("digits", 3)
					cell.set_property("editable", True)
					cell.connect("edited", self.cell_edit_rl, data, i, btnOK)
				else:
					cell=gtk.CellRendererText()
				tvc.pack_start(cell)
				tvc.set_attributes(cell, text=i)
				tv.append_column(tvc)
				i+=1
		else:
			andormodel = gtk.ListStore(str)
			andormodel.append(["and"])
			andormodel.append(["or"])
			for text in ["Rule Name", "Rule Type"]:
				tvc=gtk.TreeViewColumn(text)
				if text == "Rule Type":
					cell=gtk.CellRendererCombo()
					cell.set_property("editable", True)
					cell.set_property("has-entry", True)
					cell.set_property("text-column", 0)
					cell.set_property("model", andormodel)
					cell.connect("edited", self.cell_edit_rule, data, btnOK)
					i=1
				else:
					cell=gtk.CellRendererText()
					i=0
				tvc.pack_start(cell)
				tvc.set_attributes(cell, text=i)
				tv.append_column(tvc)
			
		sc.add_with_viewport(tv)
		mainLayout.pack_start(sc, True, True, 0)
		
		if not learning:
			selection=tv.get_selection()
			rulebuttons = gtk.HButtonBox()
			btnAdd = gtk.Button("Add New Rule")
			btnAdd.connect("clicked", self.editRule, datawindow, btnOK, data)
			addIcon = gtk.Image()
			addIcon.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
			btnAdd.set_image(addIcon)
			btnEdit = gtk.Button("Edit Rule")
			editIcon = gtk.Image()
			editIcon.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_BUTTON)
			btnEdit.set_image(editIcon)
			btnEdit.set_sensitive(False)
			btnEdit.connect("clicked", self.editRule, datawindow, btnOK, selection)
			btnDelete = gtk.Button("Delete Rule")
			deleteIcon = gtk.Image()
			deleteIcon.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_BUTTON)
			btnDelete.set_image(deleteIcon)
			btnDelete.set_sensitive(False)
			btnDelete.connect("clicked", self.delElem, selection, datawindow, btnOK, "rule")
			selection.connect("changed", self.item_select, btnEdit, btnDelete)
			
			for w in [btnAdd, btnEdit, btnDelete]:
				rulebuttons.add(w)
			mainLayout.pack_start(rulebuttons, False, False, 0)
		
		buttonbox = gtk.HButtonBox()
		btnOK.set_sensitive(False)
		btnOK.connect("clicked", self.data_destroy, datawindow, True)
		buttonbox.add(btnOK)
		
		if not learning:
			btnDefault = gtk.Button("Edit Default Rule")
			editIcon = gtk.Image()
			editIcon.set_from_stock(gtk.STOCK_EDIT, gtk.ICON_SIZE_BUTTON)
			btnDefault.set_image(editIcon)
			btnDefault.connect("clicked", self.editRule, datawindow, btnOK, selection, True)
			buttonbox.add(btnDefault)
		
		btnCancel = gtk.Button(stock=gtk.STOCK_CANCEL)
		btnCancel.connect("clicked", self.data_destroy, datawindow)
		buttonbox.add(btnCancel)
		mainLayout.pack_start(buttonbox, False, False, 0)
		datawindow.add(mainLayout)
		datawindow.show_all()
		
	def btnSave_click(self, btnSave=None):
		status = self.agent.saveToXML()
		
		if status == -1:
			msg = ["Error: File did not write properly!", "Write error"]
		elif status == -2:
			msg = ["I/O Error occurred while attempting to write file.", "I/O Error"]
		elif status == -3:
			msg = ["Agent is of incorrect type!", "Type error"]
		elif status == -4:
			msg = ["Wrong SabaacAppXML version!", "Version error"]
		
		if status < 0:
			self.writeError(msg[0], msg[1], self.window)
		else:
			btnRevert = self.wTree.get_widget("btnRevert")
			if btnSave != None:
				btnSave.set_sensitive(False)
				btnRevert.set_sensitive(False)
			self.modified = False
		
	def btnRevert_click(self, btnRevert):
		status = self.agent.loadFromXML()
		
		if status == -1:
			msg = ["Error: File no longer exists!", "File not found"]
		elif status == -2:
			msg = ["Error loading file.", "File error"]
		elif status == -3:
			msg = ["Agent is of incorrect type!", "Type error"]
		elif status == -4:
			msg = ["Wrong SabaacAppXML version!", "Version error"]
		
		if status < 0:
			self.writeError(msg[0], msg[1], self.window)
		else:
			btnSave = self.wTree.get_widget("btnSaveStatus")
			btnSave.set_sensitive(False)
			btnRevert.set_sensitive(False)
			self.modified = False
			self.setVars()
	
	def setVars(self):
		self.played.set_label(str(self.agent.played))
		self.won.set_label(str(self.agent.won))
		self.lost.set_label(str(self.agent.lost))
		self.bombouts.set_label(str(self.agent.bombouts))
		self.puresabacc.set_label(str(self.agent.pureSabacc))
		
	def data_destroy(self, widget, datawindow, update=False):
		if update: # ok button clicked, else cancel clicked
			# learning or not?
			if "RuleBasedAgent" in str(type(self.agent)):
				rules = []
				for rule in self.ruledata:
					thisrule = Rule()
					thisrule.name = rule[0]
					thisrule.type = rule[1]
					for cond in rule[2]:
						newcond = Condition()
						newcond.function = cond[0]
						newcond.score = cond[1]
						thisrule.conditions.append(newcond)
					for action in rule[3]:
						thisrule.actions.append(action[0])
					rules.append(thisrule)
				self.agent.rules = rules
				
				del(self.ruledata)
			else:
				mainlayout=datawindow.get_children()[0]
				bomblayout=mainlayout.get_children()[2]
				bombthreshold=float(bomblayout.get_children()[1].get_text())
				if bombthreshold != self.agent.bombthreshold:
					self.agent.bombthreshold=bombthreshold
				
				problayout=mainlayout.get_children()[3]
				probthreshold=float(problayout.get_children()[1].get_text())
				if probthreshold != self.agent.probthreshold:
					self.agent.probthreshold=probthreshold
				scroller=mainlayout.get_children()[4]
				tree=scroller.get_children()[0].get_children()[0]
				data = tree.get_model()
				for state in range(NUM_MP_STATES):
					statevalues=[]
					for action in range(NUM_ACTIONS):
						statevalues.append(data[state][action+2])
					if statevalues != self.agent.value[state]:
						self.agent.value[state]=statevalues
			# enable save and revert buttons
			btnSave = self.wTree.get_widget("btnSaveStatus")
			btnRevert = self.wTree.get_widget("btnRevert")
			btnSave.set_sensitive(True)
			btnRevert.set_sensitive(True)
			self.modified = True
		
		datawindow.destroy()
		
	def valueChanged(self, widget, btnOK):
		btnOK.set_sensitive(True)
		
	def cell_edit_rl(self, cell, path, new_text, data, col_num, btnOK):
		row=data[path]
		original = float(row[col_num])
		try:
			new_num = float(new_text)
		except ValueError: # value of wrong type
			new_num=original
		
		if original != new_num:
			row[col_num]=new_num
			btnOK.set_sensitive(True)
	
	def cell_edit_rule(self, cell, path, new_text, data, btnOK):
		row=data[path]
		original=row[1]
		
		if original != new_text and new_text in ["and", "or"]:
			row[1]=new_text
			btnOK.set_sensitive(True)
			
	def editRule(self, widget, window, parent_OK, selected, default=False):
		if default:
			name="default"
		elif type(selected)!=gtk.TreeSelection:
			# question dialog
			title="Create Rule"
			text = "Please enter the name of the rule:"
			dialog = gtk.Dialog(title, window, gtk.DIALOG_MODAL,
				(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
				gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
			hbox = gtk.HBox()
			icon = gtk.Image()
			icon.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
			hbox.add(icon)
			vbox=gtk.VBox(spacing=10)
			label = gtk.Label(text)
			vbox.add(label)
			entry=gtk.Entry()
			vbox.add(entry)
			hbox.add(vbox)
			dialog.vbox.pack_start(hbox, True, True, 0)
			dialog.show_all()
			while True:
				resp = dialog.run()
				if resp == gtk.RESPONSE_ACCEPT:
					name = entry.get_text()
					ruletype = ""
					if name == "default":
						self.writeError("Error: The name 'default' is reserved.", "Reserved name", window)
					else:
						break
				else:
					name = ""
					break
			dialog.destroy()
		else:
			data, row = selected.get_selected()
			name, ruletype=data.get(row, 0, 1)
		
		if name != "":
			rulewindow = gtk.Window()
			rulewindow.set_icon_from_file(iconpath)
			rulewindow.set_title("Rule Data")
			rulewindow.set_modal(True)
			rulewindow.set_transient_for(window)
			rulewindow.set_default_size(-1, 250)
			mainLayout = gtk.VBox()
			nameLayout = gtk.HBox()
			lblName1 = gtk.Label("Rule Name: ")
			nameLayout.add(lblName1)
			lblName2 = gtk.Label(name)
			nameLayout.add(lblName2)
			mainLayout.pack_start(nameLayout, False, False, 0)
			btnOK = gtk.Button(stock=gtk.STOCK_OK)
			
			if not default:
				line = gtk.HSeparator()
				mainLayout.pack_start(line, False, False, 0)
				typeLayout = gtk.HBox()
				lblType = gtk.Label("Type:")
				typeLayout.add(lblType)
				cmbType = gtk.combo_box_new_text()
				cmbType.append_text("and")
				cmbType.append_text("or")
				cmbType.connect("changed", self.valueChanged, btnOK)
				if ruletype == "and":
					cmbType.set_active(0)
				elif ruletype == "or":
					cmbType.set_active(1)
				typeLayout.add(cmbType)
				mainLayout.pack_start(typeLayout, False, False, 0)
			
			sc = gtk.ScrolledWindow()
			sc.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
			scrolledlayout = gtk.HBox()
			
			if not default:
				# find conditions list
				conditions = gtk.ListStore(str, int)
				
				for rule in self.ruledata:
					if rule[0] == name:
						for row in rule[2]:
							conditions.append(row)
						break
					
				
				condtv = gtk.TreeView(conditions)
				fnmodel = gtk.ListStore(str)
				fnmodel.append([">"])
				fnmodel.append(["<"])
				fnmodel.append(["="])
				for text in ["Function", "Score"]:
					tvc=gtk.TreeViewColumn(text)
					if text == "Function":
						cell=gtk.CellRendererCombo()
						cell.set_property("has-entry", True)
						cell.set_property("text-column", 0)
						cell.set_property("model", fnmodel)
						i=0
					else:
						cell=gtk.CellRendererText()
						i=1
					cell.set_property("editable", True)
					cell.connect("edited", self.cell_edit_cond, conditions, i, btnOK)
					
					tvc.pack_start(cell)
					tvc.set_attributes(cell, text=i)
					condtv.append_column(tvc)
			
				scrolledlayout.pack_start(condtv, True, True, 0)
				line=gtk.VSeparator()
				scrolledlayout.pack_start(line, False, False, 0)
			
			# find actions list
			actions = gtk.ListStore(int)
			
			for rule in self.ruledata:
				if rule[0] == name:
					for row in rule[3]:
						actions.append(row)
					break
			
			actv = gtk.TreeView(actions)
			tvc = gtk.TreeViewColumn("Action")
			acmodel = gtk.ListStore(str)
			acmodel.append([0])
			acmodel.append([1])
			acmodel.append([2])
			cell=gtk.CellRendererCombo()
			cell.set_property("has-entry", True)
			cell.set_property("text-column", 0)
			cell.set_property("model", acmodel)
			cell.set_property("editable", True)
			cell.connect("edited", self.cell_edit_ac, actions, btnOK)
			tvc.pack_start(cell)
			tvc.set_attributes(cell, text=0)
			actv.append_column(tvc)
			scrolledlayout.pack_start(actv, True, True, 0)
			
			sc.add_with_viewport(scrolledlayout)
			mainLayout.pack_start(sc, True, True, 0)
			
			addbuttons = gtk.HButtonBox()
			
			if not default:
				addIcon = gtk.Image()
				addIcon.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
				btnAddCond = gtk.Button("New Condition")
				btnAddCond.connect("clicked", self.newCond, rulewindow, btnOK, conditions)
				btnAddCond.set_image(addIcon)
				addbuttons.add(btnAddCond)
			
			addIcon = gtk.Image()
			addIcon.set_from_stock(gtk.STOCK_ADD, gtk.ICON_SIZE_BUTTON)
			btnAddAc = gtk.Button("New Action")
			btnAddAc.connect("clicked", self.newAc, rulewindow, btnOK, actions)
			btnAddAc.set_image(addIcon)
			addbuttons.add(btnAddAc)
			mainLayout.pack_start(addbuttons, False, False, 0)
			
			delbuttons = gtk.HButtonBox()
			
			if not default:
				condselection=condtv.get_selection()
				delIcon = gtk.Image()
				delIcon.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_BUTTON)
				btnDelCond = gtk.Button("Remove Condition")
				btnDelCond.connect("clicked", self.delElem, condselection, rulewindow, btnOK, "condition")
				btnDelCond.set_image(delIcon)
				btnDelCond.set_sensitive(False)
				delbuttons.add(btnDelCond)
				condselection.connect("changed", self.item_select, btnDelCond)
			
			acselection=actv.get_selection()
			delIcon = gtk.Image()
			delIcon.set_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_BUTTON)
			btnDelAc = gtk.Button("Remove Action")
			btnDelAc.connect("clicked", self.delElem, acselection, rulewindow, btnOK, "action")
			btnDelAc.set_image(delIcon)
			btnDelAc.set_sensitive(False)
			delbuttons.add(btnDelAc)
			acselection.connect("changed", self.item_select, btnDelAc)
			mainLayout.pack_start(delbuttons, False, False, 0)
			
			buttonbox = gtk.HButtonBox()
			btnOK.set_sensitive(False)
			btnOK.connect("clicked", self.rule_destroy, rulewindow, True, default, selected, parent_OK)
			buttonbox.add(btnOK)
			btnCancel = gtk.Button(stock=gtk.STOCK_CANCEL)
			btnCancel.connect("clicked", self.rule_destroy, rulewindow)
			buttonbox.add(btnCancel)
			mainLayout.pack_start(buttonbox, False, False, 0)
			
			rulewindow.add(mainLayout)
			rulewindow.show_all()
		
	def delElem(self, button, selected, window, btnOK, elemtype):
		data, row = selected.get_selected()
		if elemtype in ["rule", "action"]:
			name=data.get(row, 0)[0]
		elif elemtype == "condition":
			function, score = data.get(row, 0, 1)
			name = "If score "+function+" "+str(score)+":"
		
		# question dialog
		title="Delete rule"
		text = "Are you sure you want to delete the "+elemtype+" '"+str(name)+"'?"
		dialog = gtk.Dialog(title, window, gtk.DIALOG_MODAL,
			(gtk.STOCK_YES, gtk.RESPONSE_ACCEPT,
			gtk.STOCK_NO, gtk.RESPONSE_REJECT))
		hbox = gtk.HBox()
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
		label = gtk.Label(text)
		hbox.add(icon)
		hbox.add(label)
		dialog.vbox.pack_start(hbox, True, True, 0)
		dialog.show_all()
		resp = dialog.run()
		dialog.destroy()
		if resp == gtk.RESPONSE_ACCEPT:
			# remove element from list
			if elemtype == "rule":
				for rule in self.ruledata:
					if rule[0] == name:
						self.ruledata.remove(rule)
						break
			data.remove(row)
			btnOK.set_sensitive(True)
	
	def item_select(self, selected, button1, button2=None):
		iter = selected.get_selected()[1]
		if type(iter) != gtk.TreeIter:
			sensitive = False
		else:
			sensitive = True
		
		button1.set_sensitive(sensitive)
		if type(button2) == gtk.Button:
			button2.set_sensitive(sensitive)
	
	def rule_destroy(self, widget, window, update=False, default = False, selected = None, btnOK=None):
		destroy=True
		if update: # ok button clicked, else cancel clicked
			mainlayout=window.get_children()[0]
			namelayout = mainlayout.get_children()[0]
			name = namelayout.get_children()[1].get_text()
			if default:
				selected = None
				ruletype = "default"
				scroller=mainlayout.get_children()[1]
				trees=scroller.get_children()[0].get_children()[0].get_children()
				conditions = []
				actions = trees[0].get_model()
			else:
				typelayout=mainlayout.get_children()[2]
				ruletype=typelayout.get_children()[1].get_active_text()
			
				if ruletype == None:
					self.writeError("Please select a rule type!", parent=window)
					destroy=False
				
				scroller=mainlayout.get_children()[3]
				trees=scroller.get_children()[0].get_children()[0].get_children()
				condmodel = trees[0].get_model()
				acmodel = trees[2].get_model()
				
				conditions = []
				for rowmodel in condmodel:
					row = []
					for cell in rowmodel:
						row.append(cell)
					conditions.append(row)
				
				actions = []
				for row in acmodel:
					actions.append([row[0]])
		if destroy:
			if update:
				btnOK.set_sensitive(True)
				# edit rule in list or add new rule
				for rule in self.ruledata:
					if rule[0] == name:
						rule[1] = ruletype
						rule[2] = conditions
						rule[3] = actions
						break
				else:
					self.ruledata.append([name, ruletype, conditions, actions])
				
				if type(selected) == gtk.ListStore:
					data = selected
					data.append([name, ruletype])
				elif type(selected) == gtk.TreeSelection:
					data, row = selected.get_selected()
					data.set(row, 1, ruletype)
				
			window.destroy()
		
	def cell_edit_ac(self, cell, path, new_text, data, btnOK):
		row=data[path]
		original=int(row[0])
		
		try:
			new_int = int(new_text)
		except ValueError:
			new_int = original
		
		if new_int != original and new_int in [0, 1, 2]:
			row[0] = new_int
			btnOK.set_sensitive(True)
	
	def cell_edit_cond(self, cell, path, new_text, data, col_num, btnOK):
		row=data[path]
		original=row[col_num]
		
		if col_num == 0: # function
			if original != new_text and new_text in [">", "<", "="]:
				row[0] = new_text
				btnOK.set_sensitive(True)
		elif col_num == 1: # score
			original = int(original)
			try:
				new_text = int(new_text)
			except ValueError:
				new_text = original
			
			if original != new_text:
				row[1] = new_text
				btnOK.set_sensitive(True)
		
	def newCond(self, widget, window, btnOK, data):
		# question dialog
		title="Create Condition"
		text = "Please enter the condition details:"
		dialog = gtk.Dialog(title, window, gtk.DIALOG_MODAL,
			(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
			gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
		hbox = gtk.HBox()
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
		hbox.add(icon)
		vbox=gtk.VBox(spacing=10)
		label = gtk.Label(text)
		vbox.add(label)
		details = gtk.HBox()
		l1 = gtk.Label("If score ")
		details.pack_start(l1, False, False, 0)
		combo = gtk.combo_box_new_text()
		for input in [">", "<", "="]:
			combo.append_text(input)
		details.pack_start(combo, False, False, 0)
		entry = gtk.Entry()
		details.pack_start(entry, False, False, 0)
		l2 = gtk.Label(":")
		details.pack_start(l2, False, False, 0)
		vbox.add(details)
		hbox.add(vbox)
		dialog.vbox.pack_start(hbox, True, True, 0)
		dialog.show_all()
		while True:
			resp = dialog.run()
			if resp == gtk.RESPONSE_ACCEPT:
				function = combo.get_active_text()
				score = entry.get_text()
				if function == None:
					self.writeError("Please select a function!", parent=window)
				elif score == "":
					self.writeError("Please enter a score!", parent=window)
				else:
					try:
						score = int(score)
						data.append([function, score])
						btnOK.set_sensitive(True)
						break
					except ValueError:
						self.writeError("Score must be an integer!", parent=window)
			else:
				break
		dialog.destroy()
	
	def newAc(self, widget, window, btnOK, data):
		# question dialog
		title="Create Action"
		text = "Please select the action number:"
		dialog = gtk.Dialog(title, window, gtk.DIALOG_MODAL,
			(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
			gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
		hbox = gtk.HBox()
		icon = gtk.Image()
		icon.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_DIALOG)
		hbox.add(icon)
		vbox=gtk.VBox(spacing=10)
		label = gtk.Label(text)
		vbox.add(label)
		combo = gtk.combo_box_new_text()
		for num in range(3):
			combo.append_text(str(num))
		vbox.add(combo)
		hbox.add(vbox)
		dialog.vbox.pack_start(hbox, True, True, 0)
		dialog.show_all()
		while True:
			resp = dialog.run()
			if resp == gtk.RESPONSE_ACCEPT:
				action = combo.get_active_text()
				if action != None:
					data.append([int(action)])
					btnOK.set_sensitive(True)
					break
				else:
					self.writeError("Please select an action!", parent=window)
			else:
				break
		dialog.destroy()
	
	def joinGame(self):
		self.active = True
		self.status_img.set_from_stock(gtk.STOCK_YES, gtk.ICON_SIZE_BUTTON)
		self.status.set_label(" (active)")
		self.runs.set_label("0")
		btnTrainStop = self.wTree.get_widget("btnTrainStop")
		btnTrainStop.set_label("Stop Training")
		imgStop = gtk.Image()
		imgStop.set_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_BUTTON)
		btnTrainStop.set_image(imgStop)
		btnTrainStop.disconnect(self.trainStopSig)
		self.trainStopSig = btnTrainStop.connect("clicked", self.stop_training)
		
		for text in ["btnSaveStatus", "btnRevert", "btnData"]:
			widget = self.wTree.get_widget(text)
			widget.set_sensitive(False)
			
		Game.addPlayer(self.name, True)
	
	def leaveGame(self):
		self.active = False
		self.status_img.set_from_stock(gtk.STOCK_NO, gtk.ICON_SIZE_BUTTON)
		self.status.set_label(" (inactive)")
		btnTrainStop = self.wTree.get_widget("btnTrainStop")
		btnTrainStop.set_label("Train Agent")
		imgTrain = gtk.Image()
		imgTrain.set_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_BUTTON)
		btnTrainStop.set_image(imgTrain)
		btnTrainStop.disconnect(self.trainStopSig)
		self.trainStopSig = btnTrainStop.connect("clicked", self.start_training)
		
		for text in ["btnSaveStatus", "btnRevert", "btnData"]:
			widget = self.wTree.get_widget(text)
			widget.set_sensitive(True)
		self.modified=True
		
		self.setVars()
	
	def playGame(self, runs):
		players = Game.get_players()
		
		playertext = "\t"
		for player in players:
			playertext += player.name+"\tScore\t"
		
		for i in range(runs):
			if not self.active:
				break
			for agent in players:
				agent.interface.runs.set_text(str(i+1))
				# add losers back into game
				if agent not in Game.get_players():
					Game.addPlayer(agent.name, True)
			# play a game
			Game.startGame()
			
			# add losers back into game
			for agent in players:
				if agent not in Game.get_players():
					Game.addPlayer(agent.name, True)
		
		self.errors = False
		
		if self.active:
			self.stop_training()
	
	def make_inactive(self):
		self.stop_training()
