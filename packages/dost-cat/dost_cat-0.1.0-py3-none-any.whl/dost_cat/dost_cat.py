import socket, random

class SendTo:
    def __init__(self, IP="x.x.x.x", Port=12345):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = IP
        self.Port = Port
        self.s.connect((IP, Port))
    
    def send(self):
        for i in range(1, 100*10000):
            self.s.send(random._urandom(10) * 1000)
            print(f"Send: {i}")