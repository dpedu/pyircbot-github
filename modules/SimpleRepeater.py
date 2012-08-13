#! /usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader

class SimpleRepeater(ModuleBase.ModuleBase):
	def __init__(self, bot):
		# init hte base module
		ModuleBase.ModuleBase.__init__(self, bot);
		# the NAME of this module
		self.moduleName="SimpleRepeater"
		# hook our local method "repeat" to the "PRIVMSG" hook
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.repeat)]
		# let the user know we've loaded
		print "SimpleRepeater loaded"
	def repeat(self, args, prefix, trailing):
		# got a message? send it back!
		self.bot.do_privmsg(args[0], trailing);
		# debug info to console
		print "reapeat: args=%s t=%s" % (args, trailing)