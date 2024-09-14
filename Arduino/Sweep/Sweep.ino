#include <Servo.h>

Servo pan; 
Servo tilt;

int pos = 0;    // variable to store the servo position

void setup() {
  pan.attach(9);
  pan.attach(10); 
}

void loop() {
  for (pos = 0; pos <= 180; pos += 1) { 
    pan.write(pos);              
    delay(15);                       
  }
  for (pos = 0; pos <= 180; pos += 1) { 
    tilt.write(pos);              
    delay(15);                       
  }
  for (pos = 180; pos >= 0; pos -= 1) { 
    pan.write(pos);              
    delay(15);                      
  }
  for (pos = 0; pos <= 180; pos += 1) { 
    tilt.write(pos);              
    delay(15);                       
  }
}
