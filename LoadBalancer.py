import random
import queue
import threading
import time
import itertools
from Server import Server
from Settings import Settings
from datetime import datetime
from Windows import Windows
from Evaluation import Evaluation

class LoadBalancer:
    def __init__(self, startingServers, timeNow):
        #self.startingServers = startingServers
        self.pool = []
        self.removal_servers = []
        self.serversInfo = {}
        self.serverUpgrade = []
        self.startingServers = startingServers
        self.noOfServers = startingServers
        self.vip = "10.10.1.111"
        self.request_queue = queue.Queue()
        self.timeNow = timeNow
        self.running = True
        # daemon set to true to shut down once program exits 
        self.check_connection_time = threading.Thread(target=self.check_connection, daemon=True)
        self.utilisation_trigger = 50
        self.underutilisation_trigger = 30
        
        # check pool utilisation
        self.check_load = threading.Thread(target=self.check_utilisation, daemon=True)
        # check if temp servers can be removed
        self.check_removalservers = threading.Thread(target=self.check_removal, daemon=True)
        # check if upgrade is needed for servers
        self.checkServerUpgrade = threading.Thread(target=self.check_for_upgrade, daemon=True)
        # perform the server upgrade if reqs are at 0
        self.performUpgrade = threading.Thread(target=self.upgradeServers, daemon=True)
        self.performUpgrade.start()
        
        # Perform health check on servers
        self.healthChecks = threading.Thread(target=self.healthCheck, daemon=True)
        
        # Randomly break a server
        self.breakServer = threading.Thread(target=self.breakRandomServer, daemon=True)
        

    def add_server(self, server):
        self.pool.append(server)
        self.serversInfo[f"{server.serverId}"] = [0, True]
        

    def remove_server(self, server):
        self.pool.remove(server)
        
    def stop(self):
        self.running = False
        

    def check_server_capacity(self, server):
        
        # if server reqs is equal to max capacity then it cannot process any more requests
        if server.maxCapacity == self.serversInfo[f"{server.serverId}"][0]:
            return False
        else:
            return True
        
        

    def distribute_request(self):
        if not self.pool:
            return "No servers available"
        
        packet = self.request_queue.get()
        start_time = time.perf_counter()
        packet.start_time = start_time

        least = None
        
        for i in range(self.noOfServers):
            
            try:
                # checks to see if there is another server to compare with in the list
                if (i + 1 > self.noOfServers): #len(self.removal_servers) > 0
                    next
                
                else:
                    
                        
                    if len(self.removal_servers) > 0 or len(self.serverUpgrade) > 0:
                        
                        selected_server = self.pool[i]
                        
                        if self.checkInLists(selected_server) == True:
                            next
                        else:
                            if self.check_server_capacity(selected_server) == False:
                                next                              
                            elif least == None:
                                least = self.pool[i]
                            else:
                                if self.checkWeightedCapacity(selected_server, least) == True:
                                    least = self.pool[i]
                                else:
                                    next
                         # create function that checks if i or i + 1 is in either list 
            
                    else:
                        
                        # compare = self.pool[i+1] now comparing with current least and i 
                        selected_server = self.pool[i]
                        
                        if self.serversInfo[f"{selected_server.serverId}"][1] == False:
                            next
                        elif self.check_server_capacity(selected_server) == False:
                            next                              
                        elif least == None:
                            least = self.pool[i]
                        else:
                            if self.checkWeightedCapacity(selected_server, least) == True:
                                least = self.pool[i]
                            else:
                                next
                                           
            except:
                next
            
                         
        if least == None:
            
            return
        else:
            least.serverReqs += 1
            self.serversInfo[f"{least.serverId}"][0] +=1
            least.totalReqs += 1
            least.removalTrigger -= 1
            packet.connection_end = time.time() + float(packet.packet_size)
            packet.dest_ip = least.serverIP
            least.serverConnections.append(packet)
            logTime = time.time()
            logTime2 = datetime.fromtimestamp(logTime)
            with open("ConnectionLog.txt", "a") as writer:
                    writer.write(f"Request {packet.content} from {packet.source_ip} handled by {least.serverId} {logTime2}\n")
                    
            result, response_time = least.process_request(packet)
            Evaluation.log_response_time(packet.content, response_time)
            #return f"Request {packet.content} from {packet.source_ip} handled by {least.serverId}"
            return result
            
        
    def checkWeightedCapacity(self,selected_server,compare_server):
        
        selecServ = (self.serversInfo[f"{selected_server.serverId}"][0] / selected_server.maxCapacity) * 100
        CurrentLeastServ = (self.serversInfo[f"{compare_server.serverId}"][0] / compare_server.maxCapacity) * 100
        
        if selecServ < CurrentLeastServ:
            return True
        else:
            return False
        
    def checkInLists(self, server):
        
        if len(self.serverUpgrade) > 0:
            if server == self.serverUpgrade[0]:
                return True
            else:
                return False
            
        elif len(self.removal_servers) > 0:
            if server == self.removal_servers[0]:
                return True
            else:
                return False
        else:
            return False
        
        
        
    
    
    
    def check_connection(self):
        
        # checking connection in order to remove and free up server

        while self.running:
            
            
            
            if len(self.pool) < 1:
                pass
            else:
                for i in range(self.noOfServers):
                    
                
                    try:

                        selected_server = self.pool[i]
                        
                        values = len(selected_server.serverConnections)
                        
                        for j in range(values):
                            packet = selected_server.serverConnections[j]
                
                            if packet.connection_end < time.time():
                                selected_server.serverConnections.remove(packet)
                                selected_server.serverReqs -=1
                                self.serversInfo[f"{selected_server.serverId}"][0] -=1
                    except:
                        next
            
                     
                     
    def check_utilisation(self):

        # check server utilisation to determine if more resources are needed

        while self.running:
            #time.sleep(0.5)
            
            poolUtilisation =  self.calculate_utilisation()
        
            if poolUtilisation >= self.utilisation_trigger:
                print(f"Adding new server, Pool utilisation {poolUtilisation}")
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
        minusServers = 0
        
        try:
                
            for i in range(self.noOfServers):
                server = self.pool[i]
                
                if self.checkInLists(server) == False:
                    server.utilisation = ((self.serversInfo[f"{server.serverId}"][0] / server.maxCapacity) * 100.0)
                else: 
                    next
                    
                
        
            for server in self.pool:
                
                if self.checkInLists(server) == False and self.serversInfo[f"{server.serverId}"][1] == True:
                    poolUtilisation += server.utilisation
                else: 
                    minusServers +=1
                    next
                    
            serverNum = self.noOfServers - minusServers

            poolUtilisation = poolUtilisation/serverNum
                
        except:
            next
                
        return poolUtilisation
    

    def check_removal(self):
        while self.running:

            try:
                for i in range(len(self.removal_servers)):
                    checkRemoval = self.removal_servers[i]
                    if self.serversInfo[f"{checkRemoval.serverId}"][0] < 1 :
                        self.remove_server(checkRemoval)
                        print(f"Server removed {checkRemoval.serverId}")
                        self.removal_servers.remove(checkRemoval)
                        self.noOfServers -=1
                    else:
                        next
                

            except:
                next
                
    def check_for_upgrade(self):
        while self.running:
            
            time.sleep(1)
            
            earliest = datetime.strptime(Settings.earliestTimestr, "%I:%M%p")
            latest = datetime.strptime(Settings.latestTimestr, "%I:%M%p")
            
            
            if self.timeNow >= earliest:
                # only upgrading from the original servers as new ones are just temporary
               for i in range(self.startingServers):
                        server = self.pool[i]
                        
                        if server.serverOS == "Windows" and len(self.serverUpgrade) < 1 and server.removalTrigger < 1 and self.calculate_utilisation() < 20.0:
                            if server.serverVersion < Windows.latestStableRelease:
                                self.serverUpgrade.append(server)
                                print(f"{server.serverId} no longer accepting requests")
                            else:
                                next
                        elif server.serverOS == "Linux" and len(self.serverUpgrade) < 1:
                            break
                        
    def upgradeServers(self):
        
        while self.running:
            
            
            
            if len(self.serverUpgrade) > 0 :
                
                server = self.serverUpgrade[0]
                
                if self.serversInfo[f"{server.serverId}"][0] == 0:
                    print(f"Upgrading {server.serverId}")
                    sshAttempt = self.ssh(Settings.adminUsername, Settings.adminPassword, server)
                    
                    match sshAttempt:
                        case "SSH successful":
                            upgrade = server.serverCommandLine(Windows.updateCommand)
                            
                            if upgrade == "upgraded":
                                self.serverUpgrade.remove(server)
                                print(f"{server.serverId} successfully upgraded")
                    #server.serverVersion = Windows.latestStableRelease
                    
                else:
                    pass
            else:
                pass
            
            
    def healthCheck(self):
        
        while self.running:
            
            time.sleep(0.5)
            
            for server in self.pool:
                if self.pingServers(server) == False:
                    self.serverTroubleshooting(server)
                    return False
                    #pass
                else: 
                    next
                    
    
    def pingServers(self, server):
        
        if self.serversInfo[f"{server.serverId}"][1] == True:
            next
        else:
            #self.serversInfo[f"{server.serverId}"][1] = False
            print(f"Server Unresponsive: {server.serverId}")
            return False
            
    def breakRandomServer(self):
    
        waitTime = random.randint(4,8)
    
    
        time.sleep(waitTime)
        
        server = random.choice(self.pool)
        
        self.serversInfo[f"{server.serverId}"][1] = False
        
        
    def serverTroubleshooting(self,server):
        
        sshAttempt = self.ssh(Settings.adminUsername, Settings.adminPassword, server)
        
        routingTableCommand = "route print"
        ipConfigCommand = "IPconfig"
        
        match sshAttempt:
            case "SSH successful":
                routingTable = server.serverCommandLine(routingTableCommand)
                if len(routingTable) > 0:
                    
                    with open("troubleshooting.txt", "w") as writer:
                        for line in routingTable:
                          writer.write(line)
                else:
                    pass
                
                ipConfig = server.serverCommandLine(ipConfigCommand)
                if len(ipConfig) > 0:
                    
                    with open("troubleshooting.txt", "a") as writer:
                        writer.write("\n")
                        writer.write("\n")
                        for line in ipConfig:
                            writer.write(line)
                else:
                    pass
                
                with open('ConnectionLog.txt') as f:
                    datafile = f.readlines()
                found = False  # This isn't really necessary
                with open("troubleshooting.txt", "a") as writer:
                    writer.write("\n")
                    writer.write("\n")
                    writer.write("Last successful connections:\n")
                for line in datafile:
                    if server.serverId in line:
                        with open("troubleshooting.txt", "a") as writer:
                            writer.write("\n")
                            writer.write(line)
                            
                serverConnections = self.serversInfo[f"{server.serverId}"][0]
                serverUtilisation = format(server.utilisation, ".2f")
                
                with open("troubleshooting.txt", "a") as writer:
                    writer.write("\n")
                    writer.write("\n")
                    writer.write(f"Server Connections at time of error: {serverConnections}\n")
                    writer.write(f"Server Utilisation at time of error: {serverUtilisation}%")
                            
                    
            case "SSH unsuccessful":
                pass
        
        
        
    def ssh(self, username, password, server):
        
        loginString = f"ssh {username}@{server.serverIP}"
        
        answer = server.sshAttempt(loginString, password)
        
        return answer
        
        
        
    
    
    
       
        
        
        
        
                
        
        
        
                            
                        
                        
                        