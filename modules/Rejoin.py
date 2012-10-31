#!/usr/bin/env python
from botlibs import ModuleBase
import time

# Simple module for auto-rejoining a channel 30 seconds after being kicked

class Rejoin(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Rejoin"
		self.hooks=[ModuleBase.ModuleHook("KICK", self.rejoin)]
		self.loadConfig()
		
		print "Rejoin loaded"
	
	def rejoin(self, args, prefix, trailing):
		time.sleep(30)
		self.bot.do_join(args[0])