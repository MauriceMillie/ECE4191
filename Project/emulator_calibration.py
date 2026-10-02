import serial
import time
import re

PORT = "/dev/serial/by-id/usb-FTDI_TTL232R_FTEAE3LA-if00-port0"

ser = serial.Serial(
    PORT,
    baudrate=9600,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=0.2
)

command = input("Command (e.g. D128, C128, D000): ").strip().upper()

ser.reset_input_buffer()
ser.write(command.encode("ascii"))
ser.flush()

print(f"Sent {command}")
print("time_s, raw_soc")

start = time.monotonic()
buffer = ""

try:
    while time.monotonic() - start < 20:
        data = ser.read(ser.in_waiting or 1)

        if data:
            buffer += data.decode("ascii", errors="ignore")

            matches = list(re.finditer(r"\d{5}", buffer))

            for match in matches:
                raw = int(match.group())

                if 0 <= raw <= 65500:
                    t = time.monotonic() - start
                    print(f"{t:6.2f}, {raw}")

            if matches:
                buffer = buffer[matches[-1].end():]

finally:
    ser.write(b"D000")
    ser.flush()
    ser.close()
    print("Stopped emulator with D000")