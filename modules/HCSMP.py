#!/usr/bin/env python
from botlibs import ModuleBase,Tools
import time
import socket
import struct

class HCSMP(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="HCSMP"
		self.hooks=[ModuleBase.ModuleHook("PRIVMSG", self.hcsmp)]
		self.loadConfig()
		
		print "HCSMP loaded"
	
	def hcsmp(self, args, prefix, trailing):
		cmd = Tools.messageHasCommand("!hcsmp", trailing, False)
		if cmd and cmd[2]=='':
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.settimeout(5)
				start=time.time()
				s.connect(("hardcore.hcsmp.com", 25565))
				s.send('\xFE\x01')
				d = s.recv(512)
				end=time.time()
				s.close()
				d = d[5:].decode('utf-16be').split('\x00')
				
				self.bot.do_privmsg(args[0], "Online, %sms ping, MC v%s, %s/%s players: %s" % ( str(int((end-start)*1000)), d[2], d[4], d[5], d[3] ) )
			except Exception,e:
				print e
				self.bot.do_privmsg(args[0], "HCSMP seems to be down!")
