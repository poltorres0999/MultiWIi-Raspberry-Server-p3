import struct
from socket import socket

from src.Multiwii.Multiwii import MultiWii



class RaspberryServer:

    # Android APP / Raspberry protocol

    START_CONNECTION = 300
    END_CONNECTION = 301
    ARM = 302
    DISARM = 303
    START_TELEMETRY = 304
    END_TELEMETRY = 305
    RAW_IMU = 102
    SERVO = 103
    MOTOR = 104
    RC = 105
    ATTITUDE = 108
    ALTITUDE = 109
    SET_RC = 200

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.address = (self.ip_address, self.port)
        self.mw = MultiWii()
        self.sock = ""
        self.server_started = False

    def start_server(self):

        if not self.server_started:

            try:
                print("Starting server ...")
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("Socket creation: Socket created!")
                self.sock.bind(self.address)
                print("Socket binding: Socket bound!")
                self.server_started = True
                print("Server started!")

            except socket.error as err:
                print("Error starting server: {}".format(err))

    def start_listening(self):

        if self.server_started:
            print("Start listening, waiting for data")
            while self.server_started:

                package = self.sock.receive(40)

                print("Received {} bytes".format(len(package)))

                code = struct.unpack('<h', package[:2])[0]
                size = struct.unpack('<h', package[2:4])[0]
                data = struct.unpack('<' + 'h' * int(size / 2), package[4:size + 4])

                print("Code: {0} Size: {1} Data: {2}".format(code, size, data))

                # Determines what kind of package has received, and acts in consequence

                if code == self.START_CONNECTION:
                    self.sock.sendto(self.__create_package(self.START_CONNECTION, 1, 0),
                                     self.mw.settings.address,)

                if code == self.END_CONNECTION:
                    self.sock.close()
                    self.server_started = False

                if code == self.ARM:
                    self.mw.arm()

                if code == self.DISARM:
                    self.mw.disarm()

                if code == self.SET_RC:
                    self.mw.set_rc(list(data))

    @staticmethod
    def __create_package(code, size, data):

        code = struct.pack('<h', code)
        size = struct.pack('<h', size)
        data = struct.pack('<' + 'h' * len(data), *data)
        package = code + size + data

        return package











