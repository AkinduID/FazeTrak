#include <Servo.h>

Servo panServo;
Servo tiltServo;

int panPin = 9;    // Pin connected to pan servo
int tiltPin = 10;  // Pin connected to tilt servo
int panAngle = 90; // Initial position for pan
int tiltAngle = 90; // Initial position for tilt

void setup() {
  Serial.begin(9600);
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    Serial.print(command);
    
    // Parse the command
    if (command.startsWith("P") && command.indexOf("T") > 0) {
      int panPos = command.substring(1, command.indexOf("T")).toInt();
      int tiltPos = command.substring(command.indexOf("T") + 1).toInt();
      
      // Move the servos
      panServo.write(panPos);
      tiltServo.write(tiltPos);
    }
  }
}
