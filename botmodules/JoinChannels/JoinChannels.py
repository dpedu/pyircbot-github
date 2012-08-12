#! /usr/bin/env python
from botlibs import ModuleBase

class JoinChannels(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="JoinChannels"
		self.hooks=[ModuleBase.ModuleHook("001", self.joinChannels)]
		self.loadConfig()
		self.properties = {}
		print "JoinChannels loaded"
	def joinChannels(self, args, prefix, trailing):
		# just join every channel in the config file
		for channel in self.config["channels"]:
			self.bot.do_join(channel)