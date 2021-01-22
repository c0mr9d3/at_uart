#!/usr/bin/env python3
import serial, threading, time, ctypes, sys, shelve
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
    send_data = ''
    db_commands = shelve.open("commands")
    print("Start!")
    while True:
        try:
            send_data = input()
            if db_commands.get(send_data):
                ser.write(db_commands.get(send_data).encode() + b'\n')
            else:
                ser.write(send_data.encode() + b'\n')

        except KeyboardInterrupt:
            ser.flush()
            ctypes.pythonapi.PyThreadState_SetAsyncExc(t.ident, ctypes.py_object(KeyboardInterrupt))
            db_commands.close()
            print("Exit")
            sys.exit(0)

def run_once(command):
    db_commands = shelve.open("commands")
    send_command = db_commands.get(command)
    ser = open_serial()
    mutex = threading.Lock()
    mutex.acquire()
    t = threading.Thread(target=read_ser, args=(ser, True, mutex))
    t.start()
    while mutex.locked():
        pass

    if send_command:
        ser.write(send_command.encode() + b'\r\n')
    else:
        ser.write(command.encode() + b'\r\n')

    db_commands.close()
    time.sleep(1)
    ctypes.pythonapi.PyThreadState_SetAsyncExc(t.ident, ctypes.py_object(SystemExit))


def options_parser():
    parser = OptionParser()
    parser.add_option('-e', '--execute', help='execute AT command once', metavar='COMMAND')
    parser.add_option('-b', '--baudrate', help='set speed for comport. On default is equal 9600', metavar='BAUDRATE')
    parser.add_option('-a', '--add', help='add alias on command. Use with option --command', metavar='alias')
    parser.add_option('-c', '--command', help='used for set alias on command', metavar='COMMAND')
    (options, args) = parser.parse_args()

    if options.baudrate:
        global BAUDRATE
        BAUDRATE = options.baudrate

    if options.add or options.command:
        if options.add and options.command:
            db = shelve.open("commands")
            db[options.add] = options.command
            db.close()
        else:
            print("Option --add used with --command")
            sys.exit(1)
        sys.exit(0)
    elif options.execute:
        run_once(options.execute)
    else:
        main()

if __name__ == '__main__':
    options_parser()
