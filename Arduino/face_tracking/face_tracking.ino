#include <ESP32Servo.h>

// Create servo objects
Servo panServo;
Servo tiltServo;

// Define pins for the servos
int panPin = 9;    // Pin connected to pan servo
int tiltPin = 10;  // Pin connected to tilt servo

// Initial positions for servos
int panAngle = 90;  // Initial position for pan
int tiltAngle = 65; // Initial position for tilt

void setup() {
  Serial.begin(9600);

  // Attach the servos to the pins
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);

  // Move servos to initial positions
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
}

void loop() {
  if (Serial.available() > 0) {
    // Read command from Serial input
    String command = Serial.readStringUntil('\n');
    Serial.print(command);

    // Parse the command
    if (command.startsWith("P") && command.indexOf("T") > 0) {
      int panPos = command.substring(1, command.indexOf("T")).toInt();
      int tiltPos = command.substring(command.indexOf("T") + 1).toInt();

      // Constrain positions to valid servo range (0-180 degrees)
      panPos = constrain(panPos, 0, 180);
      tiltPos = constrain(tiltPos, 0, 180);

      // Move the servos
      panServo.write(panPos);
      tiltServo.write(tiltPos);
    }
  }
}
