import serial
import serial.tools.list_ports

class ServoController:
    def __init__(self, pan_angle=90, tilt_angle=65):
        self.pan_angle = pan_angle
        self.tilt_angle = tilt_angle
        self.arduino = None
        self.arduino_port = None
        self.connect_arduino()

    def connect_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Arduino" in port.description:
                try:
                    self.arduino = serial.Serial(port.device, 9600)
                    self.arduino_port = port.device
                    print(f"Connected to Arduino at {port.device}")
                    break
                except serial.SerialException as e:
                    print(f"Failed to connect to Arduino on {port.device}: {e}")
        if self.arduino is None:
            print("No Arduino detected.")
            self.arduino_port = None

    def is_connected(self):
        return self.arduino is not None and self.arduino.is_open

    def get_port(self):
        return self.arduino_port

    def move_servos(self, pan, tilt):
        command = f'P{pan}T{tilt}\n'
        if self.arduino and self.arduino.is_open:
            self.arduino.write(command.encode())
        # else: pass  # Optionally handle not connected

    def reset_servos(self):
        self.pan_angle = 90
        self.tilt_angle = 65
        self.move_servos(self.pan_angle, self.tilt_angle) 