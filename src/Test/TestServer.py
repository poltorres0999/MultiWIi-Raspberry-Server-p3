from src.RaspberryServer.RaspberryServer import RaspberryServer

server = RaspberryServer("192.168.1.38", 4445)

server.start_server()
server.start_listening()

