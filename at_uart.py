#!/usr/bin/env python3
import serial, threading, time, ctypes, sys
from optparse import OptionParser
from serial.tools import list_ports

COMPORT = '/dev/ttyS0'
BAUDRATE = 9600

def read_ser(ser, once=False, mutex=None):
    msg = b''
    c = 0
    if mutex:
        mutex.release()

    while True:
        try:
            msg += ser.read()
            if msg.endswith(b'\n'):
                msg.strip()
                try:
                    print(msg.decode(), end='')
                except UnicodeError:
                    print(msg)
                if once == True:
                    if c == 1:
                        raise SystemExit
                    c += 1
                msg = b''

        except serial.serialutil.SerialException as e:
            print(e)
            raise SystemExit
        except KeyboardInterrupt:
            print("Close reading thread")
            sys.exit(0)

def open_serial():
    try:
        ser = serial.Serial(COMPORT, baudrate=BAUDRATE, timeout=1)
    except (serial.serialutil.SerialException, FileNotFoundError):
        print("Can't open %s" % COMPORT)
        raise SystemExit
    return ser

def main():
    global COMPORT
    print("Exists comports:")
    for j, i in enumerate(list_ports.comports()):
        print("\t[%d] - %s" % (j, list_ports.comports()[j].device), sep='')

    print("On default use port: %s" % COMPORT)
    print("Choose comport or any button except numbers for continue: ", end='')
    c = input()
    try:
        c = int(c)
    except ValueError:
        pass

    if type(c) == int:
        try:
            COMPORT = list_ports.comports()[int(c)].device
        except (ValueError, IndexError):
            print("Incorrect number")
            raise SystemExit

    ser = open_serial()
    t = threading.Thread(target=read_ser, args=(ser,))
    t.start()
    i = ''
    print("Start!")
    while True:
        try:
            i = input()
            ser.write(i.encode() + b'\n')
        except KeyboardInterrupt:
            ser.flush()
            ctypes.pythonapi.PyThreadState_SetAsyncExc(t.ident, ctypes.py_object(KeyboardInterrupt))
            print("Exit")
            sys.exit(0)

def run_once(command):
    ser = open_serial()
    mutex = threading.Lock()
    mutex.acquire()
    t = threading.Thread(target=read_ser, args=(ser, True, mutex))
    t.start()
    while mutex.locked():
        pass
    ser.write(command.encode() + b'\r\n')
    time.sleep(1)
    ctypes.pythonapi.PyThreadState_SetAsyncExc(t.ident, ctypes.py_object(SystemExit))


def options_parser():
    parser = OptionParser()
    parser.add_option('-e', '--execute', help='execute AT command once', metavar='COMMAND')
    parser.add_option('-b', '--baudrate', help='set speed for comport. On default is equal 9600', metavar='BAUDRATE')
    (options, args) = parser.parse_args()

    if options.baudrate:
        global BAUDRATE
        BAUDRATE = options.baudrate

    if options.execute:
        run_once(options.execute)
    else:
        main()

if __name__ == '__main__':
    options_parser()
