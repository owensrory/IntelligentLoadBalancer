import random
import queue
import threading
import time
import itertools

class Settings:
    
    startingServers = 2
    NoOfRequests = 100
    earliestTimestr = "11:00pm"
    latestTimestr = "6:00am"
    workingTimestr = "11:45pm"
    nonWorkingTimestr = "7:00pm"
    serverOS = "Windows"
    serverVersion = 1.01
    adminUsername = "admin"
    adminPassword = "admin"
        