import random
import queue


noOfServers = random.randint(1,5)
noOfRequests = 5

class Packet:
    def __init__(self, content, ip):
        self.content = content
        self.source_ip = ip

class LoadBalancer:
    def __init__(self):
        self.pool = []
        self.request_queue = queue.Queue()

    def add_server(self, server):
        self.pool.append(server)
        

    def remove_server(self, server):
        self.pool.remove(server)

    def distribute_request(self):
        if not self.pool:
            return "No servers available"
        
        # Get the next request from the queue
        packet = self.request_queue.get()

        selected_server = random.choice(self.pool)
        selected_server.serverReqs +=1
        return f"Request {packet.content} from {packet.source_ip} handled by {selected_server.serverId}"

class Client:
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer
        self.ip_add = f"10.10.0.{random.randint(1,254)}"

    def make_request(self, content, source_ip):
        packet = Packet(content, source_ip)
        self.load_balancer.request_queue.put(packet)
        
class Server:
    def __init__(self, serverId):
        self.serverId = serverId
        self.serverReqs = 0
        

if __name__ == "__main__":
    lb = LoadBalancer()
    
        
    #for i in range(noOfServers):
    #    lb.add_server(f"Server{i+1}")
        
    for i in range(noOfServers):
        lb.add_server(Server(f"Server{i+1}"))


    client1 = Client(lb)
    client2 = Client(lb)

    # Sequential requests
    for i in range(noOfRequests):
        client1.make_request(f"Request{i+1}", client1.ip_add)
        
     # Sequential requests
    for i in range(noOfRequests):
        client2.make_request(f"Request{i+1}", client2.ip_add)

    for _ in range(noOfRequests*2):
        result = lb.distribute_request()
        print(result)
        
    for i in range(noOfServers):
        serverchoice = lb.pool[i]
        print(f"{serverchoice.serverId} no of requests {serverchoice.serverReqs}")
