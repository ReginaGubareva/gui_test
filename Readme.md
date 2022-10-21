This is a neural network for training searching for the bugs in user interface. 
It is based on Juha Eskonen master thesis, a couple of papers and actor-critic algortihm of the reinforcement learning. 


The main info in testing.py file. To launch the project use testing.py file. 

Before launch: pip install requirements.txt
Download the chromedriver and put it inside D:\ directory.
Download TesseractOCR
Change the link of the website go to environment.py
To launch centroids detection command:

python detect.py --source resources/test_images --weights weights/last.pt --conf 0.25

Dont' need to launch this commnad, it is enough just to launch main
and uncomment the code in detect.py file.

Before starting need to download new version of chromedriver and put to 
the directory "D:\chromedriver.exe"

