import serial
import time

PORT = "/dev/ttyUSB0"   # CHANGE THIS to your actual port

ser = serial.Serial(
    port=PORT,
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=0.5,
)

print(f"Listening on {PORT}...")
print("Ctrl+C to stop")

try:
    while True:
        data = ser.read(ser.in_waiting or 1)

        if data:
            print(f"RAW BYTES: {data!r}")

        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    ser.close()