from pydexarm import Dexarm
import tkinter as tk
import math
import serial
import time
import keyboard

'''windows'''
# try to open the dexarm on the port
dexarm_connected = False
dexarm2_connected = False
print("connecting with Dexarms...")
try:
    dexarm = Dexarm("COM4")
    print("connected with Dexarm 1")
    dexarm_connected = True
except:
    print("Dexarm 1 not connected")
try:
    dexarm2 = Dexarm("COM3")
    print("connected with Dexarm 2")
    dexarm2_connected = True
except:
    print("Dexarm 2 not connected")
print("connecting with Arduino...")
arduino = serial.Serial('COM6', 115200, timeout=.2)  # Adjust the port name as needed
print("connected with Arduino")

'''mac & linux'''
#dexarm = Dexarm("/dev/tty.usbmodem315D378032331") # /dev/tty.usbmodem3086337A34381") # original address "/dev/cu.usbmodem315D378032331"

# Define an increment distance
increment_distance = 10
# Define the feedrate for buttons
feedrate = 2000
# define constant servo positions
release = 65
natural = 90
intake = 125
dispense = 135
current_distance_slider_value = 25 # Define a variable to store the current value of distance_slider

# Create a text file to store gcode commands
gcode_file = open("gcode_commands.txt", "a")

def move_up():
    print("Up button pressed")
    dexarm.relative_move(0, 0, increment_distance, feedrate=feedrate)

def move_down():
    print("Down button pressed")
    dexarm.relative_move(0, 0, -increment_distance, feedrate=feedrate)

def move_Z0():
    print("Z0 button pressed")
    dexarm.move_to_Z0(feedrate=feedrate)

def move_right():
    print("Right button pressed")
    dexarm.relative_move(increment_distance, 0, 0, feedrate=feedrate)

def move_left():
    print("Left button pressed")
    dexarm.relative_move(-increment_distance, 0, 0, feedrate=feedrate)

def move_forward(): # forward
    print("Forward button pressed")
    dexarm.relative_move(0, increment_distance, 0, feedrate=feedrate)

def move_backward(): # backward
    print("Backward button pressed")
    dexarm.relative_move(0, -increment_distance, 0, feedrate=feedrate)

def position1():
    print("Position 1 button pressed")
    dexarm.move_to(50, 320, 20, feedrate=feedrate)

def distance_slider(value):
    global increment_distance 
    increment_distance = distance_slider.get() + distance_decimal_slider.get()
    print("New increment distance: ", increment_distance)

def speed_slider(value):
    global feedrate
    feedrate = int(value)
    print("New speed: ", value)

def update_position_label():
    x, y, z, e, a, b, c = dexarm.get_current_position()
    x2, y2, z2, e2, a2, b2, c2 = dexarm2.get_current_position()
    position_finder_label.config(text="X" + str(x) + " Y" + str(y) + " Z" + str(z) + " E" + str(e) + " A" + str(a) + " B" + str(b) + " C" + str(c) + "  Dexarm 2: X" + str(x2) + " Y" + str(y2) + " Z" + str(z2) + " E" + str(e2) + " A" + str(a2) + " B" + str(b2) + " C" + str(c2))

def rotate_to_0():
    x, y, z, e, a, b, c = dexarm.get_current_position()
    if y == 0:
        target = 0
    elif y != 0:
        target = int(math.degrees(math.atan(x/y)))
    target = (target + 360) % 360
    dexarm.rotate_to(target)
    rotate_to_angle_slider.set(target)
    print("Rotate to 0 button pressed. Moving to: ", target, " degrees --- coordinates: ", "X: ", x, " Y: ", y, " Z: ", z, " E: ", e)

def rotation_slider(value):
    dexarm.rotate_to(int(value))
    print("Rotation slider value: ", value)

def cut_line():
    print("Cut line button pressed")
    z_working = -73
    cmd = "G1"+"F" + str(4000) + "X-40 Y290 Z" + str(z_working+10) + "\r\n" + "G1"+"F" + str(4000) + "X-40 Y290 Z" + str(z_working) + "\r\n" + "G1"+"F" + str(4000) + "X30 Y330 Z" + str(z_working) + "\r\n" + "G1"+"F" + str(4000) + "X30 Y330 Z" + str(z_working+10) + "\r\n" + "G1"+"F" + str(4000) + "X40 Y340 Z" + str(z_working+10) + "\r\n" + "G1"+"F" + str(4000) + "X40 Y340 Z" + str(z_working) + "\r\n" + "G1"+"F" + str(4000) + "X-30 Y300 Z" + str(z_working) + "\r\n" + "G1"+"F" + str(4000) + "X-30 Y300 Z" + str(z_working+10) + "\r\n" # + "G1"+"F" + str(4000) + "X0 Y300 Z0 \r\n"
    dexarm._send_cmd(cmd)

