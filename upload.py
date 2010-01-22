#!/usr/local/bin/python3.1

from ftplib import FTP
import os
import re
import netrc



class Upload:
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
        except SomeError:
            homedir = os.path.expanduser('~') + '\\Application Data\\'
            x = netrc.netrc(homedir + '.netrc')
        info = x.authenticators(self.site)
        self.user = info[0]
        self.passwd = info[2]
        self.ftp = FTP(self.site)
        self.ftp.login(user=self.user, passwd=self.passwd)

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

    #uploadAscii('githelp.txt', 'githelp.txt')
    #uploadBinary('logo2.png', 'logo3.png')


    def traverse(self):
        count = 0
        for root, dirs, files in os.walk('test'):
            if '.git' not in root:
                print(root, dirs)
                count += 1
        print(count)


    def countDirs(self, dir):
        count = 0
        for x in os.walk(dir):
            count += 1
        return count

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
        
