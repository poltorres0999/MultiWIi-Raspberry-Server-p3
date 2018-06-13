class Drone:

    def __init__(self):
        self.armed = False
        self.attitude = {'angx': 0, 'angy': 0, 'heading': 0, 'elapsed': 0, 'timestamp': 0}
        self.altitude = {'estalt': 0, 'vario': 0, 'elapsed': 0, 'timestamp': 0}
        self.PID_coef = {'rp': 0, 'ri': 0, 'rd': 0, 'pp': 0, 'pi': 0, 'pd': 0, 'yp': 0, 'yi': 0, 'yd': 0,
                         'elapsed': 0, 'timestamp': 0}
        self.raw_imu = {'accx': 0, 'accy': 0, 'accz': 0, 'gyrx': 0, 'gyry': 0, 'gyrz': 0, 'magx': 0, 'magy': 0,
                        'magz': 0, 'elapsed': 0, 'timestamp': 0}
        self.motor = {'m1': 0, 'm2': 0, 'm3': 0, 'm4': 0, 'elapsed': 0, 'timestamp': 0}
        self.servo = {'s1': 0, 's2': 0, 's3': 0, 's4': 0, 'elapsed': 0, 'timestamp': 0}
        self.rc_channels = {'roll': 0, 'pitch': 0, 'yaw': 0, 'throttle': 0, 'elapsed': 0, 'timestamp': 0}

