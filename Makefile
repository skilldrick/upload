default :
	upload.py -vfs

test :
	python3.1 uploadtests.py

profile :
	python3.1 -m cProfile -s cumulative uploadtests.py
