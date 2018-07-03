import socket
import time
import _thread
import struct

from src.Multiwii.Multiwii import MultiWii


class Test:

    def __init__(self):
        self.mw = MultiWii()

    def test_altitude(self):

        altitude = self.mw.get_altitude()

        self.__print_altitude(altitude)

    def test_attitude(self):

        attitude = self.mw.get_attitude()

        self.__print_attitude(attitude)

    def test_raw_imu(self):

        raw_imu = self.mw.get_raw_imu()

        self.__print_raw_imu(raw_imu)

    def test_pid_coef(self):

        pid_coef = self.mw.get_pid_coef()

        self.__print_pid_coef(pid_coef)

    def test_motor(self):

        motor = self.mw.get_motor()

        self.__print_motor(motor)

    def test_servo(self):

        servo = self.mw.get_servo()

        self.__print_servo(servo)

    def test_get_rc(self):

        rc = self.mw.get_rc()

        self.__print_rc(rc)

    def test_set_rc(self, roll, pitch, yaw, throttle):

        self.mw.set_rc([roll, pitch, yaw, throttle])

        self.test_get_rc()

    def test_telemetry(self, duration):

        _thread.start_new_thread(self.mw.telemetry_loop, ())

        time_start = time.time()

        while time.time() - time_start < duration:

            if self.mw.settings.MSP_ALTITUDE:
                alt = self.mw.drone.altitude

                self.__print_altitude(alt)

            if self.mw.settings.MSP_ATTITUDE:
                att = self.mw.drone.attitude

                self.__print_attitude(att)

            if self.mw.settings.MSP_RAW_IMU:
                raw_imu = self.mw.drone.raw_imu

                self.__print_raw_imu(raw_imu)

            if self.mw.settings.MSP_RC:
                rc = self.mw.drone.rc_channels

                self.__print_rc(rc)

            if self.mw.settings.MSP_PID:
                pid = self.mw.drone.PID_coef

                self.__print_pid_coef(pid)

            if self.mw.settings.MSP_MOTOR:
                mo = self.mw.drone.motor

                self.__print_motor(mo)

            if self.mw.settings.MSP_SERVO:
                se = self.mw.drone.servo

                self.__print_servo(se)

            time.sleep(self.mw.settings.TELEMETRY_TIME)

        self.mw.stop_telemetry()

    def test_udp_telemetry(self, duration):

        server_started = False

        try:
            address = self.mw.settings.address
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print("Socket creation: Socket created!")
            sock.bind(address)
            print("Socket binding: Socket bound!")
            server_started = True
            print("Sever started")

        except socket.error as err:
            print("Error starting server: {}".format(err))

        if server_started:

            t = _thread.start_new_thread(self.mw.udp_telemetry_loop, ())

            if not t:
                print("Error: MultiWii server not started")
            else:
                time_start = time.time()

                while time.time() - time_start < duration:

                    data = sock.recv(40)

                    code = struct.unpack('<h', data[:2])[0]
                    size = struct.unpack('<h', data[2:4])[0]
                    data = struct.unpack('<' + 'h' * int(size / 2), data[4:size + 4])

                    print("Code: {0} Size: {1} Data: {2}".format(code, size, data))

                    self.__evaluate_package(code, size, data)

                    time.sleep(self.mw.settings.TELEMETRY_TIME)

                self.mw.stop_udp_telemetry()

    def __evaluate_package(self, code, size, data):

        if code == self.mw.ATTITUDE:
            if size != 4:
                print("Error in altitude package, size should be 4 instead of: %f" % size)

            self.__print_altitude(data)

        if code == self.mw.ALTITUDE:
            if size != 6:
                print("Error in attitude package, size should be 6 instead of: %f" % size)

            self.__print_attitude(data)

        if code == self.mw.RAW_IMU:
            if size != 18:
                print("Error in raw_imu package, size should be 18 instead of: %f" % size)

            self.__print_raw_imu(data)

        if code == self.mw.RC:
            if size != 8:
                print("Error in rc package, size should be 8 instead of: %f" % size)

            self.__print_rc(data)

        if code == self.mw.MOTOR:
            if size != 8:
                print("Error in motor package, size should be 8 instead of: %f" % size)

            self.__print_motor(data)

        if code == self.mw.SERVO:
            if size != 8:
                print("Error in servo package, size should be 8 instead of: %f" % size)

            self.__print_servo(data)

        if code == self.mw.PID:
            if size != 18:
                print("Error in pid package, size should be 18 instead of: %f" % size)

            self.__print_pid_coef(data)

    def test_drone_motors(self, duration):

        self.mw.arm()

        time_start = time.time()

        roll = 1000
        pitch = 1000
        yaw = 1000
        throttle = 1000

        self.test_set_rc(roll, pitch, yaw, throttle)

        while time.time() - time_start < duration:

            if not (roll >= 2000 | pitch >= 2000 | yaw >= 2000 | throttle >= 2000):

                roll += 2
                pitch += 2
                yaw += 2
                throttle += 2

                time.sleep(self.mw.settings.timeMSP)

                self.test_set_rc(roll, pitch, yaw, throttle)

            self.test_set_rc(roll, pitch, yaw, throttle)

        self.mw.disarm()

    def __print_altitude(self, data):

        print("-----ALTITUDE-----\n")
        print("EstAlt: {} cm".format(data["estalt"]))
        print("Vario: {} cm/s".format(data["vario"]))
        print("elapsed: {}".format(data["elapsed"]))
        print("timestamp: {}".format(data["timestamp"]))
        print("-------------------\n")

    def __print_attitude(self, data):

        print("-----ATTITUDE-----\n")
        print("Angx: {} cm".format(data["angx"]))
        print("Angy: {} cm/s".format(data["angy"]))
        print("Heading: {}".format(data["heading"]))
        print("elapsed: {}".format(data["elapsed"]))
        print("timestamp: {}".format(data["timestamp"]))
        print("-------------------\n")

    def __print_raw_imu(self, data):

        print("-----RAW_IMU-----")
        print("accx: {} ,".format(data["accx"]))
        print("accy: {} ,".format(data["accy"]))
        print("accz: {} ,".format(data["accz"]))
        print("gyrx: {} ,".format(data["gyrx"]))
        print("gyry: {} ,".format(data["gyry"]))
        print("gyrz: {} ".format(data["gyrz"]))
        print("-------------------\n")

    def __print_pid_coef(self, data):

        print("-----PID_COEF-----")
        print("Rp: {} ,".format(data["rp"]))
        print("Ri: {} ,".format(data["ri"]))
        print("Rd: {} ,".format(data["rd"]))
        print("Pp: {} ,".format(data["pp"]))
        print("Pi: {} ,".format(data["pi"]))
        print("Pd: {} ,".format(data["pd"]))
        print("Yp: {} ,".format(data["yp"]))
        print("Yi: {} ,".format(data["yi"]))
        print("Yd: {} ,".format(data["yd"]))
        print("Elapsed: {} ,".format(data["elapsed"]))
        print("Timestamp: {} ,".format(data["timestamp"]))
        print("-------------------\n")

    def __print_motor(self, data):

        print("-----MOTORS-----")
        print("M1: {} ,".format(data["m1"]))
        print("M2: {} ,".format(data["m2"]))
        print("M3: {} ,".format(data["m3"]))
        print("M4: {} ,".format(data["m4"]))
        print("Elapsed: {} ,".format(data["elapsed"]))
        print("Timestamp: {} ,".format(data["timestamp"]))
        print("-------------------\n")

    def __print_servo(self, data):

        print("-----SERVOS-----")
        print("S1: {} ,".format(data["s1"]))
        print("S2: {} ,".format(data["s2"]))
        print("S3: {} ,".format(data["s3"]))
        print("S4: {} ,".format(data["s4"]))
        print("Elapsed: {} ,".format(data["elapsed"]))
        print("Timestamp: {} ,".format(data["timestamp"]))
        print("-------------------\n")

    def __print_rc(self, data):

        print("-----RC-----\n")
        print("Roll: {}".format(data["roll"]))
        print("Pitch: {}".format(data["pitch"]))
        print("Yaw: {}".format(data["yaw"]))
        print("Throttle: {}".format(data["throttle"]))
        print("-------------------\n")








