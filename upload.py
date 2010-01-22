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
            self.remote.create(dir)
            if not self.remote.exists(dir):
                success = False
        return success

class Local:
    def countDirs(self, dir):
        count = 0
        for x in os.walk(dir):
            count += 1
        return count

    def getLocalDirs(self, dir):
        dirs = []
        for x in os.walk(dir):
            dirs.append(x[0])
        return dirs


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
        self.local = Local()

    def close(self):
        self.ftp.quit()

    def uploadAscii(self, local, remote):
        self.ftp.cwd('/public_html/swedish/mytest')
        file = open(local)
        self.ftp.storlines('STOR ' + remote, file)
        self.ftp.retrlines('RETR ' + remote)
        file.close()

    def uploadBinary(self, local, remote):
        self.ftp.cwd('/public_html/swedish/mytest')
        file = open(local, 'rb')
        self.ftp.storbinary('STOR ' + remote, file)
        file.close()

    def getType(self, file):
        result = re.search('\.([a-z]*)$', file)
        try:
            ext = result.group(1)
        except AttributeError:
            ext = ''
        if ext in self.lineExts:
            return 'lines'
        else:
            return 'binary'

    def create(self, path):
        if not self.exists(path):
            self.ftp.mkd(path)

    def exists(self, path):
        return bool(len(self.ftp.nlst(path)))

    def setCwd(self, path):
        return self.ftp.cwd(path)

    def getPwd(self):
        return self.ftp.pwd()
        
