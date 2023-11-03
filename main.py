import random
import queue
import threading
import time
import itertools
from LoadBalancer import LoadBalancer
from Packet import Packet
from Server import Server
from Client import Client



startingServers = 2 #random.randint(1,5)
noOfRequests = 100

        

if __name__ == "__main__":
    lb = LoadBalancer(startingServers)
    
    startingTime = time.time()
    
    print(f"starting time {startingTime}")
        
    for i in range(startingServers):
        lb.add_server(Server(f"Server{i+1}"))


    client1 = Client(lb)
    client2 = Client(lb)
    
    lb.check_load.start()
    
    id_obj = itertools.count()

    # Sequential requests
    for i in range(noOfRequests):
        
        client1.make_request(f"Request{i+1}", client1.ip_add, next(id_obj), random.randint(1,40))
        
     # Sequential requests
    for i in range(noOfRequests):
        
        client2.make_request(f"Request{i+1}", client2.ip_add, next(id_obj), random.randint(1,40))

    for _ in range(noOfRequests*2):
        currTime = time.time()
        result = lb.distribute_request()
        
        if result == None:
            #lb.add_server(Server(f"Server{noOfServers + 1}"))
            #lb.noOfServers = len(lb.pool)
            print("New Server added")
            
            
        else:
            print(f"{result} and time {currTime}")
        
        time.sleep(1)
        
        
    for i in range(lb.noOfServers):
        serverchoice = lb.pool[i]
        print(f"{serverchoice.serverId} no of requests {serverchoice.serverReqs}")
