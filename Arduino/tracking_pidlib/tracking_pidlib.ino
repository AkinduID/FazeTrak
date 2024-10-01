#include <Servo.h>
#include <PID_v1.h>  // Include the PID library

Servo panServo;
Servo tiltServo;

int panPin = 9;     // Pin connected to pan servo
int tiltPin = 10;   // Pin connected to tilt servo
int panAngle = 90;  // Initial position for pan
int tiltAngle = 65; // Initial position for tilt

// PID parameters
double panSetpoint, panInput, panOutput;  // Variables for pan PID
double tiltSetpoint, tiltInput, tiltOutput;  // Variables for tilt PID

double Kp = 1.0, Ki = 0.0, Kd = 0.5;  // PID tuning parameters

// Create PID controllers for pan and tilt
PID panPID(&panInput, &panOutput, &panSetpoint, Kp, Ki, Kd, DIRECT);
PID tiltPID(&tiltInput, &tiltOutput, &tiltSetpoint, Kp, Ki, Kd, DIRECT);

void setup() {
  Serial.begin(9600);
  
  // Attach the servos
  panServo.attach(panPin);
  tiltServo.attach(tiltPin);
  
  // Initialize the servos to the initial positions
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);

  // Initialize PID setpoints and inputs
  panSetpoint = panAngle;  // The target pan position
  panInput = panAngle;     // The current pan position
  
  tiltSetpoint = tiltAngle;  // The target tilt position
  tiltInput = tiltAngle;     // The current tilt position

  // Activate PID controllers
  panPID.SetMode(AUTOMATIC);
  tiltPID.SetMode(AUTOMATIC);
  
  // Optionally, set output limits for smooth servo movement
  panPID.SetOutputLimits(-10, 10);  // Adjust to limit servo speed
  tiltPID.SetOutputLimits(-10, 10); // Adjust to limit servo speed
}

void loop() {
  // Check if there is any serial input
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    Serial.print(command);
    
    // Parse the command (format: P<panAngle>T<tiltAngle>)
    if (command.startsWith("P") && command.indexOf("T") > 0) {
      int panPos = command.substring(1, command.indexOf("T")).toInt();
      int tiltPos = command.substring(command.indexOf("T") + 1).toInt();
      
      // Set the new target positions for the servos
      panSetpoint = panPos;
      tiltSetpoint = tiltPos;
    }
  }
  
  // Update PID inputs with the current positions of the servos
  panInput = panAngle;  // Current position of the pan servo
  tiltInput = tiltAngle;  // Current position of the tilt servo
  
  // Compute the PID output
  panPID.Compute();
  tiltPID.Compute();
  
  // Update the servo positions based on the PID outputs
  panAngle += panOutput;  // Adjust pan angle based on PID output
  tiltAngle += tiltOutput;  // Adjust tilt angle based on PID output

  // Write the new servo positions
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
  
  delay(20);  // Small delay for smoother movement
}
