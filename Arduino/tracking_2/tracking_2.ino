#include <Servo.h>

Servo panServo;
Servo tiltServo;



const uint8_t PAN_SERVO_MAX = 160;
const uint8_t PAN_SERVO_MIN = 20;
const uint8_t PAN_SERVO_CENTER = 90;
const int16_t PAN_SERVO_SENSITIVITY = int(500/max(PAN_SERVO_CENTER-PAN_SERVO_MIN, PAN_SERVO_MAX-PAN_SERVO_CENTER));

const uint8_t TILT_SERVO_MAX = 100;
const uint8_t TILT_SERVO_MIN = 10;
const uint8_t TILT_SERVO_CENTER = 65;
const int16_t TILT_SERVO_SENSITIVITY = int(500/max(TILT_SERVO_CENTER-TILT_SERVO_MIN, TILT_SERVO_MAX-TILT_SERVO_CENTER));

void initServos(){
  panServo.attach(9);
  tiltServo.attach(10);
  writePanUnits(500);
  writeTiltUnits(500);
}

void writePanUnits(int16_t val){
  //Tilt servo in integer, 500 is centered, 0 is min, 999 is max
  writePanServo(((val-500)/PAN_SERVO_SENSITIVITY) + PAN_SERVO_CENTER);  
}

void writeTiltUnits(int16_t val){
  //Tilt servo in integer, 500 is centered, 0 is min, 999 is max
  writeTiltServo(((val-500)/TILT_SERVO_SENSITIVITY) + TILT_SERVO_CENTER);  
}

void writeTiltServo(uint8_t pos){
  if(pos < TILT_SERVO_MIN){
    pos = TILT_SERVO_MIN;
  }
  else if(pos > TILT_SERVO_MAX){
    pos = TILT_SERVO_MAX;
  }
  tiltServo.write(pos);
}

void writePanServo(uint8_t pos){
  if(pos < PAN_SERVO_MIN){
    pos = PAN_SERVO_MIN;
  }
  else if(pos > PAN_SERVO_MAX){
    pos = PAN_SERVO_MAX;
  }
  panServo.write(pos);
}

//Nov 2020 Mark Gilliland

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  initServos();
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    Serial.print(command);
    
    // Parse the command
    if (command.startsWith("P") && command.indexOf("T") > 0) {
      int panPos = command.substring(1, command.indexOf("T")).toInt();
      int tiltPos = command.substring(command.indexOf("T") + 1).toInt();
  // if(Serial.available()){
  //   String newCommand = Serial.readStringUntil('\n');
  //   if(newCommand.startsWith("POS")){//POS pan tlt
  //     String panStr = newCommand.substring(4, 7);
  //     String tiltStr = newCommand.substring(8, 11);
  //     uint16_t panInt = panStr.toInt();
  //     uint16_t tiltInt = tiltStr.toInt();

      writePanUnits(panPos);
      writeTiltUnits(tiltPos);
    }
  }
}