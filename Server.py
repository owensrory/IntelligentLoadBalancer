import random
import queue
import threading
import time
import itertools
from Settings import Settings



class Server:
    def __init__(self, serverId):
        self.serverId = serverId
        self.serverIP = f"10.10.2.{random.randint(1,254)}"
        self.serverReqs = 0
        self.totalReqs = 0
        self.serverConnections = []
        self.maxCapacity = 15.0      # This is number of requests
        self.utilisation = 0.0
        self.removalTrigger = 5
        self.serverOS = Settings.serverOS
        self.serverVersion = Settings.serverVersion