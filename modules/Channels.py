#! /usr/bin/env python
from botlibs import ModuleBase,SimpleConfigReader

class Channels(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="Channels"
		self.hooks=[
			ModuleBase.ModuleHook("JOIN", self.user_joined),
			ModuleBase.ModuleHook("PART", self.user_parted)
		]
		self.properties = {}
		print "Channels loaded"
	def user_joined(self, args, prefix, trailing):
		nick = self.bot.extract_nick_from_prefix(prefix)
		print "Channels: user %s joined %s" % (nick, trailing)
	def user_parted(self, args, prefix, trailing):
		nick = self.bot.extract_nick_from_prefix(prefix)
		print "Channels: user %s parted %s with message '%s'" % (nick, args[0], trailing)
