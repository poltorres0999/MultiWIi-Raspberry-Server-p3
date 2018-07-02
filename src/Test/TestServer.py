from src.RaspberryServer.RaspberryServer import RaspberryServer

server = RaspberryServer("127.0.0.1", 4446)

server.start_server()
server.start_listening()

