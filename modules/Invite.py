#!/usr/bin/env python
from botlibs import ModuleBase

# Module for accepting (whitelisted) invitesx

class Invite(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Invite"
		self.hooks=[ModuleBase.ModuleHook("INVITE", self.invited)]
		self.loadConfig()
		
		print "Invite loaded"
	
	def invited(self, args, prefix, trailing):
		if self.config["whitelist-enabled"] and trailing.lower() in self.config["whitelist"]:
			self.bot.do_join(trailing)
			print "Invited to %s by %s" % (prefix, args[0])
		elif not self.config["whitelist-enabled"]:
			self.bot.do_join(trailing)
			print "Invited to %s by %s" % (prefix, args[0])
		else:
			print "Invited to %s by %s, but channel was not in our whitelist." % (prefix, args[0])

