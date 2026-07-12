"""
Serial interface to the Arduino-based pan/tilt servo rig.

The Arduino is expected to accept ASCII commands of the form ``P{pan}T{tilt}``
(e.g. ``P90T65``) terminated by a newline, and to expose itself over USB with
a hardware ID containing ``config.ARDUINO_USB_HWID``.
"""

import logging

import serial
import serial.tools.list_ports

from fazetrak import config

logger = logging.getLogger(__name__)


class ServoController:
    """
    Manages the serial connection to the pan/tilt servo rig and tracks the
    current commanded angles.

    If no matching Arduino is plugged in, the controller degrades gracefully:
    ``is_connected()`` returns False and ``move_to()`` becomes a no-op logged
    at debug level, so the rest of the application can run (e.g. for
    development on a machine without the physical hardware attached).
    """

    def __init__(
        self,
        initial_pan_angle: int = config.DEFAULT_PAN_ANGLE_DEGREES,
        initial_tilt_angle: int = config.DEFAULT_TILT_ANGLE_DEGREES,
    ) -> None:
        self.pan_angle_degrees = initial_pan_angle
        self.tilt_angle_degrees = initial_tilt_angle

        self._serial_connection: serial.Serial | None = None
        self._connected_port_name: str | None = None

        self.connect_to_arduino()

    def connect_to_arduino(self) -> None:
        """
        Scan all serial ports and open a connection to the first device
        whose USB hardware ID matches the tracking rig's Arduino.

        Safe to call again later to retry the connection (e.g. after the
        device was plugged in mid-session).
        """
        matching_port = self._find_arduino_port()
        if matching_port is None:
            logger.info("No matching Arduino found on any serial port.")
            self._serial_connection = None
            self._connected_port_name = None
            return

        try:
            self._serial_connection = serial.Serial(
                matching_port.device,
                config.SERIAL_BAUD_RATE,
                timeout=config.SERIAL_READ_TIMEOUT_SECONDS,
                write_timeout=config.SERIAL_WRITE_TIMEOUT_SECONDS,
            )
            self._connected_port_name = matching_port.device
            logger.info(
                "Connected to Arduino at %s (hwid=%s)",
                matching_port.device,
                matching_port.hwid,
            )
        except serial.SerialException:
            logger.exception("Failed to open serial connection to %s", matching_port.device)
            self._serial_connection = None
            self._connected_port_name = None

    @staticmethod
    def _find_arduino_port() -> serial.tools.list_ports_common.ListPortInfo | None:
        """Return the first available serial port matching the rig's Arduino, if any."""
        for port in serial.tools.list_ports.comports():
            if config.ARDUINO_USB_HWID in port.hwid:
                return port
        return None

    def is_connected(self) -> bool:
        """Return True if a serial connection to the Arduino is currently open."""
        return self._serial_connection is not None and self._serial_connection.is_open

    def get_connected_port_name(self) -> str | None:
        """Return the device path of the connected serial port, or None if not connected."""
        return self._connected_port_name

    def move_to(self, pan_angle_degrees: int, tilt_angle_degrees: int) -> None:
        """
        Command the servos to a specific pan/tilt position and update the
        controller's stored angles to match.

        If there is no active connection, this simply logs the attempt and
        returns without raising.
        """
        self.pan_angle_degrees = pan_angle_degrees
        self.tilt_angle_degrees = tilt_angle_degrees

        if not self.is_connected():
            logger.debug(
                "Skipping servo move (not connected): pan=%d tilt=%d",
                pan_angle_degrees,
                tilt_angle_degrees,
            )
            return

        command = f"P{int(pan_angle_degrees)}T{int(tilt_angle_degrees)}\n"
        try:
            self._serial_connection.write(command.encode())
            self._serial_connection.flush()
            logger.debug("Sent servo command: %s", command.strip())
        except serial.SerialTimeoutException:
            logger.warning("Serial write timed out while sending servo command.")
        except serial.SerialException:
            logger.exception("Serial write failed while sending servo command.")

    def reset_to_default_position(self) -> None:
        """Recenter the servos to their default pan/tilt angles."""
        logger.info("Resetting servos to default position.")
        self.move_to(config.DEFAULT_PAN_ANGLE_DEGREES, config.DEFAULT_TILT_ANGLE_DEGREES)
