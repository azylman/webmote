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
#define MAXMSGLEN 100
#define LED 10
#define PT 11

#define DEBUG true

char message[MAXMSGLEN];
char inChar = -1;
int index = 0;
char commandType;
String data;
int messageDestination;
int transceiverID = 0;

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
  
    if (Serial.available() > 2) {
        while (Serial.available()) {
            if (index < MAXMSGLEN - 1) {
                inChar = Serial.read();
                message[index++] = inChar;
                message[index] = '\0';
            }
            delay(100);
        }
        parseMessage(message);
        if (transceiverID == messageDestination) {
            switch (commandType) {
                case 'p':
                    playCommand();
                    break;
                case 'r':
                    recordCommand();
                    break;
                case 'a':
                    assignID();
                    break;
            }
        }
        index = 0;
    }
}

void requestID() {
    delay(5000); //make sure we don't flood the server
    Serial.println("IR_ID_REQUEST");
}

void restoreID() {
    transceiverID = EEPROM.read(0);
    dPrint("Restored ID as: ");
    dPrint(transceiverID);
    dPrint("\n");
}

void parseMessage(String message) {
    messageDestination = atoi(&message[0]);
    commandType = char(message[1]);
    data = message.substring(2);

    dPrint("\nParsed Message: \n");
    dPrint("\tDestination: ");
    dPrint(messageDestination);
    dPrint("\n\tCommand Type: ");
    dPrint(commandType);
    dPrint("\n\tData: ");
    dPrint(data);
    dPrint("\n");
}

void playCommand() {
    dPrint("Play command with data: ");
    dPrint(data);
    dPrint("\n");
    // Coming soon
  
}

void recordCommand() {
    dPrint("Record command\n");
    // Coming soon
}

void assignID() {
    EEPROM.write(0, atoi(&data[0]));
    transceiverID = atoi(&data[0]);
    dPrint("Assigned ID to transceiver: ");
    dPrint(transceiverID);
    dPrint("\n");
}

void dPrint(String str) {
    if (DEBUG) {
        Serial.print(str);
    }
}
