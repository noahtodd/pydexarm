from pydexarm import Dexarm
import tkinter as tk
import math
import serial
import time

'''windows'''
# try to open the dexarm on the port
dexarm = Dexarm("COM4")
dexarm2 = Dexarm("COM3")
arduino = serial.Serial('COM6', 115200, timeout=.2)  # Adjust the port name as needed

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

# Create a text file to store gcode commands
gcode_file = open("gcode_commands.txt", "w")

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
    print("Recording position: ", x, y, z)
    gcode_command = f"G1 X{x} Y{y} Z{z}\n"
    gcode_file.write(gcode_command)

def add_grip():
    dexarm.air_picker_pick()
    gcode_command = f"M1000\nG4 S1\n"
    gcode_file.write(gcode_command)

def add_release():
    dexarm.air_picker_place()
    gcode_command = f"M1001\nG4 S1\n"
    gcode_file.write(gcode_command)

def add_natural():
    dexarm.air_picker_nature()
    gcode_command = f"M1002\nG4 S1\n"
    gcode_file.write(gcode_command)

def run_gcode():
    gcode_file = open("gcode_commands_1.txt", "r")
    gcode_file2 = open("gcode_commands_2.txt", "r")
    gcode_file3 = open("gcode_commands_3.txt", "r")
    print("\nStarting sequence 1")
    for line in gcode_file:
        print(line)
        if line[0] == ";" or line[0] == "\n":
            continue
        else:
            dexarm._send_cmd(line)
    print("\nStarting sequence 2")
    for line in gcode_file2:
        print(line)
        if line[0] == ";" or line[0] == "\n":
            continue
        if line[0] in ["A", "B", "C"]:
            print("Sending command to arduino: ", line)
            arduino.write(bytes(line, 'utf-8'))
            time.sleep(0.05)
        else:
            dexarm2._send_cmd(line)
    print("\nStarting sequence 3")
    for line in gcode_file3:
        print(line)
        if line[0] == ";" or line[0] == "\n":
            continue
        else:
            dexarm._send_cmd(line)
    print("\nFinished running gcode")

def run_gcode2():
    gcode_file = open("gcode_commands_2.txt", "r")
    print("Starting sequence 2")
    for line in gcode_file:
        print(line)
        if line[0] == ";" or line[0] == "\n":
            continue
        if line[0] in ["A", "B", "C"]:
            print("Sending command to arduino: ", line)
            arduino.write(bytes(line, 'utf-8'))
            time.sleep(0.05)
        else:
            dexarm2._send_cmd(line)

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
    print("Recording position: ", x, y, z)
    gcode_command = f"G1 X{x} Y{y} Z{z}\n"
    gcode_file.write(gcode_command)

def add_grip2():
    dexarm2.air_picker_pick()
    gcode_command = f"M1000\n G4 S1\n"
    gcode_file.write(gcode_command)

def add_release2():
    dexarm2.air_picker_place()
    gcode_command = f"M1001\n G4 S1\n"
    gcode_file.write(gcode_command)

def add_natural2():
    dexarm2.air_picker_nature()
    gcode_command = f"M1002\n"
    gcode_file.write(gcode_command)

def add_comment():
    gcode_command = f"; {comment_entry.get()}\n"
    gcode_file.write(gcode_command)

'''
def arduino_send(x):
    # converts x to string and sends it to the arduino
    global arduino
    str_x = str(x)
    print("Sending command to arduino: ", str_x)
    arduino.write(bytes(str_x, 'utf-8'))
    time.sleep(0.05)
'''

# Create the main window
root = tk.Tk()
root.title("DexArm Control Panel")
root.minsize(600, 400)  # Set minimum size of the window to 500x400 pixels

# Configure minimum column widths for the columns spanned by the distance_slider
root.columnconfigure(0, minsize=100)
root.columnconfigure(1, minsize=100)
root.columnconfigure(2, minsize=100)
root.columnconfigure(3, minsize=100)
root.columnconfigure(4, minsize=200)
root.columnconfigure(5, minsize=100)
root.columnconfigure(6, minsize=100)
root.columnconfigure(7, minsize=100)
root.columnconfigure(8, minsize=100)

