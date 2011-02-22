import sys

def printl2(string, parent=None):
	if parent is None:
		print "[Project Valerie] ", string
	else:
		classname = str(parent.__class__).rsplit(".", 1)
		if len(classname) == 2:
			classname = classname[1]
			classname = classname.rstrip("\'>")
			classname += "::"
			
		else:
			classname = ""
		print "[Project Valerie] " + classname + str(sys._getframe(1).f_code.co_name), string