/* Webmote - Tranceiver Code

Authors: Daniel Myers, 

Description:
This code runs on all transcievers belonging to the webmote system
and is intended to allow two way communication via xbee modules.

Modus Operandi:
Refer to the README file in the webmote directory.


*/

#include <EEPROM.h>
#define recordWaitTime 3 //in minutes

int LED = 10;
int PT = 11;

String message;
int commandType;
String data;
int messageDestination;
int transceiverID = 0;
String transceiverName;

void setup() {
  pinMode(LED, OUTPUT);
  pinMode(PT, INPUT);
  Serial.begin(9600);
  restoreID();
}

void loop() {
  if (!transceiverID) {
    requestID();
  }
  
  if (Serial.available() > 0) {
    message = Serial.read();
    parseMessage(message);
    if (transceiverID == messageDestination) {
      switch (commandType) {
      case 'p':
        playCommand();
      case 'r':
        recordCommand();
      case 'a':
        assignID();
      }
    }
  }
}

void requestID() {
  delay(5000); //make sure we don't flood the server
}

void restoreID() {
  transceiverID = EEPROM.read(0);
}

void parseMessage(String message) {
  messageDestination = int(message[0]);
  commandType = message[1];
  data = message.substring(2);
}

void playCommand() {
  // Need to know a bit more about IR signaling.
  
}

void recordCommand() {
  unsigned long time = 0;
  while (time <
}

void assignID() {
  EEPROM.write(0, int(data));
}

