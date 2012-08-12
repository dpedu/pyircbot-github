#!/usr/bin/env python
from BufferedConnection import *

def readConfig(filePath):
	class config: pass
	c = config()
	read = open(filePath, "r")
	while True:
		line = read.readline()
		if not line:
			break
		key,value = line.split("=");
		if "[]" in key:
			key = key.replace("[]", "");
			if not hasattr(c,key):
				setattr(c, key, [])
			l=getattr(c, key)
			l.append(value.strip());
			setattr(c, key, l)
		else:
			setattr(c, key, value.strip())
	return c