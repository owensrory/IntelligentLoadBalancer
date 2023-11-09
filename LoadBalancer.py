import random
import queue
import threading
import time
import itertools
from Server import Server
from Settings import Settings
from datetime import datetime
from Windows import Windows

class LoadBalancer:
    def __init__(self, startingServers, timeNow):
        #self.startingServers = startingServers
        self.pool = []
        self.removal_servers = []
        self.serverUpgrade = []
        self.startingServers = startingServers
        self.noOfServers = startingServers
        self.vip = "10.10.1.111"
        self.request_queue = queue.Queue()
        self.timeNow = timeNow
        # daemon set to true to shut down once program exits 
        self.check_connection_time = threading.Thread(target=self.check_connection, daemon=True)
        self.check_connection_time.start()
        self.utilisation_trigger = 50
        self.underutilisation_trigger = 30
        self.check_load = threading.Thread(target=self.check_utilisation, daemon=True)
        #self.check_load.start()
        self.check_removalservers = threading.Thread(target=self.check_removal, daemon=True)
        self.checkServerUpgrade = threading.Thread(target=self.check_for_upgrade, daemon=True)
        self.checkServerUpgrade.start()
        self.performUpgrade = threading.Thread(target=self.upgradeServers, daemon=True)
        self.performUpgrade.start()

    def add_server(self, server):
        self.pool.append(server)
        

    def remove_server(self, server):
        self.pool.remove(server)
        

    def check_server_capacity(self, server):
        
        # if sever reqs is equal to max capacity then it cannot process any more requests
        if server.maxCapacity == server.serverReqs:
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
            
            try:
                if (i + 1 > self.noOfServers): #len(self.removal_servers) > 0
                    next
                elif(i + 1 < self.noOfServers) and len(self.removal_servers) > 0 and len(self.upgradeServers) > 0:
                    
                    if self.pool[i] == self.serverUpgrade[0] or self.pool[i+1] == self.serverUpgrade[0] or self.pool[i+1] == self.removal_servers[0]:
                        next
                    else:
                        compare = self.pool[i+1]
                        selected_server = self.pool[i]
                else:
                    compare = self.pool[i+1]
                    selected_server = self.pool[i]  
            
            
                if self.check_server_capacity(selected_server) == False:
                 next
                elif self.checkWeightedCapacity(selected_server, compare) == True:                   #selected_server.serverReqs > compare.serverReqs:
                # least = self.pool[i]
                
                    if least == None:
                     least = self.pool[i]
                    elif selected_server.serverReqs < least.serverReqs:
                        least = self.pool[i]
                    else:
                        next 
                else:
                    least = self.pool[i+1]
            except:
                next
            
                         
        if least == None:
            
            return
        else:
            least.serverReqs += 1
            least.totalReqs += 1
            least.removalTrigger -= 1
            packet.connection_end = time.time() + float(packet.packet_size)
            packet.dest_ip = least.serverIP
            least.serverConnections.append(packet)
            return f"Request {packet.content} from {packet.source_ip} handled by {least.serverId}"
            
        
    def checkWeightedCapacity(self,selected_server,compare_server):
        
        selecServ = (selected_server.serverReqs / selected_server.maxCapacity) * 100
        compareServ = (compare_server.serverReqs / compare_server.maxCapacity) * 100
        
        if selecServ <= compareServ:
            return True
        else:
            return False
        
    
    
    
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
            elif poolUtilisation <= self.underutilisation_trigger and self.noOfServers > self.startingServers:
                
                try:
                    removal = self.pool[self.noOfServers - 1]
                
                    if removal.removalTrigger > 0:
                        next
                    elif removal not in self.removal_servers:
                        self.removal_servers.append(removal)
                except:
                    next
                
                
                
        
                
                
    def calculate_utilisation(self):
        
        # Perform calculation to get utilisation value

        poolUtilisation = 0
        
        try:
                
            for i in range(self.noOfServers):
                server = self.pool[i]
                server.utilisation = ((server.serverReqs / server.maxCapacity) * 100.0)
        
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
                        print("Server removed")
                        self.removal_servers.remove(checkRemoval)
                        self.noOfServers -=1
                    else:
                        next
                

            except:
                next
                
    def check_for_upgrade(self):
        while True:
            
            time.sleep(1)
            
            earliest = datetime.strptime(Settings.earliestTimestr, "%I:%M%p")
            latest = datetime.strptime(Settings.latestTimestr, "%I:%M%p")
            
            
            if self.timeNow >= earliest:
               for i in range(self.noOfServers):
                        server = self.pool[i]
                        
                        if server.serverOS == "Windows" and len(self.serverUpgrade) < 1:
                            if server.serverVersion < Windows.latestStableRelease:
                                self.serverUpgrade.append(server)
                            else:
                                next
                        elif server.serverOS == "Linux" and len(self.serverUpgrade) < 1:
                            break
                        
    def upgradeServers(self):
        
        while True:
            
            time.sleep(0.25)
            
            if len(self.serverUpgrade) > 0 :
                
                server = self.serverUpgrade[0]
                
                if server.serverReqs == 0:
                    server.serverVersion = Windows.latestStableRelease
                else:
                    break
            else:
                break
        
        
        
                            
                        
                        
                        