# AgentFromXML.py from Sabacc 0.6
#! This package has been rewritten as sabacc.back.Agents
#! Please use that package instead of this one!

from sabacc.back import Agents
import sys

class AgentFromXML(Agents.RuleBasedAgent):
	def __init__(self, XMLFile, interface=None):
		Agents.RuleBasedAgent.__init__(self, XMLFile.filename, interface)
		
		# Empty stats so Sabacc doesn't crash
		self.played = self.won = self.lost = self.bombouts = self.pureSabacc = 0
	
	def modCredits(self, credits):
		self.credits += credits
