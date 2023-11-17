import random
import queue
import threading
import time
import itertools
from Packet import Packet


class Client:
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
        self.ip_add = f"10.10.0.{random.randint(1,254)}"

    def make_request(self, content, source_ip, connection_id, packet_size, dest_ip):
        
        
        packet = Packet( content, source_ip, connection_id, packet_size, dest_ip)
        
        self.load_balancer.request_queue.append(packet)