def record_position():
    x, y, z, _, _, _, _ = dexarm.get_current_position()
    print("Recording position: X",x, " Y",y, " Z",z)
    gcode_command = f"G1 X{x} Y{y} Z{z}\n"
    gcode_file.write(gcode_command)

def add_grip():
    dexarm.air_picker_pick()
    gcode_command = f"M1000 ; Air Pick Grab\nG4 S1\n"
    gcode_file.write(gcode_command)

def add_release():
    dexarm.air_picker_place()
    gcode_command = f"M1001 ; Air Pick Eject\nG4 S1\n"
    gcode_file.write(gcode_command)

def add_natural():
    dexarm.air_picker_nature()
    gcode_command = f"M1002 ; Air Pick Natural\nG4 S1\n"
    gcode_file.write(gcode_command)

# Function that runs the gcode commands
def run_gcode():
    gcode_file = open("gcode_commands_1.txt", "r")
    for line in gcode_file:
        print(line)
        dexarm2._send_cmd(line)
    print("\nFinished running gcode")

'''
def run_gcode():
    lineNumber = line_number_entry.get()
    # if linenumber is not a number, set it to 0. Otherwise, convert it to an integer
    if not lineNumber.isdigit():
        lineNumber = 0
    else:
        lineNumber = int(lineNumber)
    gcode_file = open("gcode_commands_1.txt", "r")
    print("\nStarting sequence at line ", lineNumber)
    # remove all lines before the line number
    if lineNumber != 0:
        for current_line_number, line in enumerate(gcode_file, start=1):
            if current_line_number < lineNumber:
                continue  # Skip lines until the desired line number is reached
    for line in gcode_file:
        print(line)
        line = line.lstrip()
        if line.strip() == "":  # Skip empty lines
            continue
        elif line[0] == ";" or line[0] == "\n":
            print("Comment: ", line[1:])
            continue
        elif line[0] in ["A", "B", "C", "D", "E", "F", "H"]:
            if ";" in line:
                line = line[0:line.index(";")]
            print("Sending command to arduino: ", line)
            arduino.write(bytes(line, 'utf-8'))
            time.sleep(0.05)
        elif line[0] in ["R"]: # if the line has X, M, G as the first letter, send the remaining letters to dexarm
            dexarm._send_cmd(line[1:].strip)
        elif line[0] in ["P", "G", "M"]: # this is for any unchanged commands. I can't add it to the conditional above because these lines to need to be cut at the beginning
            dexarm._send_cmd(line)
        elif line[0] in ["Q"]: # if the line has Q as the first letter, send the remaining letters to dexarm2
            line = line[1:].strip()
            dexarm2._send_cmd(line)
        else: # print the line and say it didn't send to anything
            print("Line did not send to anything: ", line)
        # if q has been pressed on the keyboard, stop the loop
        if keyboard.is_pressed('q') or keyboard.is_pressed('x') or keyboard.is_pressed('Q') or keyboard.is_pressed('X'):
            print("Stopping loop as 'q' was pressed.")
            break
    print("\nFinished running gcode")

'''

def move_up2():
    print("Up button pressed")
    dexarm2.relative_move(0, 0, increment_distance, feedrate=feedrate)

def move_down2():
    print("Down button pressed")
    dexarm2.relative_move(0, 0, -increment_distance, feedrate=feedrate)

def move_Z02():
    print("Z0 button pressed")
    dexarm2.move_to_Z0(feedrate=feedrate)

def move_right2():
    print("Right button pressed")
    dexarm2.relative_move(increment_distance, 0, 0, feedrate=feedrate)

def move_left2():
    print("Left button pressed")
    dexarm2.relative_move(-increment_distance, 0, 0, feedrate=feedrate)

def move_forward2(): # forward
    print("Forward button pressed")
    dexarm2.relative_move(0, increment_distance, 0, feedrate=feedrate)

def move_backward2(): # backward
    print("Backward button pressed")
    dexarm2.relative_move(0, -increment_distance, 0, feedrate=feedrate)

