#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

from dynamixel_sdk import *                    # Uses Dynamixel SDK library

# DYNAMIXEL Model definition
MY_DXL = 'MX_SERIES'

# Control table address
ADDR_TORQUE_ENABLE = 64
ADDR_GOAL_POSITION = 116
ADDR_PRESENT_POSITION = 132
LEN_GOAL_POSITION = 4
LEN_PRESENT_POSITION = 4
DXL_MINIMUM_POSITION_VALUE = 1310
DXL_MAXIMUM_POSITION_VALUE = 2566
BAUDRATE = 2000000

PROTOCOL_VERSION = 2.0

# Dynamixel IDs
DXL_IDS = [8, 28, 27, 26, 25, 24, 11, 16, 17, 15, 5]

DEVICENAME = '/dev/tty.usbserial-FT7WBEJS'

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DXL_MOVING_STATUS_THRESHOLD = 20

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)
packetHandler = PacketHandler(PROTOCOL_VERSION)

if portHandler.openPort():
    print("Succeeded to open the port")
else:
    print("Failed to open the port")
    print("Press any key to terminate...")
    getch()
    quit()

if portHandler.setBaudRate(BAUDRATE):
    print("Succeeded to change the baudrate")
else:
    print("Failed to change the baudrate")
    print("Press any key to terminate...")
    getch()
    quit()

# Enable torque for all motors
for DXL_ID in DXL_IDS:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % DXL_ID)

def main_menu():
    while True:
        print("\nMain Menu:")
        print("Select a motor to control (Enter ID number) or press ESC to quit:")
        print("Available Motors:", DXL_IDS)
        user_input = getch()

        if user_input == chr(0x1b):  # ESC key
            return None
        elif user_input.isdigit() and int(user_input) in DXL_IDS:
            return int(user_input)
        else:
            print("Invalid input, please try again.")

def control_motor(dxl_id):
    print(f"\nControlling Dynamixel#{dxl_id}. Use arrow keys to control. Press SPACE to return to main menu.")
    current_position = (DXL_MINIMUM_POSITION_VALUE + DXL_MAXIMUM_POSITION_VALUE) // 2

    while True:
        print(f"Current Position: {current_position}")
        key = getch()
        
        if key == ' ':  # Space bar to return to main menu
            break
        elif key == '\x1b[C':  # Right arrow key
            current_position = min(DXL_MAXIMUM_POSITION_VALUE, current_position + 10)
        elif key == '\x1b[D':  # Left arrow key
            current_position = max(DXL_MINIMUM_POSITION_VALUE, current_position - 10)

        # Write goal position
        param_goal_position = [DXL_LOBYTE(DXL_LOWORD(current_position)), DXL_HIBYTE(DXL_LOWORD(current_position)),
                               DXL_LOBYTE(DXL_HIWORD(current_position)), DXL_HIBYTE(DXL_HIWORD(current_position))]
        dxl_comm_result, dxl_error = packetHandler.write4ByteTxRx(portHandler, dxl_id, ADDR_GOAL_POSITION, current_position)
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

# Main loop
while True:
    selected_motor = main_menu()
    if selected_motor is None:
        break
    control_motor(selected_motor)

# Disable torque for all motors
for DXL_ID in DXL_IDS:
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(portHandler, DXL_ID, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packetHandler.getRxPacketError(dxl_error))

portHandler.closePort()
print("Program terminated.")
