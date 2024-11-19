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
    # Read data until newline character is received
    data = ''
    while data == '' or data[-1] != '\n':
        data += arduino.readline().decode("utf-8")
    return data

while SerialConnection:
    num = input("Enter a number: ")  # Taking input from user
    if num == 'q':
        print("Exiting the program")
        arduino.close()
        SerialConnection = False
        break
    # if number doesn't start with a letter and end with a number, then skip the loop
    if not num[0].isalpha() or not num[-1].isdigit():
        print("Invalid input. Please enter a valid input.")
        continue
    value = write_read(num)
    print(value)  # Printing the value