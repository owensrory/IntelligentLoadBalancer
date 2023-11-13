import random
import queue
import threading
import time
import itertools

class Windows:
    
    latestStableRelease = 1.02
    latestStableFileName = "WindowsUpdate1.02.msu"
    updateCommand = "Wusa WindowsUpdate1.02.msu /quiet"