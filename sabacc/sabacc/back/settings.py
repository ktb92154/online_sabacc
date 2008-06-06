#! This whole file is a dirty hack, used just for testing purposes.
#! Some day a REAL settings.py will be created that actually loads
#! settings from a config file or something.

## Do we need a 'constants' file as well, or are the OK here?
moves = dict(draw=0, stick=1, move_call=2, fold=-1, bet_call=-2)

rule_sets = {'bold': dict(upper=18, lower=-18),
	'cautious': dict(upper=12, lower=-12),
	'balanced': dict(upper=15, lower=-15)}
		
## Better names, maybe?
LOWEST_XML_VERSION = 1