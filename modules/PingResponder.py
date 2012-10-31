#!/usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader

class PingResponder(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="PingResponder"
		self.hooks=[ModuleBase.ModuleHook("PING", self.pingrespond)]
		print "PingResponder loaded"
	def pingrespond(self, args, prefix, trailing):
		# got a ping? send it right back
		self.bot.do_pingrespond(trailing)