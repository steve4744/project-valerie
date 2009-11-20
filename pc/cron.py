#!/usr/bin/python
import os
import time

PYTHON="E:\\Python26\\python.exe"

vRepoDir="E:\\Documents\\Valerie\\pc"
vSvnDir="E:\\SlikSvn\\bin\\"


##### GET REVISION
vRev = 0
cmd = vSvnDir + "svn info " + vRepoDir
print "Executing: ", cmd
vPipe = os.popen(cmd, 'r')
for line in vPipe.readlines():
	if line.startswith("Revision: "):
		line=line.replace("Revision: ", "")
		vRev = line.lstrip()

print "Revision: ", vRev
##### END GET REVISION

###### UPDATE
cmd = vSvnDir + "svn up " + vRepoDir
print "Executing: ", cmd
vRetVal = os.system(cmd)
print vRetVal
###### END UPDATE

##### GET NEW REVISION
vNewRev = 0
cmd = vSvnDir + "svn info " + vRepoDir
print "Executing: ", cmd
vPipe = os.popen(cmd, 'r')
for line in vPipe.readlines():
	if line.startswith("Revision: "):
		line=line.replace("Revision: ", "")
		vNewRev = line.lstrip()

print "NewRevision: ", vNewRev
##### END GET NEW REVISION


if vRev != vNewRev:
#if vRev == vNewRev:
	print "BUILD"
	
	FILE = open(vRepoDir + "\\REV","w")
	FILE.write(vNewRev)
	FILE.close()
	
	vRetVal = os.system(vRepoDir + "\\build.bat")


else:
	print "UP TO DATE, NOT BUILDING"
#e:\documents\valerie\pc\build.bat
