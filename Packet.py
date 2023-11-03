import random
import queue
import threading
import time
import itertools


class Packet:
    
    def __init__(self, content, ip, connection_id, packet_size):
        self.content = content
        self.source_ip = ip
        self.connection_end = 0.0
        self.connection_id = connection_id
        self.packet_size = packet_size