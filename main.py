import random
import queue
import threading
import time
import itertools


noOfServers = 2 #random.randint(1,5)
noOfRequests = 100

class Packet:
    
    def __init__(self, content, ip, connection_id, packet_size):
        self.content = content
        self.source_ip = ip
        self.connection_end = 0.0
        self.connection_id = connection_id
        self.packet_size = packet_size

class LoadBalancer:
    def __init__(self):
        self.pool = []
        self.request_queue = queue.Queue()
        # daemon set to true to shut down once program exits 
        self.check_connection_time = threading.Thread(target=self.check_connection, daemon=True)
        self.check_connection_time.start()

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
        
        connection_end_value = [1.0,2.0,3.0,4.0,5.0,6.0,7.0,8.0,9.0]
        #connection_end_value = [120.0,122.0,125.0,127.0,129.0]
        # Get the next request from the queue
        packet = self.request_queue.get()

        #selected_server = random.choice(self.pool)
        
        #time.sleep(1)
        
        least = None
        
        for i in range(noOfServers):
            
            if(i + 1 < noOfServers):
                compare = lb.pool[i+1]
                selected_server = lb.pool[i]
            else:
                break  # "No servers are available to take your request"
            
           # compare = lb.pool[i+1]
            #selected_server = lb.pool[i]
            
            if self.check_server_capacity(selected_server, packet) == False:
                next
            elif selected_server.serverReqs > compare.serverReqs:
                least = lb.pool[i+1]
            else:
                least = lb.pool[i]
                         
        if least == None:
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
            
            
            for i in range(noOfServers):
                selected_server = lb.pool[i]
                
                try:
                    for j in range(len(selected_server.serverConnections)):
                        packet = selected_server.serverConnections[j]
                
                        if packet.connection_end < time.time():
                            selected_server.serverConnections.remove(packet)
                            selected_server.maxCapacity += packet.packet_size
                            selected_server.serverReqs -=1
                except:
                    next
                
                #if len(selected_server.serverConnections) == 0:
                 #   next
                #else:
                 #   for j in range(len(selected_server.serverConnections)):
                  #      packet = selected_server.serverConnections[j]
                
                   #     if packet.connection_end < time.time():
                    #        selected_server.serverConnections.remove(packet)
                     #       selected_server.serverReqs -=1
                        
                

class Client:
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
        self.ip_add = f"10.10.0.{random.randint(1,254)}"

    def make_request(self, content, source_ip, connection_id, packet_size):
        packet = Packet(content, source_ip, connection_id, packet_size)
        self.load_balancer.request_queue.put(packet)
        
class Server:
    def __init__(self, serverId):
        self.serverId = serverId
        self.serverReqs = 0
        self.totalReqs = 0
        self.serverConnections = []
        self.maxCapacity = 100      # This is in mb
        

if __name__ == "__main__":
    lb = LoadBalancer()
    
    startingTime = time.time()
    
    print(f"starting time {startingTime}")
    
    
    #for i in range(noOfServers):
    #    lb.add_server(f"Server{i+1}")
        
    for i in range(noOfServers):
        lb.add_server(Server(f"Server{i+1}"))


    client1 = Client(lb)
    client2 = Client(lb)
 
    
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
            lb.add_server(Server(f"Server{noOfServers + 1}"))
            noOfServers +=1
            print("Creating New Server")
            
        else:
            print(f"{result} and time {currTime}")
        
        time.sleep(1)
        
    for i in range(noOfServers):
        serverchoice = lb.pool[i]
        print(f"{serverchoice.serverId} no of requests {serverchoice.serverReqs}")
