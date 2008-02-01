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
wndApp.py (taken from version 0.6beta1)
This module contains the wndApp class and methods to
call it without having to instantiate it first.
"""

import gtk, sys, os.path, gtk.glade

class wndApp (object):
	"""
	This class contains the main window of the application, from
	which the training and testing windows can be shown or the
	application can be quit.
	"""
	def __init__(self):
		from __init__ import gladefile
		self.windowname = "wndApp"
		self.wTree = gtk.glade.XML(gladefile,self.windowname)
		dic = {"kill_me": gtk.main_quit,
			"on_btnTrainNew_clicked": self.btnTrainNew_click,
			"on_btnTrainExist_clicked": self.btnTrainExist_click,
			"on_btnTest_clicked": self.showTest,
			"on_btnQuit_clicked": gtk.main_quit}
		self.wTree.signal_autoconnect(dic)
		
		self.window = self.wTree.get_widget("wndApp")
		
	def btnTrainNew_click(self,widget):
		self.showTrain(False)
		
	def btnTrainExist_click(self,widget):
		self.showTrain(True)
		
	def showTrain(self, exists):
		if exists:
			message = "Please select the agent file"
			action = gtk.FILE_CHOOSER_ACTION_OPEN
		else:
			message = "Create agent"
			action = gtk.FILE_CHOOSER_ACTION_SAVE
		
		# Create dialog
		d = gtk.FileChooserDialog(title=message, parent=self.window,
		action=action,
		buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
		gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
		d.set_do_overwrite_confirmation(True)
		
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
		d.set_current_folder(agentdir)
		
		# Show dialog
		resp=d.run()
		file = d.get_filename()
		d.destroy()
		if resp == gtk.RESPONSE_REJECT:
			file = ""
		
		if file != "":
			from wndTrain import wndTrain
			if exists:
				wndTrain(file)
			else:
				# if file already exists, delete it
				error = 0
				
				if os.path.exists(file):
					try:
						os.remove(file)
					except:
						error=-2
				
				if error == 0:
					# show 'create' dialog
					title = "Create agent"
					message = "Please choose your agent's characteristics:"
					createdialog = gtk.Dialog(title, self.window, gtk.DIALOG_MODAL,
						(gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
						gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
					mainLayout = gtk.VBox(spacing=10)
					msglabel = gtk.Label(message)
					mainLayout.add(msglabel)
					options = gtk.Table(3, 2)
					
					# labels
					lblName = gtk.Label("Name:")
					options.attach(lblName, 0, 1, 0, 1, xpadding=10, ypadding=5)
					lblType = gtk.Label("Type of Agent:")
					options.attach(lblType, 0, 1, 1, 2, xpadding=10, ypadding=5)
					lblLearning = gtk.Label("Learning Type: ")
					options.attach(lblLearning, 0, 1, 2, 3, xpadding=10, ypadding=5)
					
					# settings
					txtName = gtk.Entry()
					options.attach(txtName, 1, 2, 0, 1)
					typeLayout = gtk.HBox()
					btnRule = gtk.RadioButton(label="Rule-based Agent")
					typeLayout.add(btnRule)
					btnRL = gtk.RadioButton(btnRule, "Learning Agent")
					btnRL.set_sensitive(False)
					typeLayout.add(btnRL)
					options.attach(typeLayout, 1, 2, 1, 2)
					cmbLearning = gtk.combo_box_new_text()
					for text in ["WinLossAgent", "ScoreAgent", "GamblingAgent"]:
						cmbLearning.append_text(text)
					cmbLearning.set_sensitive(False)
					options.attach(cmbLearning, 1, 2, 2, 3)
					btnRule.connect("clicked", self.btnRule_click, cmbLearning)
					btnRL.connect("clicked", self.btnRL_click, cmbLearning)
					mainLayout.add(options)
					createdialog.vbox.set_spacing(10)
					createdialog.vbox.pack_start(mainLayout, True, True, 0)
					
					mainLayout.show_all()
					
					while True:
						resp = createdialog.run()
						
						if resp == gtk.RESPONSE_ACCEPT:
							# get values from input
							name=txtName.get_text()
							if btnRL.get_active():
								learning = True
								if cmbLearning.get_active_text() == "WinLossAgent":
									learningtype = 0
								elif cmbLearning.get_active_text() == "ScoreAgent":
									learningtype = 1
								elif cmbLearning.get_active_text() == "GamblingAgent":
									learningtype = 2
								else:
									learningtype = None
							elif btnRule.get_active():
								learning = False
								learningtype = -1
							else:
								learning = None
								learningtype = None
							
							if name != "" and learning != None and learningtype != None:
								break
							else:
								msglabel.set_text("Please fill in all fields!")
						else: # cancel
							break
					
					createdialog.destroy()
					
					if resp == gtk.RESPONSE_ACCEPT:
						from sabacc.back.XMLRuleAgent import XMLRuleAgent
						from sabacc.back.RuleBasedAgent import RuleBasedAgent
						xml = XMLRuleAgent(file)
						error = xml.createFile(name)
						agent = RuleBasedAgent(xml)
						
						if error == 0:
							wndTrain(agent)
						
					if error != 0:
						if error == -1:
							title = "File not found"
							text = "Error: The template file could not be found!"
						elif error == -2:
							title = "I/O Error"
							text = "An I/O error has occurred!"
						dialog = gtk.Dialog(title, self.window, gtk.DIALOG_MODAL,
							(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
						hbox = gtk.HBox()
						icon = gtk.Image()
						icon.set_from_stock(gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_DIALOG)
						label = gtk.Label(text)
						hbox.add(icon)
						hbox.add(label)
						dialog.vbox.pack_start(hbox, True, True, 0)
						dialog.show_all()
						dialog.run()
						dialog.destroy()

	def showTest(self, button):
		button.set_sensitive(False)
		import wndGame
		reload(wndGame)
		wndGame.show()
		
	def btnRule_click(self, widget, cmbLearning):
		if widget.get_active():
			cmbLearning.set_sensitive(False)
		
	def btnRL_click(self, widget, cmbLearning):
		if widget.get_active():
			cmbLearning.set_sensitive(True)
		
# Make object 'static'
_inst=wndApp()
showTrain = _inst.showTrain
showTest = _inst.showTest
wTree = _inst.wTree
window = _inst.window