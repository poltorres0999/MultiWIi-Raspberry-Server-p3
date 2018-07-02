
import serial


class Settings(object):

    def __init__(self):

        # Decides which functions will be executed in the loop method of the Multiwii
        self.MSP_PID = False
        self.MSP_RAW_IMU = True
        self.MSP_SERVO = False
        self.MSP_MOTOR = False
        self.MSP_RC = False
        self.MSP_ATTITUDE = False
        self.MSP_ALTITUDE = True
        self.TELEMETRY_TIME = 1

        # Arm/Disarm configuration

        self.throttle_yaw = True
        self.throttle_roll = False
        self.max_yaw = 2000
        self.min_throttle = 990
        self.max_roll = 1900
        self.min_yaw = 900
        self.min_roll = 900

        # Raspberry Pi UDP Server attributes
        self.ip_address = "127.0.0.1"
        self.control_port = 4445
        self.address = (self.ip_address, self.control_port)

        # Serial port configuration
        self.serial_port = serial.Serial()
        self.serial_port.port = "COM4"
        self.serial_port.baudrate = 115200
        self.serial_port.bytesize = serial.EIGHTBITS
        self.serial_port.parity = serial.PARITY_NONE
        self.serial_port.stopbits = serial.STOPBITS_ONE
        self.serial_port.timeout = 0
        self.serial_port.xonxoff = False
        self.serial_port.rtscts = False
        self.serial_port.dsrdtr = False
        self.serial_port.write_timeout = 2
        self.wakeup = 10
        self.timeMSP = 0.02





