#!/usr/bin/env python
import socket
import time
import threading

class BufferedConnection(threading.Thread):
	def __init__(self, socket, callback):
		" Passed the socket object and a method to call when a full line delimited by \n is received "
		threading.Thread.__init__(self);
		self.callback = callback
		self.sock = socket;
		self.alive = True;
		self.buffer = "";
		self.BUFFSIZE = 8192;
		self.lastLineEndedWithNewline = True;
		self.splitLastLine = "";
	def run(self):
		while self.alive:
			incoming = self.sock.recv(self.BUFFSIZE);
			if(incoming==""):
				self.alive = False;
				return;
			self.buffer += incoming
			while self.alive:
				pos = self.buffer.find("\n")
				if pos == -1:
					break
				line = self.buffer[0:pos]
				self.buffer = self.buffer[pos+1:]
				self.callback(line)
	def close(self):
		" Immediately close the socket and halt processing "
		self.alive = False
		self.sock.shutdown(socket.SHUT_WR)
	def send(self, text):
		" Send raw text to the socket "
		self.sock.send(text)