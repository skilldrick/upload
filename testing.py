import upload

uploader = upload.Uploader()

for i in uploader.local.getLocalDirs('testdir'):
    print(i)

print()
print()
print()
    
for i in uploader.local.getLocalFiles('.'):
    print(i)
