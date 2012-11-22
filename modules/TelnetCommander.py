#! /usr/bin/env python
from botlibs import ModuleBase
from botlibs import Tools
import threading
import socket
import curses
import sys
import time

import traceback
import resource

class TelnetCommander(ModuleBase.ModuleBase):
	def __init__(self, bot):
		ModuleBase.ModuleBase.__init__(self, bot);
		self.moduleName="TelnetCommander"
		self.hooks=[]
		self.loadConfig()
		
		self.commander = TelnetCommanderThread(self)
		
		print "TelnetCommander loaded"
	
	def ondisable(self):
		self.commander.stop()
		print "Module %s is being disabled" % self.moduleName
		
class TelnetCommanderThread(threading.Thread):
	def __init__(self, tc):
		threading.Thread.__init__(self);
		self.tc = tc
		self.socket = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.socket.bind((self.tc.config["listaddr"], self.tc.config["port"]))
		self.socket.listen(9999)
		self.clients = []
		self.listening = True
		self.start()
		print "TelnetCommander listening on port %s" % self.tc.config["port"]
	def stop(self):
		self.listening = False
		self.socket.shutdown(socket.SHUT_RDWR)
		self.socket.close()
		for client in self.clients:
			client.stop()
	def run(self):
		while self.listening:
			try:
				s = self.socket.accept();
				x = TelnetCommanderClientThread(self, self.tc.bot, s);
				self.clients.append(x)
			except Exception,e:
				pass

class TelnetCommanderClientThread(threading.Thread):
	def __init__(self, commanderMaster, bot, socket):
		threading.Thread.__init__(self);
		self.commanderMaster = commanderMaster
		self.bot = bot
		self.s = socket[0]
		self.remoteAddr = socket[1][0]
		
		self.authenticated = False
		
		self.start()
	def run(self):
		print "TelnetCommander: Connected from %s" % self.remoteAddr
		
		self.s.send("Hello Welcome to PYIRCBOT")
		while not self.authenticated:
			self.s.send("\nPlease enter a password and press enter: ")
			password = self.s.recv(1024)
			if password.strip()==self.commanderMaster.tc.config["password"]:
				self.authenticated = True
		self.s.send("Authenticated successfully.\n\n")
		
		while True:
			self.s.send("> ")
			inp = self.s.recv(1024)
			if inp =="":
				break
			cmd = inp.strip().split(" ", 1)
			args = cmd[1:]
			if len(args)>0:
				args = args[0]
			cmd = cmd[0]
			try:
				
				if cmd=="help":
					self.s.send( "	Help for Telnet Commander \n")
					self.s.send( "	mem:               display bot's total memory usage\n")
					self.s.send( "	reload <module>:   reload a module by given name\n")
					self.s.send( "	print <what>:      print information about the bot\n")
					self.s.send( "	      trace:       a stack trace\n")
					self.s.send( "	      version:     bot version\n")
					self.s.send( "	      imports:     imported bot modules\n")
					self.s.send( "	      modules:     running modules\n")
					self.s.send( "	      hooks:       active hooks from modules\n")
					self.s.send( "	quit:              disconnect from telnetcommander\n")
					self.s.send( "	bot <action>:      make the bot do something\n")
					self.s.send( "	    stop           shut down the bot\n")
					self.s.send( "	msg <ch> <msg>     Message a channel (or person)\n")
				
				elif cmd=="reload":
					if len(args)==0:
						self.s.send("Usage: reload TelnetCommander\n")
						continue
					for what in args:
						self.s.send("Reloading %s... \n" % what)
						if self.commanderMaster.tc.moduleName == what:
							self.s.send("Warning: You will lose connection now.\n")
						self.bot.redomodule(what)
				elif cmd=="print":
					if len(args)==0:
						self.s.send("Usage: print <what>\n")
						continue
					for what in args:
						if what == "imports":
							for moduleName in self.bot.modules:
								self.s.send("	%s : %s\n" % (moduleName, str(self.bot.modules[moduleName])))
						elif what == "trace":
							self.s.send("%s\n" % self.bot.fullTrace())
						elif what == "version":
							self.s.send("PyIRCBot Version: %s\n" % self.bot.version)
						elif what == "modules":
							for moduleName in self.bot.moduleInstances:
								self.s.send("	%s : %s\n" % (moduleName, str(self.bot.moduleInstances[moduleName])))
						elif what == "hooks":
							# self.hookcalls[command]=[]
							for irccommand in self.bot.hookcalls:
								if len(self.bot.hookcalls[irccommand])>0:
									self.s.send("	%s\n" % irccommand)
									for method in self.bot.hookcalls[irccommand]:
										# TODO add module name too
										self.s.send("		%s\n" % (method.__name__))
				elif cmd=="bot":
					if len(args)==0:
						self.s.send("Usage: bot <action>\n")
						continue
					if args[0]=="stop":
						self.bot.shutdown()
						sys.exit(0)
				elif cmd=="msg":
					self.bot.do_privmsg(args.split(" ", 1)[0], args.split(" ", 1)[1])
					self.s.send("	%s -> %s : %s\n" % ("PyIRCBot", args.split(" ", 1)[0], args.split(" ", 1)[1]))
				elif cmd=="quit":
					self.s.send( "Goodbye.\n")
					self.stop()
				elif cmd=="mem":
					size = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024, 2)
					self.s.send( "Runtime memory use: %s MB\n" % size)
				else:
					self.s.send("Invalid command.\n")
			except Exception, e:
				self.s.send( "Error processing your command: %s\n" % str(e))
		
		
		
	def stop(self):
		self.s.shutdown(socket.SHUT_RDWR)
		self.s.close()