# Create a button and assign an action
up_button = tk.Button(root, text="Up", command=move_up)
Z0_button = tk.Button(root, text="Z0", command=move_Z0)
down_button = tk.Button(root, text="Down", command=move_down)
right_button = tk.Button(root, text="Right", command=move_right)
left_button = tk.Button(root, text="Left", command=move_left)
forward_button = tk.Button(root, text="Forward", command=move_forward)
backward_button = tk.Button(root, text="Backward", command=move_backward)
home_button = tk.Button(root, text="Home", command=dexarm.go_home)
# cut_line_button = tk.Button(root, text="Cut Line", command=cut_line)
position1_button = tk.Button(root, text="Position 1", command=position1)
# Create sliders
distance_slider_label = tk.Label(root, text="Increment Size, mm")
distance_slider = tk.Scale(root, from_=0, to=40, orient=tk.HORIZONTAL, command=distance_slider, length=300)
distance_slider.set(25)
# Create a slider for decimal values of the distance
distance_decimal_slider = tk.Scale(root, from_=0, to=.9, orient=tk.HORIZONTAL, command=distance_slider, length=100, resolution=0.1)
distance_decimal_slider.set(.4)
speed_slider_label = tk.Label(root, text="Speed, mm/min")
speed_slider = tk.Scale(root, from_=500, to=500*60, orient=tk.HORIZONTAL, command=speed_slider, length=300)
speed_slider.set(4000)
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
# Buttons for recording gcode commands
record_position_button = tk.Button(root, text="Record Position", command=record_position)
record_pick_button = tk.Button(root, text="Record Pick", command=add_grip)
record_place_button = tk.Button(root, text="Record Place", command=add_release)
record_nat_button = tk.Button(root, text="Record Nature", command=dexarm.air_picker_nature)
run_gcode_button = tk.Button(root, text="Run Gcode", command=run_gcode)
run_gcode_button2 = tk.Button(root, text="Run Gcode2", command=run_gcode2)
# Dexarm 2
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
comment_entry = tk.Entry(root)

'''release_button = tk.Button(root, text="Release", command=arduino_send(release))
natural_button = tk.Button(root, text="Natural", command=arduino_send(natural))
intake_button = tk.Button(root, text="Intake", command=arduino_send(intake))
dispense_button = tk.Button(root, text="Dispense", command=arduino_send(dispense))
'''
# Place the button on the window
up_button.grid(row=0, column=3)
home_button.grid(row=1, column=1)
Z0_button.grid(row=1, column=3)
down_button.grid(row=2, column=3)
right_button.grid(row=1, column=2)
left_button.grid(row=1, column=0)
forward_button.grid(row=0, column=1)
backward_button.grid(row=2, column=1)
# cut_line_button.grid(row=0, column=4)
position1_button.grid(row=2, column=4)
# Place the slider on the window
distance_slider_label.grid(row=4, column=0)
distance_slider.grid(row=4, column=1, columnspan=3)
distance_decimal_slider.grid(row=4, column=4)
speed_slider_label.grid(row=5, column=0)
speed_slider.grid(row=5, column=1, columnspan=3)
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
run_gcode_button.grid(row=9, column=4)
run_gcode_button2.grid(row=10, column=5)
# Dexarm 2
up_button2.grid(row=0, column=8)
Z0_button2.grid(row=1, column=8)
down_button2.grid(row=2, column=8)
right_button2.grid(row=1, column=7)
left_button2.grid(row=1, column=5)
forward_button2.grid(row=0, column=6)
backward_button2.grid(row=2, column=6)
home_button2.grid(row=1, column=6)
# position1_button2.grid(row=2, column=7)
rotate_to_0_button2.grid(row=8, column=5)
record_position_button2.grid(row=9, column=5)
record_pick_button2.grid(row=9, column=6)
record_place_button2.grid(row=9, column=7)
record_nat_button2.grid(row=9, column=8)
# Place the comment entry and button
comment_entry.grid(row=10, column=1, columnspan=4)
comment_button.grid(row=10, column=0)
# Place the arduino buttons
'''release_button.grid(row=11, column=0)
natural_button.grid(row=11, column=1)
intake_button.grid(row=11, column=2)
dispense_button.grid(row=11, column=3)'''

# dexarm setup
dexarm.setup()

# Start the event loop
root.mainloop()


