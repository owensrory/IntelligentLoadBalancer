import random
import queue
import threading
import time
import itertools
from Server import Server

class LoadBalancer:
    def __init__(self, startingServers):
        #self.startingServers = startingServers
        self.pool = []
        self.removal_servers = []
        self.startingServers = startingServers
        self.noOfServers = startingServers
        self.vip = "10.10.1.111"
        self.request_queue = queue.Queue()
        # daemon set to true to shut down once program exits 
        self.check_connection_time = threading.Thread(target=self.check_connection, daemon=True)
        self.check_connection_time.start()
        self.utilisation_trigger = 50
        self.underutilisation_trigger = 30
        self.check_load = threading.Thread(target=self.check_utilisation, daemon=True)
        #self.check_load.start()
        self.check_removalservers = threading.Thread(target=self.check_removal, daemon=True)

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
            
            if (i + 1 < self.noOfServers) and len(self.removal_servers) > 0 and self.pool[i+1] == self.removal_servers[0]:
                break
            elif(i + 1 < self.noOfServers):
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
            
            return
        else:
            least.serverReqs +=1
            least.totalReqs += 1
            least.maxCapacity -= packet.packet_size
            packet.connection_end = time.time() + float(packet.packet_size)
            packet.dest_ip = least.serverIP
            least.serverConnections.append(packet)
            return f"Request {packet.content} from {packet.source_ip} handled by {least.serverId}"
            
        
    
    
    
    def check_connection(self):
        
        # checking connection in order to remove and free up server

        while True:
            time.sleep(0.25)
            
            
            if len(self.pool) < 1:
                return
            else:
                for i in range(self.noOfServers):
                    
                
                    try:

                        selected_server = self.pool[i]
                        for j in range(len(selected_server.serverConnections)):
                            packet = selected_server.serverConnections[j]
                
                            if packet.connection_end < time.time():
                                selected_server.serverConnections.remove(packet)
                                selected_server.maxCapacity += packet.packet_size
                                selected_server.serverReqs -=1
                    except:
                        next
            
                     
                     
    def check_utilisation(self):

        # check server utilisation to determine if more resources are needed

        while True:
            time.sleep(0.5)
            
            poolUtilisation =  self.calculate_utilisation()
        
            if poolUtilisation >= self.utilisation_trigger:
            
                print("Adding new server")
                self.add_server(Server(f"Server{self.noOfServers + 1}"))
                self.noOfServers +=1
            elif self.underutilisation_trigger <= poolUtilisation and self.noOfServers > self.startingServers:
                removal = self.pool[self.noOfServers -1]
                if removal not in self.removal_servers:
                    self.removal_servers.append(removal)
                
                
        
                
                
    def calculate_utilisation(self):
        
        # Perform calculation to get utilisation value

        poolUtilisation = 0
        try:
                
            for i in range(self.noOfServers):
                server = self.pool[i]
                server.utilisation = ((server.maxCapacity / 200.0) * 100.0)
        
            for server in self.pool:
                poolUtilisation += server.utilisation

            poolUtilisation = poolUtilisation/self.noOfServers
                
        except:
            next
                
        return poolUtilisation
    

    def check_removal(self):
        while True:

            try:
                for i in range(len(self.removal_servers)):
                 checkRemoval = self.removal_servers[i]
                 if checkRemoval.serverReqs < 1 :
                    self.remove_server(checkRemoval)
                    self.removal_servers.remove(checkRemoval)
                    self.noOfServers -=1

            except:
                next