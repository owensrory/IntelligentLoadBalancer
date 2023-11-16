import random
from Windows import Windows
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
        
    def process_request(self,packet):
        
        response = f"{self.serverId} processing {packet.content} from {packet.source_ip}"
        
        return response
        
    def sshAttempt(self, loginString, password):
        
        correctUsername = "admin"
        correctPassword = "admin"
        
        loginStringCompare = f"{correctUsername}@{self.serverIP}"
        
        
        match loginString:
            case loginStringCompare:
                if correctPassword == password:
                    return "SSH successful"
                else:
                    return "SSH unsuccessful"
                
              
    def serverCommandLine(self, command):
        
        
        match command:
            case "route print":
                with open("RoutingTable.txt", "r") as reader:
                    routeTable = reader.readlines()
                return routeTable
            case "IPconfig":
                with open("IPConfig.txt", "r") as reader:
                    ipconfig = reader.readlines()
                return ipconfig
            case "Wusa WindowsUpdate1.02.msu /quiet":
                upgradeAttempt = self.upgradeServer(command)
                
                if upgradeAttempt == "upgraded":
                    return "upgraded"
                
    def upgradeServer(self,command):
        
        self.serverVersion = Windows.latestStableRelease
        
        return "upgraded"
                
            
            
            
            
                
            
             
        
        