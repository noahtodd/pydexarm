import serial
import re
import time

class Dexarm:
    # creates feedrate variable
    default_feedrate = 2000
    # creates relative boolean to reduce the number of commands sent when switching between relative and absolute movement
    relative_positioning = False

    def __init__(self, port):
        self.ser = serial.Serial(port, 115200, timeout=None)
        self.is_open = self.ser.isOpen()
        if self.is_open:
            print('pydexarm: %s open' % self.ser.name)
        else:
            print('Failed to open serial port')

    # I need to add a send command method that can be parallelized
    '''def _send_cmd(self, data):
        self.ser.write(data.encode())
        while True:
            str = self.ser.readline().decode("utf-8")
            if len(str) > 0:
                if str.find("ok") > -1:
                    print("read ok")
                    break
                else:
                    print("read：", str)
    '''
    def _send_cmd(self, data):
        # stores the start time of the function
        # start = time.time()
        # checks to see if the dexarm is executing a command and waits until it is done
        # if self.ser.in_waiting > 0:
        while True:
            str = self.ser.readline().decode("utf-8")
            if len(str) > 0:
                if str.find("ok") > -1:
                    print("read ok")
                    break
                else:
                    print("read：", str)
            # breaks the loop if it has run for more than 5 seconds
            '''if time.time() - start > 5:
                print("timeout")
                break'''
        # sends the command
        self.ser.write(data.encode())
        
        '''str = self.ser.readline().decode("utf-8")
        if str.find("ok") == -1 and str != "":
            while True:
                str = self.ser.readline().decode("utf-8")
                if len(str) > 0:
                    if str.find("ok") > -1:
                        print("read ok")
                        break
                    else:
                        print("read：", str)
        self.ser.write(data.encode())
        '''

    def setup(self):
        # clears the buffer
        if self.is_open:
            self.ser.reset_input_buffer()
        else:
            print('Serial port not open')
        # sets positioning to absolute
        cmd = "G90\r\n"
        self.ser.write(cmd.encode())
        self.relative_positioning = False
    
    def factory_reset(self):
        self._send_cmd("M502\r")

    def go_home(self):
        self._send_cmd("M1112\r")

    def set_work_origin(self, X, Y, Z):
        print("Setting work origin")
        self._send_cmd("G92 X" + str(X) + " Y" + str(Y) + " Z" + str(Z) + "\r\n")

    def set_acceleration(self, acceleration, travel_acceleration, retract_acceleration=60):
        cmd = "M204"+"P" + str(acceleration) + "T"+str(travel_acceleration) + "T" + str(retract_acceleration) + "\r\n"
        self._send_cmd(cmd)

    def set_module_kind(self, kind):
        self._send_cmd("M888 P" + str(kind) + "\r")

    def get_module_kind(self):
        self.ser.write('M888\r'.encode())
        while True:
            str = self.ser.readline().decode("utf-8")
            if len(str) > 0:
                if str.find("PEN") > -1:
                    module_kind = 'PEN'
                if str.find("LASER") > -1:
                    module_kind = 'LASER'
                if str.find("PUMP") > -1:
                    module_kind = 'PUMP'
                if str.find("3D") > -1:
                    module_kind = '3D'
            if len(str) > 0:
                if str.find("ok") > -1:
                    return module_kind

    def move_to(self, x, y, z, feedrate=default_feedrate):
        if self.relative_positioning:
            cmd = "G90\r\n"
            self._send_cmd(cmd)
            self.relative_positioning = False
        cmd = "G1"+"F" + str(feedrate) + "X"+str(x) + "Y" + str(y) + "Z" + str(z) + "\r\n"
        self._send_cmd(cmd)

    def fast_move_to(self, x, y, z, feedrate=default_feedrate):
        if self.relative_positioning:
            cmd = "G90\r\n"
            self._send_cmd(cmd)
            self.relative_positioning = False
        cmd = "G0"+"F" + str(feedrate) + "X"+str(x) + "Y" + str(y) + "Z" + str(z) + "\r\n"
        self._send_cmd(cmd)

    def move_to_Z0(self,feedrate=default_feedrate):
        # if self.relative_positioning:
        cmd = "G90\r\n"
        self._send_cmd(cmd)
        self.relative_positioning = False
        cmd = "G1"+"F" + str(feedrate) + "Z0\r\n"
        self._send_cmd(cmd)

    def relative_move(self, x, y, z, feedrate=default_feedrate):
        # if not self.relative_positioning:
        cmd = "G91\r\n"
        self._send_cmd(cmd)
        self.relative_positioning = True
        cmd = "G1"+"F" + str(feedrate) + "X"+str(x) + "Y" + str(y) + "Z" + str(z) + "\r\n"
        self._send_cmd(cmd)

    def rotate_to(self, angle):
        cmd = "M2101 P" + str(angle) + "\r\n"
        self._send_cmd(cmd)

    def get_current_position(self):
        self.ser.write('M114\r'.encode())
        while True:
            str = self.ser.readline().decode("utf-8")
            print(str)
            if len(str) > 0:
                if str.find("X:") > -1:
                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", str)
                    x = float(temp[0])
                    y = float(temp[1])
                    z = float(temp[2])
                    e = float(temp[3])
            if len(str) > 0:
                if str.find("DEXARM Theta") > -1:
                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", str)
                    a = float(temp[0])
                    b = float(temp[1])
                    c = float(temp[2])
            # if all variables have been assigned, break the loop and return the values
            if 'x' in locals() and 'y' in locals() and 'z' in locals() and 'e' in locals() and 'a' in locals() and 'b' in locals() and 'c' in locals():
                return x,y,z,e,a,b,c       
            '''if len(str) > 0:
                if str.find("ok") > -1:
                    return x,y,z,e,a,b,c'''
            # else:
            #    return 0,0,0,0,0,0,0
        return 0,0,0,0,0,0,0
    
    # get current position based on the set work origin
    def get_current_position_workorigin(self):
        # start timeout timer
        start = time.time()
        self.ser.write('M114\r'.encode())
        while True:
            str = self.ser.readline().decode("utf-8")
            if len(str) > 0:
                if str.find("X:") > -1 and str.find("Real") == -1:
                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", str)
                    x = float(temp[0])
                    y = float(temp[1])
                    z = float(temp[2])
                    e = float(temp[3])
            # if all variables have been assigned, break the loop and return the values
            if 'x' in locals() and 'y' in locals() and 'z' in locals() and 'e' in locals():
                return x,y,z,e      
            # breaks the loop if it has run for more than 3 seconds
            if time.time() - start > 3:
                print("timeout")
                break
        return 0,0,0,0

    """Delay"""
    def dealy_ms(self, value):
        self._send_cmd("G4 P" + str(value) + '\r')

    def dealy_s(self, value):
        self._send_cmd("G4 S" + str(value) + '\r')

    """SoftGripper & AirPicker"""
    def soft_gripper_pick(self):
        self._send_cmd("M1001\r")

    def soft_gripper_place(self):
        self._send_cmd("M1000\r")

    def soft_gripper_nature(self):
        self._send_cmd("M1002\r")

    def soft_gripper_stop(self):
        self._send_cmd("M1003\r")

    def air_picker_pick(self):
        self._send_cmd("M1000\r")

    def air_picker_place(self):
        self._send_cmd("M1001\r")

    def air_picker_nature(self):
        self._send_cmd("M1002\r")

    def air_picker_stop(self):
        self._send_cmd("M1003\r")

    """Laser"""
    def laser_on(self, value=0):
        self._send_cmd("M3 S" + str(value) + '\r')

    def laser_off(self):
        self._send_cmd("M5\r")

    """Conveyor Belt"""
    def conveyor_belt_forward(self, speed=0):
        self._send_cmd("M2012 S" + str(speed) + 'D0\r')
    def conveyor_belt_backward(self, speed=0):
        self._send_cmd("M2012 S" + str(speed) + 'D1\r')
    def conveyor_belt_stop(self, speed=0):
        self._send_cmd("M2013\r")
