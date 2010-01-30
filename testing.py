import time
import os
import upload


uploader = upload.Uploader()

remoteFile = 'testdir/txtfiles/boring/other.txt'
localFile = 'testdir/txtfiles/boring/other.txt'
remoteTime = uploader.remote.ftp.sendcmd('MDTM ' + remoteFile)
remoteTime = int(remoteTime[4:])
localTime = os.path.getmtime(localFile)
localTime = time.gmtime(localTime)
localTime = int(time.strftime('%Y%m%d%H%M%S', localTime))
print(localTime >= remoteTime)

