default :
	upload.py -vfs

test :
	python2.6 uploadtests.py

profile :
	python2.6 -m cProfile -s cumulative uploadtests.py
