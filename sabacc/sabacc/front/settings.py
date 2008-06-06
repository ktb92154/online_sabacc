#! This whole file is a dirty hack, used just for testing purposes.
#! Some day a REAL settings.py will be created that actually loads
#! settings from a config file or something.

from front import basedir#!
import os.path
agent_dir = os.path.join(basedir, 'agents')
rulesets = 'bold cautious balanced'.split()