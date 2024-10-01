#include <Servo.h>

Servo panServo;
Servo tiltServo;

int panPin = 9;     // Pin connected to pan servo
int tiltPin = 10;   // Pin connected to tilt servo
int panAngle = 90;  // Initial position for pan
int tiltAngle = 65; // Initial position for tilt

// PID coefficients
float Kp = 2.0;  // Proportional gain
float Ki = 0.0;  // Integral gain (can be tuned further)
float Kd = 0.0;  // Derivative gain

// PID variables
float prevErrorPan = 0;
float integralPan = 0;
float prevErrorTilt = 0;
float integralTilt = 0;

int maxServoSpeed = 10;  // Maximum change in degrees per iteration
int timeStep = 300;       // Time between PID updates in milliseconds

// Function to apply PID control to the servos
int pidControl(int target, int current, float &prevError, float &integral) {
  // Compute the error
  float error = target - current;

  // Calculate integral (accumulated error)
  integral += error * (timeStep / 1000.0);

  // Calculate derivative (rate of change of error)
  float derivative = (error - prevError) / (timeStep / 1000.0);

  // PID output
  float output = (Kp * error) + (Ki * integral) + (Kd * derivative);

  // Constrain output to prevent overshoot (limit the speed)
  output = constrain(output, -maxServoSpeed, maxServoSpeed);

  // Update previous error for next iteration
  prevError = error;

  // Return the new servo position based on the output
  return current + output;
}

// Function to move both servos using PID control
void move_servo(int panTarget, int tiltTarget) {
  unsigned long currentTime = millis();
  unsigned long previousTime = currentTime;

  // Move until both servos reach their targets
  while (panAngle != panTarget || tiltAngle != tiltTarget) {
    currentTime = millis();
    if (currentTime - previousTime >= timeStep) {
      // PID control for pan
      panAngle = pidControl(panTarget, panAngle, prevErrorPan, integralPan);
      panServo.write(panAngle);

      // PID control for tilt
      tiltAngle = pidControl(tiltTarget, tiltAngle, prevErrorTilt, integralTilt);
      tiltServo.write(tiltAngle);

      // Update the timestamp
      previousTime = currentTime;
    }
  }
}

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
      
      // Move the servos using PID control
      move_servo(panPos, tiltPos);
    }
  }
}
