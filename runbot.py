#! /usr/bin/env python

# Only required import
from botlibs import PyIRCBot

# For testing
import traceback
import signal

# One or more bots can be started this way
botThread = PyIRCBot.PyIRCBot("botconfig/config.yml")
botThread.start()
signal.signal(signal.SIGINT, botThread.signal_handler)

# Simple debug "shell"
# Commands:
#	load <module>
#	unload <module>
#	deport <module>
#	import <module>
#	reload <module>
#	redo <module>
#	dump imports
#	dump insts
#	dump hookcalls
#	dump settings
#	dump modules
#	trace
#	exit

alive = True
while alive:
	c = raw_input().strip();
	try:
		args = c.split(" ")
		if args[0]=="load":
			botThread.loadmodule(args[1])
		elif args[0]=="unload":
			botThread.unloadmodule(args[1])
		elif args[0]=="dump":
			if args[1]=="imports":
				print str(botThread.modules)
			elif args[1]=="insts":
				print str(botThread.moduleInstances)
			elif args[1]=="hookcalls":
				print str(botThread.hookcalls)
			elif args[1]=="settings":
				print str(botThread.moduleSettings)
			elif args[1]=="modules":
				for item in sys.modules:
					print "%s: %s" % (item, sys.modules[item])
		elif args[0]=="deport":
			botThread.deportmodule(args[1]);
		elif args[0]=="import":
			botThread.importmodule(args[1]);
		elif args[0]=="reload":
			botThread.reloadmodule(args[1]);
		elif args[0]=="redo":
			botThread.redomodule(args[1]);
		elif args[0]=="exit":
			botThread.signal_handler(9, 9)
			alive = False
		elif args[0]=="trace":
			print >> sys.stderr, "\n*** STACKTRACE - START ***\n"
			code = []
			for threadId, stack in sys._current_frames().items():
				code.append("\n# ThreadID: %s" % threadId)
				for filename, lineno, name, line in traceback.extract_stack(stack):
					code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
					if line:
						code.append("  %s" % (line.strip()))
			for line in code:
				print >> sys.stderr, line
			print >> sys.stderr, "\n*** STACKTRACE - END ***\n"
		else:
			print "nope"
	except Exception,e:
		print e
		pass