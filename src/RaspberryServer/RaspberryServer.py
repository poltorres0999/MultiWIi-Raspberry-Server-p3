import struct
import socket

import _thread

from src.Multiwii.Multiwii import MultiWii


class RaspberryServer:

    # Android APP / Raspberry protocol

    START_CONNECTION = 300
    ACCEPT_CONNECTION = 302
    END_CONNECTION = 301
    ARM = 220
    DISARM = 221
    START_TELEMETRY = 120
    ACCEPT_TELEMETRY = 122
    END_TELEMETRY = 121
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
        self.telemetry_activated = False
        self.camera = ""
        self.camera_streaming_ip = ""

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

                package = self.sock.recvfrom(40)
                p = package[0]
                address = package[1]

                print("Received {} bytes".format(len(package)))

                # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.

                code = struct.unpack('>h', p[:2])[0]
                size = struct.unpack('>h', p[2:4])[0]
                data = struct.unpack('>' + 'h' * int(size / 2), p[4:size + 4])

                print("Code: {0} Size: {1} Data: {2}".format(code, size, data))

                # Determines what kind of package has received, and acts in consequence
                self.evaluate_package(code, data, address)

    @staticmethod
    def __create_package(code, size, data):
        # '>' for BigEndian encoding , change to < for LittleEndian, or @ for native.
        code = struct.pack('>h', code)
        size = struct.pack('>h', size)
        data = struct.pack('>' + 'h' * len(data), *data)
        package = code + size + data

        print("Package created -> " + str(package))

        return package

    def evaluate_package(self, code, data, address):

        if int(str(code)[:1]) == 3:
            self.server_config_package(code, address)

        if int(str(code)[:1]) == 2:
            self.drone_control_packages(code, data)

        if int(str(code)[:1]) == 1:
            self.drone_telemetry_package(code, address)

    # covers the basic packages for communication and server configuration

    def server_config_package(self, code, address):

        if code == self.START_CONNECTION:
            self.sock.sendto(self.__create_package(self.ACCEPT_CONNECTION, 2, [0]),
                             address)
            print("Start connection package sent!")

        if code == self.END_CONNECTION:
            self.sock.close()
            self.server_started = False
            print("Connection finished!")

    # covers the packages used to control the drone (arm, disarm, rc, ...)

    def drone_control_packages(self, code, data):

        if code == self.ARM:
            self.mw.arm()
            print("Received ARM command")

        if code == self.DISARM:
            self.mw.disarm()
            print("Received DISARM command")

        if code == self.SET_RC:
            self.mw.set_rc(list(data))
            print("Received SET_RC command, values: " + str(data))

    # covers the packages used to receive information about the drone state (altitude, acc, gyro, ...)

    def drone_telemetry_package(self, code, address):

        if code == self.START_TELEMETRY:

            if not self.telemetry_activated:
                self.sock.sendto(self.__create_package(self.ACCEPT_TELEMETRY, 1, [0]),
                                 address)
                # creates a new thread to manage the telemetry loop
                t = _thread.start_new_thread(self.mw.udp_telemetry_loop, ())

                if not t:
                    print("Error: MultiWii udp connection not started")

                print("Telemetry thread started!")

        if code == self.END_TELEMETRY:
            self.mw.stop_udp_telemetry()
            print("Stop telemetry command received!")

        if code == self.ALTITUDE:
            self.mw.udp_get_altitude()
            print("Received get_altitude command!, values: " + str(self.mw.drone.altitude))

        if code == self.ATTITUDE:
            self.mw.udp_get_attitude()
            print("Received get_attitude command!, values: " + str(self.mw.drone.attitude))

        if code == self.RAW_IMU:
            self.mw.udp_get_raw_imu()
            print("Received get_raw_imu command!, values: " + str(self.mw.drone.raw_imu))

        if code == self.RC:
            self.mw.udp_get_rc()
            print("Received get_rc command!, values: " + str(self.mw.drone.rc_channels))

        if code == self.SERVO:
            self.mw.get_servo()
            print("Received get_servo command!, values: " + str(self.mw.drone.servo))

        if code == self.MOTOR:
            self.mw.get_motor()
            print("Received get_motor command!, values: " + str(self.mw.drone.motor))

