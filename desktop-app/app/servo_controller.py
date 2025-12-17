import serial
import serial.tools.list_ports
import logging

logger = logging.getLogger(__name__)

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
            if "303A:1001" in port.hwid:
                try:
                    # Add timeout to prevent blocking
                    self.arduino = serial.Serial(
                        port.device, 
                        115200,
                        timeout=0.01,          # Read timeout: 10ms
                        write_timeout=0.01     # Write timeout: 10ms
                    )
                    self.arduino_port = port.device
                    print(f"Connected to MCU at {port.device} {port.hwid}")
                    logger.info(f"Serial connection established with timeouts")
                    break
                except serial.SerialException as e:
                    print(f"Failed to connect to MCU on {port.device}: {e}")
                    logger.error(f"Connection failed: {e}")
        if self.arduino is None:
            print("No MCU detected.")
            self.arduino_port = None

    def is_connected(self):
        return self.arduino is not None and self.arduino.is_open

    def get_port(self):
        return self.arduino_port

    def move_servos(self, pan, tilt):
        command = f'P{int(pan)}T{int(tilt)}\n'
        if self.arduino and self.arduino.is_open:
            try:
                logger.debug(f"Sending command: {command.strip()}")
                self.arduino.write(command.encode())
                self.arduino.flush()  # Ensure data is sent immediately
                logger.debug("Command sent successfully")
            except serial.SerialTimeoutException:
                logger.warning("Serial write timeout - continuing")
            except Exception as e:
                logger.error(f"Serial write error: {e}")

    def reset_servos(self):
        self.pan_angle = 90
        self.tilt_angle = 65
        self.move_servos(self.pan_angle, self.tilt_angle)