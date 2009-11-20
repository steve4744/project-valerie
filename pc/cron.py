#!/usr/bin/python
import os
import time

PYTHON="E:\\Python26\\python.exe"

vRepoDir="E:\\Documents\\Valerie\\pc"
vSvnDir="E:\\SlikSvn\\bin\\"



cmd = vSvnDir + "svn info " + vRepoDir
print "Executing: ", cmd

vRev = 0
vLastRev = 0

vPipe = os.popen(cmd, 'r')
for line in vPipe.readlines():
	if line.startswith("Revision: "):
		line=line.replace("Revision: ", "")
		vRev = line.lstrip()
	if line.startswith("Last Changed Rev: "):
		line=line.replace("Last Changed Rev: ", "")
		vLastRev = line.lstrip()

print "Revision: ", vRev
print "Last: ", vLastRev

if vRev != vLastRev:
#if vRev == vLastRev:

	cmd = vSvnDir + "svn up " + vRepoDir
	print "Executing: ", cmd

	vRetVal = os.system(cmd)

	print vRetVal
	if vRetVal == 0:
		print "BUILD"
		
		FILE = open(vRepoDir + "\\REV","w")
		FILE.write(vRev)
		FILE.close()
		
		vRetVal = os.system(vRepoDir + "\\build.bat")


else:
	print "UP TO DATE, NOT BUILDING"
#e:\documents\valerie\pc\build.bat
