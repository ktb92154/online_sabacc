# Agent.py from Sabacc 0.6
#! This package has been rewritten as sabacc.back.Agents
#! Please use that package instead of this one!

from sabacc.back import Agents
import sys

class Agent(Agents.HumanAgent):
	def modCredits(self, credits):
		self.credits += credits