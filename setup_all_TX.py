# Python Transmitter AGC Open
# Matthew Jones
# V1.0
# This program scans through all the transmitters and opens AGC loop
# as of 20/6/2025 this is just a mish mash of other scripts and will need work doing to make this run correctly

import serial
import pandas as pd

ser = serial.Serial('/dev/ttyS0')     # For use in field
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
radar_position = pd.read_csv("/home/radar/UOL_scripts/Antenna_Positions_CSV/antenna_positions.csv")

print() # blank line to aid readability

def configure_tx(addr):

    # Retreive address for TX from file and convert to int
    radar_addr_hex = (radar_position.loc[addr].at['agc'])
    rad_addr = int(radar_addr_hex, 16)

    # ==========================================================
    # Check current TX status
    # Create status packet to send
    packet_to_send[1] = rad_addr
    packet_to_send[3] = 0x01
    packet_to_send[4] = (sum(packet_to_send[1:4]))

    # Send read status command and get response
    ser.write(packet_to_send)
    sts_data_received = ser.readall()

    # Check for valid header in response
    if sts_data_received[3] == packet_to_send[1]:
        print('Response received, TX position: ', addr+1)
    else:
        print('No or invalid response received, TX position: ', addr+1)
        return()

    # ==========================================================
    # Check AGC loop status and open if needed

    # Check if AGC loop closed
    if ((sts_data_received[13] >> 4) & 1) == 1:
        # If AGC loop closed then open

        # Create AGC open packet
        packet_to_send[3] = 0x05
        packet_to_send[4] = (sum(packet_to_send[1:4]))

        # Send AGC open command and get response
        ser.write(packet_to_send)
        data_received = ser.readall()

        # Check for valid header in response
        if data_received[0:1] == packet_to_send[0:1]:
            print('AGC loop opened, TX position: ', addr+1)
        else:
            print('No or invalid response received, TX position: ', addr+1)
            return()

    else:
        print('AGC loop already open, TX position: ', addr+1)


    # ==========================================================
    # Check relay status and close if needed

    # Check if relay open
    if ((sts_data_received[12] >> 0) & 1) == 0:
        # If relay open then close

        # Create relay close packet
        packet_to_send[3] = 0x02
        packet_to_send[4] = (sum(packet_to_send[1:4]))

        # Send relay close command and get response
        ser.write(packet_to_send)
        data_received = ser.readall()

        # Check for valid header in response
        if data_received[0:1] == packet_to_send[0:1]:
            print('Relay closed, TX position: ', addr+1)
        else:
            print('No or invalid response received, TX position: ', addr+1)
            return()

    else:
        print('Relay already closed, TX position: ', addr+1)


    # ==========================================================
    # Turn on auto reset (note: current setting is not in packet, so have to send regardless)

    # Create enable auto reset packet
    packet_to_send[3] = 0x0C
    packet_to_send[4] = (sum(packet_to_send[1:4]))

    # Send auto reset command and get response
    ser.write(packet_to_send)
    data_received = ser.readall()

    # Check for valid header in response
    if data_received[0:1] == packet_to_send[0:1]:
        print('Auto reset enabled, TX position: ', addr+1)
    else:
        print('No or invalid response received, TX position: ', addr+1)
        return()



#def reset_mic():
#
#    rad_value = int(logging_stuff.var, 16)
#    print(rad_value)
#    packet_to_send[1] = rad_value
#    packet_to_send[3] = 0x0a
#    packet_to_send[4] = (sum(packet_to_send[1:4]))
#    #ser.write(packet_to_send)
#    print(packet_to_send)

for radar in range(16):
    print('=== Radar Position ', radar+1, ' ===')
    configure_tx(radar)
    print('')