def position12():
    print("Position 1 button pressed")
    dexarm2.move_to(50, 320, 20, feedrate=feedrate)

def rotate_to_02():
    x, y, z, e, a, b, c = dexarm2.get_current_position()
    if y == 0:
        target = 0
    elif y != 0:
        target = int(math.degrees(math.atan(x/y)))
    target = (target + 360) % 360
    dexarm2.rotate_to(target)
    rotate_to_angle_slider.set(target)
    print("Rotate to 0 button pressed. Moving to: ", target, " degrees --- coordinates: ", "X: ", x, " Y: ", y, " Z: ", z, " E: ", e)

def record_position2():
    x, y, z, _, _, _, _ = dexarm2.get_current_position()
    print("Recording position: X",x, " Y",y, " Z",z)
    gcode_command = f"Q G1 X{x} Y{y} Z{z}\n"
    gcode_file.write(gcode_command)

def add_grip2():
    dexarm2.air_picker_pick()
    gcode_command = f"Q M1000\nQ G4 S1\n"
    gcode_file.write(gcode_command)

def add_release2():
    dexarm2.air_picker_place()
    gcode_command = f"Q M1001\nQ G4 S1\n"
    gcode_file.write(gcode_command)

def add_natural2():
    dexarm2.air_picker_nature()
    gcode_command = f"Q M1002\n"
    gcode_file.write(gcode_command)

def add_comment():
    gcode_command = f"; {comment_entry.get()}\n"
    gcode_file.write(gcode_command)

# function that takes in a letter value for a servo and a value and sends it to the arduino
def rotateServoA(servoLetter, value): 
    print("Sending command to arduino: ", servoLetter, value)
    arduino.write(bytes(servoLetter + " " + str(value), 'utf-8'))
    time.sleep(0.05)

def rotateServoB(): # takes the value from the slider and sends it to the arduino
    value = servo_b_slider.get()
    print("Sending command to arduino: ", value)
    arduino.write(bytes("B "+str(value), 'utf-8'))
    time.sleep(0.05)

def rotateServoC(): # takes the value from the slider and sends it to the arduino
    value = servo_c_slider.get()
    print("Sending command to arduino: ", value)
    arduino.write(bytes("C "+str(value), 'utf-8'))
    time.sleep(0.05)

def recordServoB():
    value = servo_b_slider.get()
    print("Recording servo B position: ", value)
    gcode_command = f"B {value}\n"
    gcode_file.write(gcode_command)

def recordServoC():
    value = servo_c_slider.get()
    print("Recording servo C position: ", value)
    gcode_command = f"C {value}\n"
    gcode_file.write(gcode_command)

