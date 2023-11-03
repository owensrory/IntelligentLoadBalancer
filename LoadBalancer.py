import random
import queue
import threading
import time
import itertools
from Server import Server

class LoadBalancer:
    def __init__(self, startingServers):
        self.startingServers = startingServers
        self.pool = []
        self.noOfServers = startingServers
        self.request_queue = queue.Queue()
        # daemon set to true to shut down once program exits 
        self.check_connection_time = threading.Thread(target=self.check_connection, daemon=True)
        self.check_connection_time.start()
        self.utilisation_trigger = 50
        self.check_load = threading.Thread(target=self.check_utilisation, daemon=True)
        #self.check_load.start()

    def add_server(self, server):
        self.pool.append(server)
        

    def remove_server(self, server):
        self.pool.remove(server)
        

    def check_server_capacity(self, server, packet):
        
        if (server.maxCapacity - packet.packet_size) <= 0:
            return False
        else:
            return True
        
        

    def distribute_request(self):
        if not self.pool:
            return "No servers available"
        
        packet = self.request_queue.get()

        #selected_server = random.choice(self.pool)
        
        #time.sleep(1)
        
        least = None
        
        for i in range(self.noOfServers):
            
            if(i + 1 < self.noOfServers):
                compare = self.pool[i+1]
                selected_server = self.pool[i]
            else:
                break  
            
            
            if self.check_server_capacity(selected_server, packet) == False:
                next
            elif selected_server.serverReqs > compare.serverReqs:
                least = self.pool[i+1]
            else:
                least = self.pool[i]
                         
        if least == None:
            #self.add_server(Server(f"Server{self.noOfServers+1}"))
            
            return
        else:
            least.serverReqs +=1
            least.totalReqs += 1
            least.maxCapacity -= packet.packet_size
            packet.connection_end = time.time() + float(packet.packet_size)
            least.serverConnections.append(packet)
            return f"Request {packet.content} from {packet.source_ip} handled by {least.serverId}"
            
        
    
    
    
    def check_connection(self):
        
        while True:
            time.sleep(0.25)
            
            
            if len(self.pool) < 1:
                return
            else:
                for i in range(self.noOfServers):
                    selected_server = self.pool[i]
                
                    try:
                        for j in range(len(selected_server.serverConnections)):
                            packet = selected_server.serverConnections[j]
                
                            if packet.connection_end < time.time():
                                selected_server.serverConnections.remove(packet)
                                selected_server.maxCapacity += packet.packet_size
                                selected_server.serverReqs -=1
                    except:
                        next
            
                     
                     
    def check_utilisation(self):
        while True:
           # time.sleep(0.25)
            
            poolUtilisation =  self.calculate_utilisation()
        
            if poolUtilisation >= self.utilisation_trigger:
            
                print("\nAdding new server")
                self.add_server(Server(f"Server{self.noOfServers + 1}"))
                self.noOfServers +=1
                
        
                
                
    def calculate_utilisation(self):
        
        poolUtilisation = 0
        try:
                
            for i in range(self.noOfServers):
                server = self.pool[i]
                server.utilisation = ((100.0 - server.maxCapacity) / 100.0) * 100.0
        
            for server in self.pool:
                poolUtilisation += server.utilisation
                
        except:
            next
                
        return poolUtilisation