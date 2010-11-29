'''
Created on 21.05.2010

@author: i7
'''

import os
import re

class DirectoryScanner():
    '''
    classdocs
    '''
    directory = ""
    fileList = []

    def __init__(self, directory):
        '''
        Constructor
        '''
        self.directory = directory
        
    def setDirectory(self, directory):
        self.directory = directory
        
    def getDirectory(self):
        return self.directory
        
    def listDirectory(self, fileExtList, fileIgnoreRegex, type):
        self._listDirectory(self.directory, fileExtList, fileIgnoreRegex, type)
        return self.fileList
        
    def _listDirectory(self, directory, fileExtList, fileIgnoreRegex, type):                                        
        "get list of file info objects for files of particular extensions" 
        try:
            for f in os.listdir(directory):
                file = os.path.join(directory, f)
                if os.path.isdir(file):
                    self._listDirectory(file, fileExtList, fileIgnoreRegex, type)
                elif os.path.isfile(file):
                    ext = os.path.splitext(f)[1].lstrip(".")
                    name = os.path.splitext(f)[0]
                    if ext in fileExtList and re.search(fileIgnoreRegex, name) is None:
                        self.fileList.append([directory, name, ext, type])
        except Exception, ex:
            import sys, traceback

            print ex
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print "*** print_tb:"
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            print "*** print_exception:"
            traceback.print_exception(exc_type, exc_value, exc_traceback,
                                      limit=2, file=sys.stdout)
            print "*** print_exc:"
            traceback.print_exc()
