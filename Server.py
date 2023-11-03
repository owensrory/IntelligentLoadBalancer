import random
import queue
import threading
import time
import itertools



class Server:
    def __init__(self, serverId):
        self.serverId = serverId
        self.serverIP = f"10.10.2.{random.randint(1,254)}"
        self.serverReqs = 0
        self.totalReqs = 0
        self.serverConnections = []
        self.maxCapacity = 200.0      # This is in mb
        self.utilisation = 0.0