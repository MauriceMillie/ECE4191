import serial

ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)
ser.readline()
while True:
    print(ser.readline())
