#!/usr/bin/python2.6

import sys
import os
#adds the current path to the import path
sys.path.insert(0, os.path.realpath('.')) 

from ftplib import FTP
import ftplib
import re
import netrc
import optparse
import time

import uploadsettings as settings


def fill(fillChar):
    print ''.center(78, fillChar)


class Uploader:
    dircount = 0
    filecount = 0
    fileerrorcount = 0
    
    def __init__(self, options=None, args=None):
        try:
            comparison = options.comparison
        except AttributeError:
            comparison = 'time'

        try:
            site = args[0]
        except (IndexError, TypeError):
            site = settings.site
        
        if comparison == 'size':
            self.comparisonFunc = self.compareSize
        else:
            self.comparisonFunc = self.compareTime
            
        self.speedyComparisonFunc = self.compareTimeLocally

        try:
            self.verbose = options.verbose
        except AttributeError:
            self.verbose = False
        self.local = Local()
        self.remote = Remote(site)

    def createDirs(self, localRoot, remoteRoot):
        success = True
        for dir in self.local.getLocalDirs(localRoot):
            remoteDir = self.remote.makeUnix(dir, remoteRoot)
            if self.remote.create(remoteDir, self.verbose):
                self.dircount += 1
        for dir in self.local.getLocalDirs(localRoot, True):
            remoteDir = self.remote.makeUnix(dir, remoteRoot)
            if not self.remote.exists(remoteDir):
                    print 'Failed to upload', dir
                    self.dircount -= 1
                    success = False
        if self.verbose and success:
            print 'Directories created successfully'
            fill('-')
        elif self.verbose:
            print 'Error creating directories'
        return success

    def uploadFiles(self, localRoot, remoteRoot, speedy=False):
        files = self.local.getLocalFiles(localRoot)
        success = True
        for localPath in files:
            remotePath = self.remote.makeUnix(localPath, remoteRoot)
            localPath = os.path.join(localRoot, localPath)
            if speedy:
                if not self.speedyComparisonFunc(localPath, remotePath):
                    if self.verbose:
                        print 'Uploading', localPath
                    self.remote.upload(localPath, remotePath)
                    self.filecount += 1
                    if not self.comparisonFunc(localPath, remotePath):
                        self.filecount -= 1
                        self.fileerrorcount += 1
                        if self.verbose:
                            print localPath, 'is different to', remotePath
                        success = False
                elif self.verbose:
                    print 'Skipping', localPath
            else:
                if not self.comparisonFunc(localPath, remotePath):
                    if self.verbose:
                        print 'Uploading', localPath
                    self.remote.upload(localPath, remotePath)
                    self.filecount += 1
                elif self.verbose:
                    print 'Skipping', localPath
                if not self.comparisonFunc(localPath, remotePath):
                    self.filecount -= 1
                    self.fileerrorcount += 1
                    if self.verbose:
                        print localPath, 'is different to', remotePath
                    success = False
        return success

    def compareSize(self, localFile, remoteFile):
        localSize = self.local.getSize(localFile)
        if self.remote.exists(remoteFile):
            remoteSize = self.remote.getSize(remoteFile)
        else:
            return False
        return localSize == remoteSize

    def compareTime(self, localFile, remoteFile):
        localTime = self.local.getTime(localFile)
        if self.remote.exists(remoteFile):
            remoteTime = self.remote.getTime(remoteFile)
        else:
            return False
        if localTime > remoteTime:
            return self.checkEmpty(localFile, remoteFile)
        return True

    def checkEmpty(self, localFile, remoteFile):
        if (not self.local.getSize(localFile)) and (not self.remote.getSize(remoteFile)):
            return True
        else:
            return False

    def compareTimeLocally(self, localFile, remoteFile):
        localTime = self.local.getTime(localFile)
        lastRun = self.readLastRun()
        if lastRun == -1: #if no config file
            return self.compareTime(localFile, remoteFile)
        else:
            return localTime <= lastRun

    def printSummary(self):
        fill('=')
        if not (self.dircount or self.filecount):
            print 'Nothing changed'
        if self.dircount:
            if self.dircount == 1:
                print '1 directory was created'
            else:
                print self.dircount, 'directories were created'
        if self.filecount:
            if self.filecount == 1:
                print '1 file was uploaded'
            else:
                print self.filecount, 'files were uploaded'
        if self.fileerrorcount:
            if self.fileerrorcount == 1:
                print 'There was an error with 1 file'
            else:
                print 'There were errors with', self.filecount, 'files'
            
    def writeLastRun(self, value):
        import ConfigParser
        config = ConfigParser.RawConfigParser()
        config.set('DEFAULT', 'lastrun', value)
        with open('.lastrun', 'w') as configfile:
            config.write(configfile)

    def readLastRun(self):
        import ConfigParser
        config = ConfigParser.RawConfigParser()
        try:
            config.read('.lastrun')
            lastRun = config.getint('DEFAULT', 'lastrun')
        except configparser.NoOptionError:
            lastRun = -1
        return lastRun


