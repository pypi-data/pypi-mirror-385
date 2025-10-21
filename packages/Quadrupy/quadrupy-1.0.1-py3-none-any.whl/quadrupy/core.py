import serial
import time
import serial.tools.list_ports

class STQV1:
    def __init__(self, port=None):
        if port is None:
            port = self.find_esp32_port()
        print(f"Connecting to ESP32 on {port}...")
        self.esp32 = serial.Serial(port, baudrate=115200, timeout=1)
        time.sleep(2)  # let ESP32 reset

    def find_esp32_port(self):
        """Try to auto-detect the ESP32 COM port"""
        ports = serial.tools.list_ports.comports()
        for p in ports:
            if "Bluetooth" in p.description or "ESP32" in p.description:
                return p.device
        # fallback if nothing matches
        raise Exception("ESP32 port not found. Check Device Manager.")

    def send(self, cmd: str):
        """Send a string command to ESP32"""
        if not cmd.endswith("\n"):
            cmd += "\n"
        self.esp32.write(cmd.encode())
        print(f"Sent: {cmd.strip()}")

    def walk(self):
        self.send("walk()")

    def writeScreen(self, text):
        self.send(f'writeScreen("{text}")')

    def writeMotor(self, val):
        self.send(f"writeMotor({val})")

    def led(self, state: bool):
        if state:
            self.send("ON")
        else:
            self.send("OFF")

    def clearScreen(self):
        self.send("clearScreen()")

    def reset(self):
        self.send("reset()")

    def close(self):
        self.esp32.close()
        print("Connection closed")
