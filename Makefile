default :
	python3.1 upload.py -v

test :
	python3.1 uploadtests.py

profile :
	python3.1 -m cProfile -s cumulative uploadtests.py
