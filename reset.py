# Python Transmitter reset
# Cassie Lakin
# V1.0
# This program scans through all the transmitters and if any faults are found it will reset the transmitters accordingly
# as of 20/6/2025 this is just a mish mash of other scripts and will need work doing to make this run correctly




import serial
import pandas as pd

ser = serial.Serial('/dev/ttyS1')     # For use in field
ser.baudrate = 9600
ser.bytesize = 8
ser.parity = 'N'
ser.stopbits = 1
ser.timeout = 1

# Main Data String Array in bytes.
# 0 "STX" byte is always 55(hex).
# 1 "addr" is target microcontroller address in the range 1-254 decimal.
# 2 "Len" is the length of the data field. This is always 1 for command packets.
# 3 "cmd" is the command number 1-13.
# 4 "bcc" is the block checksum. This is the least significant 8 bits of the sum of bytes 1-3.
# This is the main packet. It will change depending on commands.
packet_to_send = bytearray([0x55, 0x01, 0x01, 0x01, 0x03])
logging_check = bytearray([0xff])
packet_to_log = bytearray([0x55, 0x01, 0x01, 0x01, 0x03])
radar_position = pd.read_csv("/home/radar/UOL_scripts/AGC_commander/antenna_positions.csv")

def logging_stuff():
    fault_counter = 0
    attempt_counter = 0

    for i in range(1):

        attempt_counter = attempt_counter + 1
        for radar in range(16):
            true_radar_position = (radar_position.loc[radar].at['agc'])
            logging_stuff.var = true_radar_position
            rad_value = int(true_radar_position, 16)
            packet_to_send[1] = rad_value
            packet_to_send[3] = 0x01
            packet_to_send[4] = (sum(packet_to_send[1:4]))
            ser.write(packet_to_send)
            data_received = ser.readall()
            expected_response = packet_to_send[0:1]
            logging_check_two = logging_check[0:1]

            if data_received[0:1] == expected_response:
                print("no comment")

                if data_received[14:15] == logging_check_two:
                    print("no comment")
                else:
                    fault_counter = fault_counter + 1
                    reset_mic()
            else:
                fault_counter = fault_counter + 1
                reset_mic()

def reset_mic():

    rad_value = int(logging_stuff.var, 16)
    print(rad_value)
    packet_to_send[1] = rad_value
    packet_to_send[3] = 0x0a
    packet_to_send[4] = (sum(packet_to_send[1:4]))
    ser.write(packet_to_send)
    print(packet_to_send)

logging_stuff()
