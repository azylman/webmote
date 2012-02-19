/* Webmote - Tranceiver Code

Authors: Daniel Myers, 

Description:
This code runs on all transcievers belonging to the webmote system
and is intended to allow two way communication via xbee modules.

Modus Operandi:
Refer to the README file in the webmote directory.


*/


int LED = 10;
int PT = 11;

String message;
int commandType;
String command;
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

void restoreID() {}

void parseMessage(String message) {}

void playCommand() {}

void recordCommand() {}

void assignID() {
// This function should save the ID and Name to EEPROM
}

