#!/usr/bin/env python
import socket
import threading
import sys
import yaml
import traceback
from botlibs import BufferedConnection

# main class of the bot - yes, this means you can theoretically run more then one bot at once. you just need multiple config files.
class PyIRCBot(threading.Thread):
	def __init__(self, configpath):
		threading.Thread.__init__(self)
		
		# Add module includes path
		sys.path.append("modules/")
		
		# path to our configuration file
		self.configpath = configpath
		
		# will hold our config information as an object
		self.config = None;
		
		# listener thread
		self.listener = None;
		
		# BufferedConnection reference
		self.connection = None;
		
		# commands from RFC 1459
		self.hooks = [
			'NOTICE',	# :irc.129irc.com NOTICE AUTH :*** Looking up your hostname...
			'MODE',		# :CloneABCD MODE CloneABCD :+iwx
			'PING',		# PING :irc.129irc.com
			'JOIN',		# :CloneA!dave@hidden-B4F6B1AA.rit.edu JOIN :#clonea
			'PART',		# :CloneA!dave@hidden-B4F6B1AA.rit.edu PART #clonea
			'PRIVMSG',	# :CloneA!dave@hidden-B4F6B1AA.rit.edu PRIVMSG #clonea :aaa
			'KICK',		# :xMopxShell!~rduser@host KICK #xMopx2 xBotxShellTest :xBotxShellTest
			'001',		# :irc.129irc.com 001 CloneABCD :Welcome to the 129irc IRC Network CloneABCD!CloneABCD@djptwc-laptop1.rit.edu
			'002',		# :irc.129irc.com 002 CloneABCD :Your host is irc.129irc.com, running version Unreal3.2.8.1
			'003',		# :irc.129irc.com 003 CloneABCD :This server was created Mon Jul 19 2010 at 03:12:01 EDT
			'004',		# :irc.129irc.com 004 CloneABCD irc.129irc.com Unreal3.2.8.1 iowghraAsORTVSxNCWqBzvdHtGp lvhopsmntikrRcaqOALQbSeIKVfMCuzNTGj
			'005',		# :irc.129irc.com 005 CloneABCD CMDS=KNOCK,MAP,DCCALLOW,USERIP UHNAMES NAMESX SAFELIST HCN MAXCHANNELS=10 CHANLIMIT=#:10 MAXLIST=b:60,e:60,I:60 NICKLEN=30 CHANNELLEN=32 TOPICLEN=307 KICKLEN=307 AWAYLEN=307 :are supported by this server
						# :irc.129irc.com 005 CloneABCD MAXTARGETS=20 WALLCHOPS WATCH=128 WATCHOPTS=A SILENCE=15 MODES=12 CHANTYPES=# PREFIX=(qaohv)~&@%+ CHANMODES=beI,kfL,lj,psmntirRcOAQKVCuzNSMTG NETWORK=129irc CASEMAPPING=ascii EXTBAN=~,cqnr ELIST=MNUCT :are supported by this server
			'250',		# :chaos.esper.net 250 xBotxShellTest :Highest connection count: 1633 (1632 clients) (186588 connections received)
			'251',		# :irc.129irc.com 251 CloneABCD :There are 1 users and 48 invisible on 2 servers
			'252',		# :irc.129irc.com 252 CloneABCD 9 :operator(s) online
			'254',		# :irc.129irc.com 254 CloneABCD 6 :channels formed
			'255',		# :irc.129irc.com 255 CloneABCD :I have 42 clients and 1 servers
			'265',		# :irc.129irc.com 265 CloneABCD :Current Local Users: 42  Max: 47
			'266',		# :irc.129irc.com 266 CloneABCD :Current Global Users: 49  Max: 53
			'332',		# :chaos.esper.net 332 xBotxShellTest #xMopx2 :/ #XMOPX2 / https://code.google.com/p/pyircbot/ (Channel Topic)
			'333',		# :chaos.esper.net 333 xBotxShellTest #xMopx2 xMopxShell!~rduser@108.170.60.242 1344370109
			'353',		# :irc.129irc.com 353 CloneABCD = #clonea :CloneABCD CloneABC 
			'366',		# :irc.129irc.com 366 CloneABCD #clonea :End of /NAMES list.
			'372',		# :chaos.esper.net 372 xBotxShell :motd text here
			'375',		# :chaos.esper.net 375 xBotxShellTest :- chaos.esper.net Message of the Day -
			'376',		# :chaos.esper.net 376 xBotxShell :End of /MOTD command.
			'422'		# :irc.129irc.com 422 CloneABCD :MOTD File is missing
		]
		# /me is :user PRIVMSG #clonea :ACTION action
		
		# map of commands to hooked-in methods - created automatically
		self.hookcalls = {}
		
		# stored imported modules
		self.modules = {}
		
		# instances of modules
		self.moduleInstances = {}
		
		# module settings that persist across reload
		self.moduleSettings = {}
		
	def run(self):
		# load bots configuration
		self.readConfig()
		# create dict of hookable functions
		self.createHookCalls()
		# from the config, load all the autoloaded modules
		self.loadInitialModules()
		# Conenct to server
		self.connect()
		# Send USER and NICK and that crap
		self.initConnection()
		# Start out listener thread
		self.listener = BotSocketListener(self)
	
	def connect(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(( self.config["server"], int(self.config["port"]) ))
		self.connection = BufferedConnection.BufferedConnection(s)
	
	def readConfig(self):
		self.config = yaml.load(file(self.configpath, 'r'))
	
	def initConnection(self):
		self.sendUser()
		self.set_nick(self.config["nick"])
	
	def createHookCalls(self):
		for command in self.hooks:
			self.hookcalls[command]=[]
		
	def addHook(self, command, method):
		if command in self.hooks:
			self.hookcalls[command].append(method);
		else:
			print "Invalid hook - %s" % command
			return False
	
	def removeHook(self, command, method):
		if command in self.hooks:
			for hookedMethod in self.hookcalls[command]:
				if hookedMethod == method:
					self.hookcalls[command].remove(hookedMethod)
		else:
			print "Invalid hook - %s" % command
			return False
	
	def loadModuleHooks(self, module):
		for hook in module.hooks:
			self.addHook(hook.hook, hook.method)
	
	def unloadModuleHooks(self, module):
		for hook in module.hooks:
			self.removeHook(hook.hook, hook.method)
	def loadInitialModules(self):
		for modulename in self.config["autoload"]:
			self.loadmodule(modulename)
	
	def loadmodule(self, name):
		if name in self.moduleInstances:
			print "Module %s already loaded" % name
			return False
		if not name in self.modules:
			self.importmodule(name)
		self.moduleInstances[name] = getattr(self.modules[name], name)(self)
		self.loadModuleHooks(self.moduleInstances[name])
		if name in self.moduleSettings:
			moduleInstances[name].properties = self.moduleSettings[name]
	def unloadmodule(self, name):
		if name in self.moduleInstances:
			# run module's diable method
			self.moduleInstances[name].ondisable()
			# remove hooks
			self.unloadModuleHooks(self.moduleInstances[name]);
			# remove instance in self.moduleInstances
			item = self.moduleInstances.pop(name)
			# and finally, delete the object.
			del item
			print "Module %s unloaded" % name
		else:
			print "module %s not loaded" % name
	def importmodule(self, name):
		if not name in self.modules:
			try:
				# manually import the module saving it in out list of modules
				moduleref = __import__(name)
				self.modules[name]=moduleref
				return True
			except Exception, e:
				print "Module %s failed to load: " % name
				print str(e)
				return False
		else:
			print "Module %s already imported" % name
			return False
		# this will silently fail if the module is already loaded
	def deportmodule(self, name):
		# unload it before we do this
		self.unloadmodule(name)
		if name in self.modules:
			# delete it
			item = self.modules[name];
			del self.modules[name]
			del item
			# finally, delete any cache in sys.modules
			if name in sys.modules:
				del sys.modules[name]
	def reloadmodule(self, name):
		if name in self.modules:
			loadedbefore = name in self.moduleInstances;
			self.unloadmodule(name);
			print "reloading %s" % self.modules[name]
			reload(self.modules[name])
			if loadedbefore:
				self.loadmodule(name);
	def redomodule(self, name):
		loadedbefore = name in self.moduleInstances;
		self.deportmodule(name)
		self.importmodule(name)
		if loadedbefore:
			self.loadmodule(name)
	
	def getmodulebyname(self, name):
		if not name in self.moduleInstances:
			return None
		return self.moduleInstances[name]
	
	def getmodulesbyservice(self, service):
		validModules = []
		for module in self.moduleInstances:
			if service in self.moduleInstances[module].services:
				validModules.append(self.moduleInstances[module])
		return validModules
	
	def set_nick(self, newNick):
		self.sendText("NICK %s" % newNick);
	def get_nick(self):
		return self.config["nick"];
	
	def do_join(self, channel):
		self.sendText("JOIN %s"%channel);
		
	def do_privmsg(self, towho, message):
		self.sendText("PRIVMSG %s :%s"%(towho,message))
		
	def do_setMode(self, channel, mode, extra=None):
		if extra != None:
			self.sendText("MODE %s %s %s" % (channel,mode,extra))
		else:
			self.sendText("MODE %s %s" % (channel,mode))
	
	def do_pingrespond(self, where):
		self.sendText("PONG :%s" % where)
	
	def do_action(self, channel, action):
		self.sendText("PRIVMSG %s :\x01ACTION %s"%(channel,action))
		
	def do_kick(self, channel, who, comment):
		self.sendText("KICK %s %s :%s" % (channel, who, comment));
	
	
	def sendUser(self):
		self.sendText("USER %s %s %s :%s" % (self.config["nick"], self.config["hostname"], self.config["server"], self.config["realname"]))
	
	def sendText(self, text):
		self.connection.send(text+"\n")
	
	def extract_nick_from_prefix(self, prefix):
		pos=[]
		pos.append(prefix.find("@"))
		pos.append(prefix.find("!"))
		pos.sort()
		return prefix[0:pos[0]]
	def extract_ip_from_prefix(self, prefix):
		return prefix.split("@")[1]
	def processLine(self, line):
		if line.strip() == "":
			return;
		originalline = line
		prefix = None;
		command = None
		args=[]
		trailing=None
		
		if line[0]==":":
			prefix=line.split(" ")[0][1:]
			line=line[line.find(" ")+1:]
		command = line.split(" ")[0]
		line=line[line.find(" ")+1:]
		if(line[0]==":"):
			# no args
			trailing = line[1:].strip()
		else:
			trailing = line[line.find(" :")+2:].strip()
			line = line[:line.find(" :")]
			args = line.split(" ")
		for index,arg in enumerate(args):
			args[index]=arg.strip()
		#print "Got cmd '%s' prefix '%s' args '%s', trailing '%s'" % (command, prefix, args, trailing)
		if not command in self.hookcalls:
			print "Unknown command: cmd='%s' prefix='%s' args='%s' trailing='%s'" % (command, prefix, args, trailing)
			print "Original text: '%s'" % (originalline.strip())
		else:
			for hook in self.hookcalls[command]:
				try:
					hook(args, prefix, trailing)
				except:
					print "Error processing hook: \n%s"% traceback.format_exc()
	def shutdown(self):
		names = []
		for name in self.modules:
			names.append(name)
		for name in names:
			self.deportmodule(name)
		self.listener.running = False
		self.connection.close()
	def signal_handler(self, signal, frame):
		print "CTRL-C Recieved, Shutting down"
		self.shutdown()
		
class BotSocketListener(threading.Thread):
	def __init__(self, bot):
		threading.Thread.__init__(self)
		self.bot = bot;
		self.running = True;
		self.start()
	def run(self):
		while self.running:
			line=self.bot.connection.nextLine()
			self.bot.processLine(line);
