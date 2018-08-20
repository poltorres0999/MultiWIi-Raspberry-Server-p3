from src.RaspberryServer.RaspberryServer import RaspberryServer

server = RaspberryServer("192.168.0.164", 4445)

server.start_server()
server.start_listening()

