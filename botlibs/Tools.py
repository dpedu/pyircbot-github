#!/usr/bin/env python

def messageHasCommand(command, message, requireArgs=False):
	# Check if the message at least starts with the command
	messageBeginning = message[0:len(command)]
	if messageBeginning!=command:
		return False
	# Make sure it's not a subset of a longer command (ie .meme being set off by .memes)
	subsetCheck = message[len(command):len(command)+1]
	if subsetCheck!=" " and subsetCheck!="":
		return False
	
	# We've got the command! Do we need args?
	argsStart = len(command)
	args = ""
	if argsStart > 0:
		args = message[argsStart+1:]
	
	if requireArgs and args.strip() == '':
		return False
	
	# Verified! Return the set.
	return (True, command, args, message)