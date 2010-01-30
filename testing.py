import time
import os
import upload
import ftplib


uploader = upload.Uploader()

file = 'newdir/output.txt'

try:
    response = uploader.remote.ftp.sendcmd('MDTM ' + file)
    print(response)
except ftplib.error_perm:
    print('File does not exist')
