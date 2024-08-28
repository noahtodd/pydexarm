from pydexarm import Dexarm

'''windows'''
#dexarm = Dexarm("COM67")
'''mac & linux'''
dexarm = Dexarm("/dev/cu.usbmodem315D378032331")# /dev/tty.usbmodem3086337A34381") #315D37803233

dexarm.go_home()

dexarm.move_to(50, 300, 0)
dexarm.move_to(50, 300, -50)
dexarm.air_picker_pick()
dexarm.move_to(50, 300, 0)
dexarm.move_to(-50, 300, 0)
dexarm.move_to(-50, 300, -50)
dexarm.relative_move(0, 0, 10)
dexarm.air_picker_place()
dexarm.air_picker_nature()

dexarm.go_home()