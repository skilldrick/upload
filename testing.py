import upload
import time
import datetime


uploader = upload.Uploader()

modtime = uploader.local.getTime('.lastrun')
now = int(time.strftime('%Y%m%d%H%M%S', time.localtime()))

print(now - modtime)
