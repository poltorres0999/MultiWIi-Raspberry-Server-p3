import socket
import time
import serial
import struct

from src.Multiwii import MultiwiiSettings, Drone


class MultiWii(object):
    # Multiwii Serial Protocol message IDs.
    # Getters
    IDENT = 100
    STATUS = 101
    RAW_IMU = 102
    SERVO = 103
    MOTOR = 104
    RC = 105
    RAW_GPS = 106
    COMP_GPS = 107
    ATTITUDE = 108
    ALTITUDE = 109
    ANALOG = 110
    RC_TUNING = 111
    PID = 112
    BOX = 113
    MISC = 114
    MOTOR_PINS = 115
    BOXNAMES = 116
    PIDNAMES = 117
    WP = 118
    BOXIDS = 119
    RC_RAW_IMU = 121

    # Setters
    SET_RAW_RC = 200
    SET_RAW_GPS = 201
    SET_PID = 202
    SET_BOX = 203
    SET_RC_TUNING = 204
    ACC_CALIBRATION = 205
    MAG_CALIBRATION = 206
    SET_MISC = 207
    RESET_CONF = 208
    SET_WP = 209
    SWITCH_RC_SERIAL = 210
    IS_SERIAL = 211
    DEBUG = 254

    def __init__(self): # Add conf file to the constructor

        self.drone = Drone.Drone()
        self.udp_server_started = False
        self.sock = ""
        self.udp_telemetry = False
        self.telemetry = False

        try:
            self.settings = MultiwiiSettings.Settings()
            self.serial = self.settings.serial_port
            self.serial.open()
            time.sleep(self.settings.wakeup)
        except ValueError as err:
            print('Serial port exception:' + str(err) + '\n')

    def send_cmd(self, data_length, code, data):

        checksum = 0
        total_data = ['$', 'M', '<', data_length, code] + data
        for i in struct.pack('<2B%dH' % len(data), *total_data[3:len(total_data)]):
            checksum = checksum ^ ord(chr(i))
        total_data.append(checksum)

        try:

            header = struct.pack('<c', total_data[0].encode('ascii'))
            preamble = struct.pack('<c', total_data[1].encode('ascii'))
            direction = struct.pack('<c', total_data[2].encode('ascii'))
            data = struct.pack('2B%dHB' % len(data), *total_data[3:len(total_data)])

            package = header + preamble + direction + data

            b = None
            b = self.serial.write(package)

        except ValueError as err:
            print('Serial port exception:' + str(err) + '\n')

    def get_data(self, cmd):

        try:
            start = time.time()
            self.send_cmd(0, cmd, [])

            header = self.serial.read()
            while header != b'$':
                header = self.serial.read()

            preamble = self.serial.read()
            direction = self.serial.read()
            size = struct.unpack('<b', self.serial.read())[0]
            cmd = self.serial.read()
            data = self.serial.read(size)
            total_data = struct.unpack('<' + 'h' * int((size / 2)), data)

            self.serial.flushInput()
            self.serial.flushOutput()

            elapsed = time.time() - start

            return total_data, elapsed

        except serial.SerialException as err:
            print('Serial port exception:' + str(err) + '\n')

    def arm(self):

        if not self.drone.armed:

            if self.settings.throttle_yaw:
                start = time.time()
                while (time.time() - start) < 2.5:
                    self.set_rc([1500, 1500, self.settings.max_yaw, self.settings.min_throttle])

            if self.settings.throttle_roll:
                start = time.time()
                while (time.time() - start) < 2.5:
                    self.set_rc([self.settings.max_roll, 1500, 1500, self.settings.min_throttle])

            self.drone.armed = True

    def disarm(self):

        if self.drone.armed:

            if self.settings.throttle_yaw:
                start = time.time()
                while (time.time() - start) < 2.5:
                    self.set_rc([1500, 1500, self.settings.min_yaw, self.settings.min_throttle])

            if self.settings.throttle_roll:
                start = time.time()
                while (time.time() - start) < 2.5:
                    self.set_rc([self.settings.min_roll, 1500, 1500, self.settings.min_throttle])

        self.drone.armed = False

    def get_altitude(self):

        total_data, elapsed = self.get_data(MultiWii.ALTITUDE)

        self.drone.altitude['estalt'] = total_data[0]
        self.drone.altitude['vario'] = total_data[1]
        self.drone.altitude['elapsed'] = round(elapsed, 3)
        self.drone.altitude['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.altitude

    def get_attitude(self):

        total_data, elapsed = self.get_data(MultiWii.ATTITUDE)

        self.drone.attitude['angx'] = float(total_data[0] / 10.0)
        self.drone.attitude['angy'] = float(total_data[1] / 10.0)
        self.drone.attitude['heading'] = float(total_data[2])
        self.drone.attitude['elapsed'] = round(elapsed, 3)
        self.drone.attitude['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.attitude

    # ROLL/PITCH/YAW/THROTTLE
    def get_rc(self):

        total_data, elapsed = self.get_data(MultiWii.RC)

        self.drone.rc_channels['roll'] = total_data[0]
        self.drone.rc_channels['pitch'] = total_data[1]
        self.drone.rc_channels['yaw'] = total_data[2]
        self.drone.rc_channels['throttle'] = total_data[3]
        self.drone.rc_channels['elapsed'] = round(elapsed, 3)
        self.drone.rc_channels['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.rc_channels

    def get_raw_imu(self):

        total_data, elapsed = self.get_data(MultiWii.RAW_IMU)

        self.drone.raw_imu['accx'] = total_data[0]
        self.drone.raw_imu['accy'] = total_data[1]
        self.drone.raw_imu['accz'] = total_data[2]
        self.drone.raw_imu['gyrx'] = total_data[3]
        self.drone.raw_imu['gyry'] = total_data[4]
        self.drone.raw_imu['gyrz'] = total_data[5]
        self.drone.raw_imu['magx'] = total_data[6]
        self.drone.raw_imu['magy'] = total_data[7]
        self.drone.raw_imu['magz'] = total_data[8]
        self.drone.raw_imu['elapsed'] = round(elapsed, 3)
        self.drone.raw_imu['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.raw_imu

    def get_motor(self):

        total_data, elapsed = self.get_data(MultiWii.MOTOR)

        self.drone.motor['m1'] = total_data[0]
        self.drone.motor['m2'] = total_data[1]
        self.drone.motor['m3'] = total_data[2]
        self.drone.motor['m4'] = total_data[3]
        self.drone.motor['elapsed'] = "%0.3f" % (elapsed,)
        self.drone.motor['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.motor

    def get_servo(self):

        total_data, elapsed = self.get_data(MultiWii.SERVO)

        self.drone.servo['s1'] = total_data[0]
        self.drone.servo['s2'] = total_data[1]
        self.drone.servo['s3'] = total_data[2]
        self.drone.servo['s4'] = total_data[3]
        self.drone.servo['elapsed'] = "%0.3f" % (elapsed,)
        self.drone.servo['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.servo

    def get_pid_coef(self):

        total_data, elapsed = self.get_data(MultiWii.PID)

        self.drone.PID_coef['rp'] = total_data[0]
        self.drone.PID_coef['ri'] = total_data[0]
        self.drone.PID_coef['rd'] = total_data[0]
        self.drone.PID_coef['pp'] = total_data[0]
        self.drone.PID_coef['pi'] = total_data[0]
        self.drone.PID_coef['pd'] = total_data[0]
        self.drone.PID_coef['yp'] = total_data[0]
        self.drone.PID_coef['yi'] = total_data[0]
        self.drone.PID_coef['yd'] = total_data[0]
        self.drone.PID_coef['elapsed'] = "%0.3f" % (elapsed,)
        self.drone.PID_coef['timestamp'] = "%0.2f" % (time.time(),)

        return self.drone.PID_coef

    def set_rc(self, rc_data):

        self.send_cmd(8, MultiWii.SET_RAW_RC, rc_data)

    def telemetry_loop(self):

        self.telemetry = True

        timer = time.time()

        while self.telemetry:

            if time.time() - timer >= self.settings.TELEMETRY_TIME:

                if self.settings.MSP_ALTITUDE:
                    self.get_altitude()

                if self.settings.MSP_ATTITUDE:
                    self.get_attitude()

                if self.settings.MSP_RAW_IMU:
                    self.get_raw_imu()

                if self.settings.MSP_RC:
                    self.get_rc()

                if self.settings.MSP_MOTOR:
                    self.get_motor()

                if self.settings.MSP_SERVO:
                    self.get_servo()

                timer = time.time()

    # UDP communication methods

    def udp_get_altitude(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        altitude = self.get_altitude()
        data = [altitude['estalt'], altitude['vario']]

        self.sock.sendto(self.__create_package(self.ALTITUDE, 4, data),
                         (self.settings.ip_address, 4446))

    def udp_get_attitude(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        attitude = self.get_attitude()
        data = [attitude['angx'], attitude['angy'], attitude['heading']]

        self.sock.sendto(self.__create_package(self.ATTITUDE, 6, data),
                         (self.settings.ip_address, 4446))

    def udp_get_raw_imu(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        raw_imu = self.get_raw_imu()
        data = [raw_imu["accx"], raw_imu["accy"], raw_imu["accz"], raw_imu["gyrx"], raw_imu["gyry"],
                raw_imu["gyrz"], raw_imu["magx"], raw_imu["magy"], raw_imu["magz"]]

        self.sock.sendto(self.__create_package(self.RAW_IMU, 18, data),
                         (self.settings.ip_address, 4446))

    def udp_get_rc(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        rc = self.get_rc()
        data = [rc["roll"], rc["pitch"], rc["yaw"], rc["throttle"]]
        self.sock.sendto(self.__create_package(self.RC, 8, data),
                         (self.settings.ip_address, 4446))

    def udp_get_motor(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        motor = self.get_motor()
        data = [motor['m1'], motor['m2'], motor['m3'], motor['m4']]
        self.sock.sendto(self.__create_package(self.MOTOR, 8, data),
                         (self.settings.ip_address, 4446))

    def udp_get_servo(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        servo = self.get_servo()
        data = [servo['s1'], servo['s2'], servo['s3'], servo['s4']]
        self.sock.sendto(self.__create_package(self.SERVO, 8, data),
                         (self.settings.ip_address, 4446))

    def udp_get_pid_coef(self):

        if not self.udp_server_started:
            self.__start_udp_server()

        pid = self.get_pid_coef()
        data = [pid["rp"], pid["ri"], pid["rd"], pid["pp"], pid["pi"],
                pid["pd"], pid["yp"], pid["yi"], pid["yd"]]

        self.sock.sendto(self.__create_package(self.PID, 18, data),
                         (self.settings.ip_address, 4446))

    def udp_telemetry_loop(self):

        self.__start_udp_server()

        if self.udp_server_started:

            self.udp_telemetry = True

            timer = time.time()

            while self.udp_telemetry:

                if time.time() - timer >= self.settings.TELEMETRY_TIME:

                    if self.settings.MSP_ALTITUDE:
                        self.udp_get_altitude()

                    if self.settings.MSP_ATTITUDE:
                        self.udp_get_altitude()

                    if self.settings.MSP_RAW_IMU:
                        self.udp_get_raw_imu()

                    if self.settings.MSP_RC:
                        self.udp_get_rc()

                    if self.settings.MSP_MOTOR:
                        self.udp_get_motor()

                    if self.settings.MSP_SERVO:
                        self.get_servo()

                    timer = time.time()
        else:
            return self.udp_server_started

    def __start_udp_server(self):

        if not self.udp_server_started:

            try:
                address = self.settings.address
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                print("Socket creation: Socket created!")
                self.sock.bind(address)
                print("Socket binding: Socket bound!")
                self.udp_server_started = True

            except socket.error as err:
                print("Error starting server: {}".format(err))
        else:
            print("Server already started!")

    def stop_telemetry(self):
        self.telemetry = False

    def close_udp_server(self):

        if self.sock != "":
            self.udp_server_started = False
            self.sock.close()

    def stop_udp_telemetry(self):

        self.close_udp_server()
        self.udp_telemetry = False

    @staticmethod
    def __create_package(code, size, data):

        code = struct.pack('<h', code)
        size = struct.pack('<h', size)
        data = struct.pack('<'+'h' * len(data), *data)
        package = code + size + data

        return package
