#!/usr/bin/env python
#
# This program automatically flashes eMMC memory connected to Renesas RZ-G2L/V2L SOC
#

import sys
import os
import time
import serial
import select
import time
from YModem import YModem

def progressBar(count_value, total, suffix=''):
    bar_length = 100
    filled_up_Length = int(round(bar_length* count_value / float(total)))
    percentage = round(100.0 * count_value/float(total),1)
    bar = '=' * filled_up_Length + '-' * (bar_length - filled_up_Length)
    sys.stdout.write('[%s] %s%s %s\r' %(bar, percentage, '%', suffix))
    sys.stdout.flush()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Simple eMMC flasher for Renesas RZ-G2L/V2L SoC')

    parser.add_argument(
        '-p', '--port',
        help="serial port name")

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='suppress non error messages',
        default=False)

    parser.add_argument(
        '-l', '--loader',
        help="Initial loader file (S-Record format!)")

    parser.add_argument(
        '-i', '--image',
        help="boot partition image file (binary format)")

    args = parser.parse_args()

    # connect to serial port
    ser = serial.Serial()
    ser.port = args.port
    ser.baudrate = 115200

    # open serial port
    print('Opening serial port: ' + args.port)
    try:
        ser.open()
    except serial.SerialException as e:
        sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
        sys.exit(1)

    print('Please perform board reset...')

    # wait for BOOTROM message
    while True:
        line = ser.readline().decode().strip()
        print('==> ' + line)

        if line == 'please send !':
            break

    start_time = time.time()

    print('sending loader...')

    loaderStream = open(args.loader, 'r')
    loader = loaderStream.readlines()
    count = 0
    for line in loader:
        ser.write(bytes(line, 'ascii'))
        count += 1
        progressBar(count, len(loader), os.path.basename(args.loader))

    print('')
    # wait for loader boot
    while True:
        line = ser.readline().decode().strip()
        print('==> ' + line)
        if line.find('Product Code :') != -1:
            break

    # send command to change speed to 921600
    time.sleep(0.5)

    print('switching to 921600...')
    ser.write(b'sup\r\n')
    while True:
        line = ser.readline().decode().strip()
        print('==> ' + line)
        if line.find('921.6Kbps') != -1:
            break

    ser.baudrate = 921600

    time.sleep(0.1)

    # wait until new baudrate setting is active
    while True:
        time.sleep(0.1)
        ser.write(b'\r\n')
        line = ser.readline().decode().strip()
        print('==> ' + line )
        if line == '>':
            break

    # send boot partition image
    print('sending binary file...')

    ser.write(b'EM_WYB1\r\n')

    while True:
        line = ser.readline().decode().strip()
        print('==> ' + line )
        if line == 'Please send a file (YMODEM)!':
            break

    def sender_getc(size):
        return ser.read(size) or None

    def sender_putc(data, timeout=15):
        return ser.write(data)

    def ymodem_progress(pos, total):
        progressBar(pos, total, os.path.basename(args.image))

    ymodem = YModem(sender_getc, sender_putc, data_pad=b'\xFF')

    ymodem_progress(0,1)
    ymodem.send_file(args.image, 20, ymodem_progress)

    while True:
        line = ser.readline().decode().strip()
        print('==> ' + line )
        if line == 'EM_WYB done':
            break

    # change eMMC configuration
    ser.write(b'EM_BCFG\r\n')

    while True:
        line = ser.readline().decode().strip()
        print('==> ' + line )
        if line == 'EM_BCFG done':
            break
    print("device flashed successfully!")

    # print elapsed time for debugging
    print("Elapsed time: ", int(time.time() - start_time), " seconds")

    exit()
