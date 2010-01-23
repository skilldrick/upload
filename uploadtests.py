import unittest

import upload
import os


class UploaderTests(unittest.TestCase):
    def setUp(self):
        self.uploader = upload.Uploader()
        
    def testCreateDirTreeOnServer(self):
        localRoot = 'testdir'
        remoteRoot = '/public_html'
        success = self.uploader.createDirs(localRoot,
                                           remoteRoot)
        self.assertTrue(success)
        

class LocalTests(unittest.TestCase):
    def setUp(self):
        self.local = upload.Local()

    def testThereAreNDirs(self):
        N = 15
        self.assertEqual(N,
                         self.local.countDirs('testdir'))

    def testGetLocalDirs(self):
        s = os.sep
        localRoot = 'testdir' + s + 'txtfiles'
        dirs = [
            localRoot,
            localRoot + s + 'boring',
            localRoot + s + 'interesting']
        self.assertEqual(self.local.getLocalDirs(localRoot),
                         dirs)

    def testGetLocalLeaves(self):
        s = os.sep
        localRoot = 'testdir' + s + 'txtfiles'
        dirs = [
            localRoot + s + 'boring',
            localRoot + s + 'interesting']
        self.assertEqual(self.local.getLocalDirs(localRoot,
                                                 True),
                         dirs)

    def testSizeOfLocalFile(self):
        assumedSize = 165
        s = os.sep
        file = os.path.join('testdir',
                            'txtfiles',
                            'boring',
                            'log.txt',)
        actualSize = self.local.getSize(file)
        self.assertEqual(assumedSize, actualSize)

    
class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.remote = upload.Remote()

    def tearDown(self):
        self.remote.close()
    
    def testLinesMode(self):
        filenames = [
            'foo.txt',
            'my test file with spaces.html',
            'index.php',
            ]
        for file in filenames:
            self.assertEqual('lines',
                             self.remote.getType(file))

    def testBinaryMode(self):
        filenames = [
            'a nice image.png',
            'something1.gif',
            'this.has.dots.in.jpg',
            'th1s_has_underscor3s_and_numbers42.jpeg',
            'noextensionatall',
            ]
        for file in filenames:
            self.assertEqual('binary',
                             self.remote.getType(file))

    def testCreateDirOnServer(self):
        self.remote.create(
            '/public_html/swedish/mytest/newdir4')
        exists = self.remote.exists(
            '/public_html/swedish/mytest/newdir4')
        self.assertTrue(exists)

    def testFakeDirOnServer(self):
        exists = self.remote.exists(
            '/public_html/thisdirwillneverexist')
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

    #def testSizeOfRemoteFile(self):

    
if __name__ == '__main__':
    unittest.main()
