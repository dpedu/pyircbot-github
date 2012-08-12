#! /usr/bin/env python

import time
import threading

class BufferedConnection(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self);
		self.sock = socket;
		self.alive = True;
		self.buffer = [];
		self.BUFFSIZE = 8192;
		self.lastLineEndedWithNewline = True;
		self.splitLastLine = "";
		self.start();
	def run(self):
		while self.alive:
			incoming = self.sock.recv(self.BUFFSIZE);
			if(incoming==""):
				self.alive = False;
				return;
			if incoming[-1]=="\n":
				setNL = True;
			else:
				setNL= False
			incoming = incoming.split("\n");
			if not setNL: # if we didnt reach the end of the line on this buffer, save the last line for next time.
				self.splitLastLine = self.splitLastLine + incoming.pop();
			if not self.lastLineEndedWithNewline and len(incoming) > 0: # if our first line is actually a piece of last buffer's last line, put the 2 pieces back together and send it to the ready-for-output buffer.
				fixedline = self.splitLastLine + incoming.pop(0);
				self.splitLastLine=""
				self.buffer.append(fixedline)
			# Now, we can put any remaining full lines onto the output buffer
			self.buffer.extend(incoming);
			# and remember to save what happened this time
			self.lastLineEndedWithNewline = setNL
	def close(self):
		self.sock.close;
	def send(self, text):
		self.sock.send(text);
	def hasNext(self):
		return len(self.buffer) > 0;
	def nextLine(self):
		while(len(self.buffer)==0):
			time.sleep(.001);
		return self.buffer.pop(0)+"\n";