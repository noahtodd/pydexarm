import serial
import time

# Configure the serial port
arduino = serial.Serial('COM6', 115200, timeout=.2)  # Adjust the port name as needed
# On Windows, the port might be 'COM3' or similar
# On macOS, it might be '/dev/tty.usbmodem1101' or similar
SerialConnection = True

def write_read(x):
    arduino.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = arduino.readline()
    return data

while SerialConnection:
    num = input("Enter a number: ")  # Taking input from user
    if num == 'q':
        print("Exiting the program")
        arduino.close()
        SerialConnection = False
        break
    value = write_read(num)
    print(value)  # Printing the value