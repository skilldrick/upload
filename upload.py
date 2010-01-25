#!/usr/local/bin/python3.1

from ftplib import FTP
import os
import re
import netrc


class Uploader:
    def __init__(self):
        self.local = Local()
        self.remote = Remote()

    def createDirs(self, localRoot, remoteRoot):
        self.remote.setCwd(remoteRoot)
        success = True
        for dir in self.local.getLocalDirs(localRoot):
            remoteDir = self.remote.makeUnix(dir)
            self.remote.create(remoteDir)
        for dir in self.local.getLocalDirs(localRoot, True):
            remoteDir = self.remote.makeUnix(dir)
            if not self.remote.exists(remoteDir):
                success = False
        return success

    def uploadFiles(self, dir):
        files = self.local.getLocalFiles(dir)
        for localPath in files:
            remotePath = self.remote.makeUnix(localPath)
            localSize = self.local.getSize(localPath)
            if self.remote.exists(remotePath):
                remoteSize = self.remote.getSize(remotePath)
            else:
                remoteSize = -1
            if not localSize == remoteSize:
                self.remote.upload(localPath, remotePath)
            remoteSize = self.remote.getSize(remotePath)
            if not localSize == remoteSize:
                return False
        return True


class Local:
    def countDirs(self, dir):
        count = 0
        for x in os.walk(dir):
            count += 1
        return count

    def getLocalDirs(self, dir, leaves=False):
        dirs = []
        for x in os.walk(dir):
            if leaves and x[1] == []:
                yield x[0]
            if not leaves:
                yield x[0]

    def getSize(self, filename):
        return os.path.getsize(filename)

    def getLocalFiles(self, dir):
        for x in os.walk(dir):
            for file in x[2]:
                yield os.path.join(x[0], file)


class Remote:
    lineExts = [
        'txt',
        'php',
        'html',
        'py',
        ]

    site = 'ftp.skilldrick.co.uk'
    
    def __init__(self):
        try:
            x = netrc.netrc()
        except IOError:
            homedir = os.path.expanduser('~') + '\\Application Data\\'
            x = netrc.netrc(homedir + '.netrc')
        info = x.authenticators(self.site)
        self.user = info[0]
        self.passwd = info[2]
        self.ftp = FTP(self.site)
        self.ftp.login(user=self.user, passwd=self.passwd)
        self.setCwd('/public_html')
        self.local = Local()

    def close(self):
        self.ftp.quit()

    def upload(self, local, remote):
        if self.getType(local) == 'lines':
            self.uploadAscii(local, remote)
        else:
            self.uploadBinary(local, remote)

    def uploadAscii(self, local, remote):
        self.ftp.cwd('/public_html')
        file = open(local)
        self.ftp.storlines('STOR ' + remote, file)
        file.close()

    def uploadBinary(self, local, remote):
        self.ftp.cwd('/public_html')
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

    def create(self, dir):
        dir = self.makeUnix(dir)
        if not self.exists(dir):
            self.ftp.mkd(dir)

    def exists(self, parent, item=None):
        parent = self.rstrip(parent)
        if item == None:
            parent, item = os.path.split(parent)
        filelist = self.ftp.nlst(parent)
        return item in filelist

    def setCwd(self, path):
        return self.ftp.cwd(path)

    def getPwd(self):
        return self.ftp.pwd()

    def getSize(self, filename):
        self.setCwd('/public_html')
        return self.ftp.size(filename)

    def rstrip(self, path):
        return path.rstrip('/')

    def makeUnix(self, path):
        return path.replace('\\', '/')
