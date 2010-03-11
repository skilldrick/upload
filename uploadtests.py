import unittest

import upload
import os


class UploaderTests(unittest.TestCase):
    def setUp(self):
        self.uploader = upload.Uploader()
        
    def testCreateDirTreeOnServer(self):
        localRoot = 'testdir'
        remoteRoot = 'testdir'
        success = self.uploader.createDirs(localRoot,
                                           remoteRoot)
        self.assertTrue(success)

    def testUploadAllFiles(self):
        localRoot = 'testdir'
        remoteRoot = 'testdir'
        success = self.uploader.uploadFiles(localRoot,
                                            remoteRoot)
        self.assertTrue(success)

    def testReadWriteLastRun(self):
        lastrun1 = self.uploader.readLastRun()
        self.uploader.writeLastRun(lastrun1 - 1)
        lastrun2 = self.uploader.readLastRun()
        self.assertEqual(lastrun1 - 1, lastrun2)

    def testUploadEmptyLines(self):
        localFile = os.path.join('testdir',
                                'misc',
                                'empty.txt',)
        remoteFile = 'testdir/misc/empty.txt'
        self.uploader.remote.upload(localFile,
                                    remoteFile)
        self.assertTrue(self.uploader.checkEmpty(localFile, remoteFile))
        




class LocalTests(unittest.TestCase):
    def setUp(self):
        self.local = upload.Local()

    def testThereAreNDirs(self):
        N = 10
        self.assertEqual(N,
                         self.local.countDirs('testdir'))

    def testGetLocalDirs(self):
        s = os.sep
        localRoot = 'testdir' + s + 'txtfiles'
        dirs = ['', 'boring', 'interesting']
        self.assertEqual(list(self.local.getLocalDirs(localRoot)),
                         dirs)

    def testGetLocalLeaves(self):
        s = os.sep
        localRoot = os.path.join('testdir', 'txtfiles')
        dirs = ['boring', 'interesting']
        self.assertEqual(list(self.local.getLocalDirs(localRoot,
                                                      True)),
                         dirs)

    def testSizeOfLocalFile(self):
        assumedSize = 165
        filename = os.path.join('testdir',
                                'txtfiles',
                                'boring',
                                'log.txt',)
        actualSize = self.local.getSize(filename)
        self.assertEqual(assumedSize, actualSize)

    def testGetLocalFiles(self):
        files = self.local.getLocalFiles('testdir')
        count = len(list(files))
        self.assertEqual(count, 14)

    
class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.remote = upload.Remote('ftp.skilldrick.co.uk')

    def tearDown(self):
        self.remote.close()
    
    def testLinesMode(self):
        filenames = [
            'foo.txt',
            'my test file with spaces.html',
            'index.php',
            ]
        for filename in filenames:
            self.assertEqual('lines',
                             self.remote.getType(filename))

    def testBinaryMode(self):
        filenames = [
            'a nice image.png',
            'something1.gif',
            'this.has.dots.in.jpg',
            'th1s_has_underscor3s_and_numbers42.jpeg',
            'noextensionatall',
            ]
        for filename in filenames:
            self.assertEqual('binary',
                             self.remote.getType(filename))

    def testCreateDirOnServer(self):
        self.remote.create(
            '/public_html/swedish/mytest/newdir4')
        exists = self.remote.exists(
            '/public_html/swedish/mytest', 'newdir4')
        self.assertTrue(exists)

    def testFakeDirOnServer(self):
        exists = self.remote.exists(
            '/public_html', 'thisdirwillneverexist')
        self.assertFalse(exists)

    def testDirExistsOnServer(self):
        exists1 = self.remote.exists('/public_html')
        exists2 = self.remote.exists('/public_html/')
        self.assertTrue(exists1 and exists2)
        
    def testSetCwd(self):
        path = '/public_html'
        self.remote.setCwd(path)
        pwd = self.remote.getPwd()
        self.assertEqual(path, pwd)

    def testSizeOfRemoteFile(self):
        assumedSize = 165
        filename = 'testdir/txtfiles/boring/log.txt'
        actualSize = self.remote.getSize(filename)
        self.assertEqual(assumedSize, actualSize)
        
    def testUploadLines(self):
        filename = os.path.join('testdir',
                                'txtfiles',
                                'boring',
                                'log.txt',)
        self.remote.upload(filename,
                           'testdir/txtfiles/boring/log.txt')

    def testUploadBinary(self):
        filename = os.path.join('testdir',
                                'misc',
                                'animals',
                                'cat2.jpg',)
        self.remote.upload(filename,
                           'testdir/misc/animals/cat2.jpg')

    
if __name__ == '__main__':
    unittest.main()
