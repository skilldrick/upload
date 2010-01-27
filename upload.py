#!/usr/local/bin/python3.1

from ftplib import FTP
import os
import re
import netrc
import optparse

import settings

class Uploader:
    def __init__(self, site=settings.site, verbose=False):
        self.verbose = verbose
        self.local = Local()
        self.remote = Remote(site)

    def createDirs(self, localRoot, remoteRoot):
        success = True
        for dir in self.local.getLocalDirs(localRoot):
            remoteDir = self.remote.makeUnix(dir)
            remoteDir = remoteRoot + '/' + remoteDir
            self.remote.create(remoteDir)
        for dir in self.local.getLocalDirs(localRoot, True):
            remoteDir = self.remote.makeUnix(dir)
            if not self.remote.exists(remoteDir):
                success = False
        if self.verbose and success:
            print('Directories created successfully')
        elif self.verbose:
            print('Error creating directories')
        return success

    def uploadFiles(self, localRoot, remoteRoot):
        files = self.local.getLocalFiles(localRoot)
        for localPath in files:
            remotePath = self.remote.makeUnix(localPath)
            remotePath =  remoteRoot + '/' + remotePath
            localSize = self.local.getSize(localPath)
            if self.remote.exists(remotePath):
                remoteSize = self.remote.getSize(remotePath)
            else:
                remoteSize = -1
            if not localSize == remoteSize:
                if self.verbose:
                    print('Uploading', localPath)
                self.remote.upload(localPath, remotePath)
            else:
                if self.verbose:
                    print('Skipping', localPath)
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

    def create(self, dir):
        dir = self.makeUnix(dir)
        if not self.exists(dir):
            self.ftp.mkd(dir)

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

    def stripSlash(self, path):
        return path.rstrip('/')

    def makeUnix(self, path):
        return path.replace('\\', '/')



if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-v", "--verbose", action="store_true")
    options, args = parser.parse_args()

    if options.verbose and args:
        uploader = Uploader(site=args[0], verbose=True)
    elif options.verbose:
        uploader = Uploader(verbose=True)
    else:
        uploader = Uploader()

    uploader.createDirs(settings.localDir,
                        settings.remoteDir)
    uploader.uploadFiles(settings.localDir,
                         settings.remoteDir)