# Functions for Pipette control
# Function that releases
def release_plunger():
    print("Plunger release recorded")
    position = 275
    arduino.write(bytes("A "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("A "+ str(position) + " ; release plunger\n")
# Function that presses the plunger before getting liquid
def press_plunger():
    print("Plunger press recorded")
    position = 120
    arduino.write(bytes("A "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("A "+ str(position) + " ; press plunger\n")
# Function that ejects liquid in the plunger
def eject_liquid():
    print("Liquid eject recorded")
    position = 105
    arduino.write(bytes("A "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("A "+ str(position) + " ; eject liquid\n")
# Function that ejects pipette tips
def eject_tip():
    print("Tip eject recorded")
    position = 205
    arduino.write(bytes("D "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("D "+ str(position) + " ; eject tip\n")
# Function that sets the pipette ejector to natural
def natural_tip():
    print("Tip ejector reset recorded")
    position = 240
    arduino.write(bytes("D "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("D "+ str(position) + " ; reset tip ejector\n")
# Opens pipette disposal bin
def open_bin():
    print("Pipette disposal bin opening recorded")
    position = 141
    arduino.write(bytes("E "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("E "+ str(position) + " ; open pipette disposal bin\n")
# Closes pipette disposal bin
def close_bin():
    print("Pipette disposal bin closing recorded")
    position = 300
    arduino.write(bytes("E "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("E "+ str(position) + " ; close pipette disposal bin\n")
# Opens the bottle cap
def open_bottle():
    print("Bottle cover opening recorded")
    position = 245
    arduino.write(bytes("F "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("F "+ str(position) + " ; open bottle cover\n")
# Closes the bottle cap
def close_bottle():
    print("Bottle cover closing recorded")
    position = 430
    arduino.write(bytes("F "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("F "+ str(position) + " ; close bottle cover\n")
# Moves heating element to home position
def move_heating_home():
    print("Heating element home position recorded")
    position = 100
    arduino.write(bytes("H "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("H "+ str(position) + " ; move heating element to rest position\n")
# Moves heating element to working position 1
def move_heating_1():
    print("Heating element working position 1 recorded")
    position = 200
    arduino.write(bytes("H "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("H "+ str(position) + " ; move heating element to position 1\n")
# Moves heating element to working position 2
def move_heating_2():
    print("Heating element working position 2 recorded")
    position = 300
    arduino.write(bytes("H "+str(position), 'utf-8'))
    time.sleep(0.05)
    gcode_file.write("H "+ str(position) + " ; move heating element to position 2\n")

# Function to handle the Shift_L key press
def handle_shift_l(event):
    global current_distance_slider_value
    current_distance_slider_value = distance_slider.get()  # Store the current value
    distance_slider.set(12.7)  # Set the new value




# Create the main window
root = tk.Tk()
root.title("DexArm Control Panel")
root.minsize(600, 400)  # Set minimum size of the window to 500x400 pixels

# Configure minimum column widths for the columns spanned by the distance_slider
root.columnconfigure(0, minsize=100)
root.columnconfigure(1, minsize=80)
root.columnconfigure(2, minsize=80)
root.columnconfigure(3, minsize=80)
root.columnconfigure(4, minsize=100)
root.columnconfigure(5, minsize=80)
root.columnconfigure(6, minsize=80)
root.columnconfigure(7, minsize=80)
root.columnconfigure(8, minsize=80)

# Create buttons for dexarm 1
if dexarm_connected:
    up_button = tk.Button(root, text="Up", command=move_up)
    Z0_button = tk.Button(root, text="Z0", command=move_Z0)
    down_button = tk.Button(root, text="Down", command=move_down)
    right_button = tk.Button(root, text="Right", command=move_right)
    left_button = tk.Button(root, text="Left", command=move_left)
    forward_button = tk.Button(root, text="Forward", command=move_forward)
    backward_button = tk.Button(root, text="Backward", command=move_backward)
    home_button = tk.Button(root, text="Home", command=dexarm.go_home)
    position1_button = tk.Button(root, text="Position 1", command=position1)
    # Create picker buttons
    air_picker_label = tk.Label(root, text="Air Picker")
    air_picker_pick_button = tk.Button(root, text="Pick", command=dexarm.air_picker_pick)
    air_picker_place_button = tk.Button(root, text="Place", command=dexarm.air_picker_place)
    air_picker_nature_button = tk.Button(root, text="Nature", command=dexarm.air_picker_nature)
    air_picker_stop_button = tk.Button(root, text="Stop", command=dexarm.air_picker_stop)
    # Create a button that request the dexarm coordinates
    position_finder_title = tk.Label(root, text="Get Position")
    position_finder_button = tk.Button(root, text="Get Position", command=update_position_label)
    position_finder_label = tk.Label(root, text="Coordinates yet to be displayed")
    # Create a slider that rotates the arm to a specific angle
    rotate_to_angle_slider_label = tk.Label(root, text="Rotate to angle, deg")
    rotate_to_angle_slider = tk.Scale(root, from_= 0, to=360, orient=tk.HORIZONTAL, command=rotation_slider , length=300)
    # Create a button that rotates the arm to 0 degrees
    rotate_to_0_button = tk.Button(root, text="Rotate to 0", command=rotate_to_0)
# Create sliders
distance_slider_label = tk.Label(root, text="Increment Size, mm")
distance_slider = tk.Scale(root, from_=0, to=40, orient=tk.HORIZONTAL, command=distance_slider, length=300)
distance_slider.set(current_distance_slider_value)
# Create a slider for decimal values of the distance
distance_decimal_slider = tk.Scale(root, from_=0, to=.9, orient=tk.HORIZONTAL, command=distance_slider, length=100, resolution=0.1)
distance_decimal_slider.set(.4)
speed_slider_label = tk.Label(root, text="Speed, mm/min")
speed_slider = tk.Scale(root, from_=500, to=5000, orient=tk.HORIZONTAL, command=speed_slider, length=300)
speed_slider.set(4000)
# Create a slider that reads an input between 0-500 and a button that sends that value to Servo B
servo_b_slider_label = tk.Label(root, text="Servo B - Rotation")
servo_b_slider = tk.Scale(root, from_=100, to=500, orient=tk.HORIZONTAL, length=300)
servo_b_button = tk.Button(root, text="Rotate Servo B", command=rotateServoB)
record_servo_b_button = tk.Button(root, text="Record Servo B", command=recordServoB)
servo_c_slider_label = tk.Label(root, text="Servo C - Clamp")
servo_c_slider = tk.Scale(root, from_=100, to=500, orient=tk.HORIZONTAL, length=300)
servo_c_button = tk.Button(root, text="Rotate Servo C", command=rotateServoC)
record_servo_c_button = tk.Button(root, text="Record Servo C", command=recordServoC)
# Buttons for recording gcode commands
record_position_button = tk.Button(root, text="Record Position", command=record_position)
record_pick_button = tk.Button(root, text="Record Pick", command=add_grip)
record_place_button = tk.Button(root, text="Record Place", command=add_release)
record_nat_button = tk.Button(root, text="Record Nature", command=dexarm.air_picker_nature)
# Text box for adding a starting line for gcode. The line number is set to 0 by default
line_number_label = tk.Label(root, text="Starting line number")
line_number_entry = tk.Entry(root)
line_number_entry.insert(0, "0")
# Button for running gcode commands
run_gcode_button = tk.Button(root, text="Run Gcode", command=run_gcode)
# Dexarm 2Q
if dexarm2_connected:
    up_button2 = tk.Button(root, text="Up2", command=move_up2)
    Z0_button2 = tk.Button(root, text="Z02", command=move_Z02)
    down_button2 = tk.Button(root, text="Down2", command=move_down2)
    right_button2 = tk.Button(root, text="Right2", command=move_right2)
    left_button2 = tk.Button(root, text="Left2", command=move_left2)
    forward_button2 = tk.Button(root, text="Forward2", command=move_forward2)
    backward_button2 = tk.Button(root, text="Backward2", command=move_backward2)
    home_button2 = tk.Button(root, text="Home2", command=dexarm2.go_home)
    position1_button2 = tk.Button(root, text="Position 12", command=position12)
    rotate_to_0_button2 = tk.Button(root, text="Rotate to 02", command=rotate_to_02)
    record_position_button2 = tk.Button(root, text="Record Position2", command=record_position2)
    record_pick_button2 = tk.Button(root, text="Record Pick2", command=add_grip2)
    record_place_button2 = tk.Button(root, text="Record Place2", command=add_release2)
    record_nat_button2 = tk.Button(root, text="Record Nature2", command=add_natural2)
comment_button = tk.Button(root, text="Add Comment", command=add_comment)
comment_entry = tk.Entry(root, width=50)
# Buttons for controlling the pipette
pipette_label = tk.Label(root, text="Pipette Control")
release_button = tk.Button(root, text="Release", command=release_plunger)
natural_button = tk.Button(root, text="Eject Liquid", command=eject_liquid)
intake_button = tk.Button(root, text="Intake Mode", command=press_plunger)
pipette_ejector_label = tk.Label(root, text="Tip Ejector")
dispense_button = tk.Button(root, text="Eject Tip", command=eject_tip)
tip_natural_button = tk.Button(root, text="Reset Tip Ejector", command=natural_tip)
# Buttons for cover controls
liquid_cover_label = tk.Label(root, text="Bottle Cover")
liquid_cover_open_button = tk.Button(root, text="Open Liquid Cover", command=open_bottle)
liquid_cover_close_button = tk.Button(root, text="Close Liquid Cover", command=close_bottle)
tip_cover_label = tk.Label(root, text="Tip Disposal Cover")
tip_cover_open_button = tk.Button(root, text="Open Tip Cover", command=open_bin)
tip_cover_close_button = tk.Button(root, text="Close Tip Cover", command=close_bin)




# Place the button on the window
if dexarm_connected:
    up_button.grid(row=0, column=3)
    home_button.grid(row=1, column=1)
    Z0_button.grid(row=1, column=3)
    down_button.grid(row=2, column=3)
    right_button.grid(row=1, column=2)
    left_button.grid(row=1, column=0)
    forward_button.grid(row=0, column=1)
    backward_button.grid(row=2, column=1)
    position1_button.grid(row=2, column=4) 
    # Place the picker buttons on the window
    air_picker_label.grid(row=6, column=0)
    air_picker_pick_button.grid(row=6, column=1)
    air_picker_place_button.grid(row=6, column=2)
    air_picker_nature_button.grid(row=6, column=3)
    air_picker_stop_button.grid(row=6, column=4)
    # Place buttons and labels for the position finder on the window
    position_finder_title.grid(row=7, column=0)
    position_finder_button.grid(row=7, column=1)
    position_finder_label.grid(row=7, column=2, columnspan=6)
    # Place the slider that rotates the arm to a specific angle
    rotate_to_angle_slider_label.grid(row=8, column=0)
    rotate_to_angle_slider.grid(row=8, column=1, columnspan=3)
    # Place the button that rotates the arm to 0 degrees
    rotate_to_0_button.grid(row=8, column=4)
    record_position_button.grid(row=9, column=0)
    record_pick_button.grid(row=9, column=1)
    record_place_button.grid(row=9, column=2)
    record_nat_button.grid(row=9, column=3)
# Place the slider on the window
distance_slider_label.grid(row=4, column=0)
distance_slider.grid(row=4, column=1, columnspan=3)
distance_decimal_slider.grid(row=4, column=4)
speed_slider_label.grid(row=5, column=0)
speed_slider.grid(row=5, column=1, columnspan=3)
run_gcode_button.grid(row=9, column=4)
# Servo B slider and button
servo_b_slider_label.grid(row=11, column=0)
servo_b_slider.grid(row=11, column=1, columnspan=3)
servo_b_button.grid(row=11, column=4)
record_servo_b_button.grid(row=11, column=5)
servo_c_slider_label.grid(row=12, column=0)
servo_c_slider.grid(row=12, column=1, columnspan=3)
servo_c_button.grid(row=12, column=4)
record_servo_c_button.grid(row=12, column=5)
# Dexarm 2
if dexarm2_connected:
    up_button2.grid(row=0, column=8)
    Z0_button2.grid(row=1, column=8)
    down_button2.grid(row=2, column=8)
    right_button2.grid(row=1, column=7)
    left_button2.grid(row=1, column=5)
    forward_button2.grid(row=0, column=6)
    backward_button2.grid(row=2, column=6)
    # home_button2.grid(row=1, column=6)
    # position1_button2.grid(row=2, column=7)
    rotate_to_0_button2.grid(row=8, column=5)
    record_position_button2.grid(row=9, column=5)
    record_pick_button2.grid(row=9, column=6)
    record_place_button2.grid(row=9, column=7)
    record_nat_button2.grid(row=9, column=8)
# Place the comment entry and button
comment_entry.grid(row=10, column=1, columnspan=2)
comment_button.grid(row=10, column=0)
# Place pipette controls
pipette_label.grid(row=10, column=6)
release_button.grid(row=10, column=7)
natural_button.grid(row=10, column=8)
intake_button.grid(row=10, column=9)
pipette_ejector_label.grid(row=11, column=6)
dispense_button.grid(row=11, column=7)
tip_natural_button.grid(row=11, column=8)
# Place cover controls
liquid_cover_label.grid(row=12, column=6)
liquid_cover_open_button.grid(row=12, column=7)
liquid_cover_close_button.grid(row=12, column=8)
tip_cover_label.grid(row=13, column=6)
tip_cover_open_button.grid(row=13, column=7)
tip_cover_close_button.grid(row=13, column=8)

# Bind the Shift_L key to the handle_shift_l function
root.bind("<Shift_L>", handle_shift_l)
# makes it so releasing the shift key sets the increment distance back to the original value
root.bind("<KeyRelease-Shift_L>", lambda event: distance_slider.set(current_distance_slider_value))

# Makes it so the w s a d keys can be used to control the dexarm
root.bind("<comma>", lambda event: move_forward())
root.bind("<o>", lambda event: move_backward())
root.bind("<a>", lambda event: move_left())
root.bind("<e>", lambda event: move_right())
root.bind("<p>", lambda event: move_up())
root.bind("<u>", lambda event: move_down())
# Makes the e button record a position
root.bind("<period>", lambda event: record_position())
# Makes it so the arrow keys can be used to control the dexarm2
root.bind("<Up>", lambda event: move_forward2())
root.bind("<Down>", lambda event: move_backward2())
root.bind("<Left>", lambda event: move_left2())
root.bind("<Right>", lambda event: move_right2())
root.bind("<minus>", lambda event: move_up2())
root.bind("<z>", lambda event: move_down2())
# Makes the enter button record the position of dexarm2
root.bind("<Return>", lambda event: record_position2())

# dexarm setup
dexarm.setup()

# Start the event loop
root.mainloop()


