#!/usr/local/bin/python3.1

from ftplib import FTP
import ftplib
import os
import re
import netrc
import optparse
import time

import uploadsettings as settings


def fill(fillChar):
    print(''.center(78, fillChar))


class Uploader:
    dircount = 0
    filecount = 0
    
    def __init__(self, site=settings.site, verbose=False, comparison=None):
        if comparison == None:
            comparison = 'time'
        
        if comparison == 'size':
            self.comparisonFunc = self.compareSize
        else:
            self.comparisonFunc = self.compareTime

        self.verbose = verbose
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
                    print('Failed to upload', dir)
                    self.dircount -= 1
                    success = False
        if self.verbose and success:
            print('Directories created successfully')
            fill('-')
        elif self.verbose:
            print('Error creating directories')
        return success

    def uploadFiles(self, localRoot, remoteRoot):
        files = self.local.getLocalFiles(localRoot)
        success = True
        for localPath in files:
            remotePath = self.remote.makeUnix(localPath, remoteRoot)
            localPath = os.path.join(localRoot, localPath)
            if not self.comparisonFunc(localPath, remotePath):
                if self.verbose:
                    print('Uploading', localPath)
                self.remote.upload(localPath, remotePath)
                self.filecount += 1
            else:
                if self.verbose:
                    print('Skipping', localPath)
            if not self.comparisonFunc(localPath, remotePath):
                if self.verbose:
                    print(localPath, 'is different to', remotePath)
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
        localTime = os.path.getmtime(localFile)
        localTime = time.gmtime(localTime)
        localTime = int(time.strftime('%Y%m%d%H%M%S', localTime))
        if self.remote.exists(remoteFile):
            remoteTime = self.remote.getTime(remoteFile)
        else:
            return False
        return localTime <= remoteTime

    def printSummary(self):
        fill('=')
        if not (self.dircount or self.filecount):
            print('Nothing changed')
        if self.dircount:
            if self.dircount == 1:
                print('1 directory was created')
            else:
                print(self.dircount, 'directories were created')
        if self.filecount:
            if self.filecount == 1:
                print('1 file was uploaded')
            else:
                print(self.filecount, 'files were uploaded')
            


class Local:
    def countDirs(self, dir):
        count = 0
        for x in os.walk(dir):
            count += 1
        return count

    def getLocalDirs(self, dir, leaves=False):
        ignoreDirs = tuple([os.path.join(dir, x) for x
                      in settings.ignoreDirs])
        for x in os.walk(dir):
            if x[0].startswith(ignoreDirs):
                continue
            if leaves and x[1] == []:
                yield x[0][len(dir) + 1:]
            if not leaves:
                yield x[0][len(dir) + 1:]

    def getSize(self, filename):
        return os.path.getsize(filename)

    def getLocalFiles(self, dir):
        ignoreDirs = tuple([os.path.join(dir, x) for x
                      in settings.ignoreDirs])
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
                print('Making', dir)
            self.ftp.mkd(dir)
            return True
        else:
            if verbose:
                print('Skipping', dir)
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



if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", action="store_true")
    parser.add_option("-f", "--files", action="store_true")
    parser.add_option("-c", "--comparison")
    options, args = parser.parse_args()

    if options.verbose and args:
        uploader = Uploader(site=args[0], verbose=True,
                            comparison=options.comparison)
    elif options.verbose:
        uploader = Uploader(verbose=True,
                            comparison=options.comparison)
    else:
        uploader = Uploader(comparison=options.comparison)

    if not options.files:
        uploader.createDirs(settings.localDir,
                            settings.remoteDir)
    uploader.uploadFiles(settings.localDir,
                         settings.remoteDir)
    if options.verbose:
        uploader.printSummary()
