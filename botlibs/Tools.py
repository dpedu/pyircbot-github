#!/usr/bin/env python

def messageHasCommand(command, message):
	if message[0:len(command)+1] == command+" " or (message[0:len(command)] == command and len(command) == len(command)):
		return (True, command, message[len(command)+1:], message)
	else:
		return False;