# XMLAgent.py from Sabacc 0.6
#! This package has been obsoleted by sabacc.back.xml_tools
#! Please use that package instead of this one!

from XMLAgent import XMLAgent

class XMLRuleAgent (XMLAgent):
	def getRules(self):
		# Blank set of rules
		return [[], 0]

	def saveRules(self, rules):
		sys.stderr.write('Warning: back.XMLRuleAgent.saveRules: This method does nothing! Please use sabacc.back.xml_tools instead!\n')
		return 0

Rule = Condition = object
