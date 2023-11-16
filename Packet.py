import random
import queue
import threading
import time
import itertools


class Packet:
    
    def __init__(self, content, ip, connection_id, packet_size, dest_ip):
        #self.traffic_type = trafficType
        self.content = content
        self.source_ip = ip
        self.connection_end = 0.0
        self.connection_id = connection_id
        self.packet_size = packet_size
        self.dest_ip = dest_ip