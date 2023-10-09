import random
import queue


noOfServers = random.randint(1,5)

class Packet:
    def __init__(self, content):
        self.content = content

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
        return f"Request {packet.content} handled by {selected_server}"

class Client:
    def __init__(self, load_balancer):
        self.load_balancer = load_balancer

    def make_request(self, content):
        packet = Packet(content)
        self.load_balancer.request_queue.put(packet)

if __name__ == "__main__":
    lb = LoadBalancer()

    # Add some servers to the load balancer
    ##lb.add_server("Server1")
    ##lb.add_server("Server2")
    ##lb.add_server("Server3")
    
    
    for i in range(noOfServers):
        lb.add_server(f"Server{i+1}")


    client1 = Client(lb)
    client2 = Client(lb)

    # Sequential requests
    for i in range(5):
        client1.make_request(f"Request{i}")

    for _ in range(5):
        result = lb.distribute_request()
        print(result)
