import random
import queue
import threading
import time
import itertools
from LoadBalancer import LoadBalancer
from Packet import Packet
from Server import Server
from Client import Client
from Settings import Settings
from datetime import datetime
from Evaluation import Evaluation



#startingServers = 5 #random.randint(1,5)
#noOfRequests = 100
timeWorking = datetime.strptime(Settings.workingTimestr, "%I:%M%p")
timeNotWorking = datetime.strptime(Settings.nonWorkingTimestr, "%I:%M%p")

        

if __name__ == "__main__":
    lb = LoadBalancer(Settings.startingServers, timeWorking)
    
    startingTime = time.time()
    
    print(f"starting time {startingTime}")
        
    for i in range(Settings.startingServers):
        lb.add_server(Server(f"Server{i+1}"))


    client1 = Client(lb)
    client2 = Client(lb)
    
    lb.check_connection_time.start()
    lb.check_load.start()
    #lb.check_removalservers.start()
    #lb.checkServerUpgrade.start()
    lb.healthChecks.start()
    
    
    id_obj = itertools.count()

    # Sequential requests
    for i in range(Settings.NoOfRequests):
        
        client1.make_request(f"Request{i+1}", client1.ip_add, next(id_obj), random.randint(1,40), lb.vip)
        
     # Sequential requests
    for i in range(Settings.NoOfRequests):
        
        client2.make_request(f"Request{i+1}", client2.ip_add, next(id_obj), random.randint(1,40), lb.vip)
        
    
    #lb.breakServer.start()

         
    while lb.request_queue:
        currTime = time.time()
        result = lb.distribute_request()

        if result is None:
            print("No response")
        else:
            print(f"{result} and time {currTime}")
        
        
        
        
    for i in range(lb.noOfServers):
        serverchoice = lb.pool[i]
        print(f"{serverchoice.serverId} no of requests {serverchoice.serverReqs}")
        
    lb.stop()
        
    # Create an instance of Evaluation and plot the response times
    
    
    
