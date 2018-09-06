from src.RaspberryServer.RaspberryServer import RaspberryServer

IpAddress = "192.168.0.164"
port = 4445

server = RaspberryServer(IpAddress, port)

server.start_server()
server.start_listening()
