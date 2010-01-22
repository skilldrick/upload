import unittest

from upload import Upload

class UploadTests(unittest.TestCase):
    def setUp(self):
        self.upload = Upload()

    def tearDown(self):
        self.upload.close()
    
    def testThereAreNDirs(self):
        N = 15
        self.assertEqual(N,
                         self.upload.countDirs('testdir'))

    def testLinesMode(self):
        filenames = [
            'foo.txt',
            'my test file with spaces.html',
            'index.php',
            ]
        for file in filenames:
            self.assertEqual('lines',
                             self.upload.getType(file))

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
                             self.upload.getType(file))

    def testCreateDirOnServer(self):
        self.upload.create(
            '/public_html/swedish/mytest/newdir4')
        exists = self.upload.exists(
            '/public_html/swedish/mytest/newdir4')
        self.assertTrue(exists)

    def testFakeDirOnServer(self):
        exists = self.upload.exists(
            '/public_html/thisdirwillneverexist')
        self.assertFalse(exists)

    def testDirExistsOnServer(self):
        exists1 = self.upload.exists('/public_html')
        exists2 = self.upload.exists('/public_html/')
        self.assertTrue(exists1 and exists2)
        
    def testSetCwd(self):
        path = '/public_html'
        self.upload.setCwd(path)
        pwd = self.upload.getPwd()
        self.assertEqual(path, pwd)

    def testGetLocalDirs(self):
        localRoot = 'testdir/txtfiles'
        dirs = [
            localRoot,
            localRoot + '/boring',
            localRoot + '/interesting']
        self.assertEqual(self.upload.getLocalDirs(localRoot),
                         dirs)

    """
    def testCreateDirTreeOnServer(self):
        localRoot = 'testdir'
        remoteRoot = '/public_html/testdir'
        localDirs = self.upload.getLocalDirs(localRoot)
        print(localDirs)
""" 

if __name__ == '__main__':
    unittest.main()