class Local:
    def countDirs(self, dir):
        count = 0
        for x in os.walk(dir):
            count += 1
        return count

    def getIgnoreDirs(self, dir):
        ignoreDirsNested = settings.ignoreDirs
        ignoreDirs = []
        for item in ignoreDirsNested:
            if isinstance(item, list):
                item = os.path.join(*item)
            ignoreDirs.append(item)
        ignoreDirs = tuple([os.path.join(dir, x) for x in ignoreDirs])
        return ignoreDirs

    def getLocalDirs(self, dir, leaves=False):
        ignoreDirs = self.getIgnoreDirs(dir)
        for x in os.walk(dir):
            if x[0].startswith(ignoreDirs):
                continue
            if leaves and x[1] == []:
                yield x[0][len(dir) + 1:]
            if not leaves:
                yield x[0][len(dir) + 1:]

    def getSize(self, filename):
        return os.path.getsize(filename)

    def getTime(self, filename):
        localTime = os.path.getmtime(filename)
        localTime = time.gmtime(localTime)
        return int(time.strftime('%Y%m%d%H%M%S', localTime))

    def getNow(self):
        return int(time.strftime('%Y%m%d%H%M%S', time.localtime()))

    def getLocalFiles(self, dir):
        ignoreDirs = self.getIgnoreDirs(dir)
        ignoreSuffixes = tuple(settings.ignoreFileSuffixes)
        for x in os.walk(dir):
            if x[0].startswith(ignoreDirs):
                continue
            for file in x[2]:
                if file.endswith(ignoreSuffixes):
                    continue
                yield os.path.join(x[0][len(dir) + 1:],
                                   file)


class Remote:
    lineExts = [
        'txt',
        'php',
        'html',
        'py',
        ]

    webRoot = settings.webRoot

    def __init__(self, site):
        try:
            x = netrc.netrc()
        except IOError:
            homedir = os.path.expanduser('~') + '\\Application Data\\'
            x = netrc.netrc(homedir + '.netrc')
        info = x.authenticators(site)
        self.user = info[0]
        self.passwd = info[2]
        self.ftp = FTP(site)
        self.ftp.login(user=self.user, passwd=self.passwd)
        self.setCwd(self.webRoot)
        self.local = Local()

    def close(self):
        self.ftp.quit()

    def upload(self, local, remote):
        if self.getType(local) == 'lines':
            self.uploadAscii(local, remote)
        else:
            self.uploadBinary(local, remote)

    def uploadAscii(self, local, remote):
        self.ftp.cwd(self.webRoot)
        file = open(local)
        self.ftp.storlines('STOR ' + remote, file)
        file.close()

    def uploadBinary(self, local, remote):
        self.ftp.cwd(self.webRoot)
        file = open(local, 'rb')
        self.ftp.storbinary('STOR ' + remote, file)
        file.close()

    def getType(self, filename):
        result = re.search('\.([a-z]*)$', filename)
        try:
            ext = result.group(1)
        except AttributeError:
            ext = ''
        if ext in self.lineExts:
            return 'lines'
        else:
            return 'binary'

    def create(self, dir, verbose=False):
        if not self.exists(dir):
            if verbose:
                print 'Making', dir
            self.ftp.mkd(dir)
            return True
        else:
            if verbose:
                print 'Skipping', dir
            return False

    def exists(self, parent, item=None):
        parent = self.stripSlash(parent)
        if item == None:
            parent, item = os.path.split(parent)

        filelist = self.ftp.nlst(parent)
        return item in filelist

    def setCwd(self, path):
        return self.ftp.cwd(path)

    def getPwd(self):
        return self.ftp.pwd()

    def getSize(self, filename):
        self.setCwd(self.webRoot)
        return self.ftp.size(filename)

    def getTime(self, filename):
        modifiedTime = self.ftp.sendcmd('MDTM ' + filename)
        return int(modifiedTime[4:])

    def stripSlash(self, path):
        return path.rstrip('/')

    def makeUnix(self, path, remoteRoot):
        return remoteRoot + '/' + path.replace('\\', '/')


def main():
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", action="store_true")
    parser.add_option("-f", "--files", action="store_true")
    parser.add_option("-s", "--speedy", action="store_true")
    parser.add_option("-c", "--comparison")
    #need to pass options to Uploader in a more sensible way
    #speedy option doesn't need to check files have uploaded
    #so we'll have to refactor uploadfiles
    options, args = parser.parse_args()

    uploader = Uploader(options, args)

    if not options.files:
        uploader.createDirs(settings.localDir,
                            settings.remoteDir)

    uploader.uploadFiles(settings.localDir,
                         settings.remoteDir,
                         options.speedy)

    uploader.writeLastRun(uploader.local.getNow())
    
    if options.verbose:
        uploader.printSummary()
        print
    
        
if __name__ == '__main__':
    main()
