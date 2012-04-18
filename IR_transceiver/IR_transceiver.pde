/* Webmote - Tranceiver Code

Authors: Daniel Myers, 

Description:
This code runs on all transcievers belonging to the webmote system
and is intended to allow two way communication via xbee modules.

Modus Operandi:
Refer to the README file in the webmote directory.

Thanks to Ken Shirriff for the IRremote library.
http://www.arcfn.com/2009/08/multi-protocol-infrared-remote-library.html
 * An IR LED must be connected to the output PWM pin 3.
*/

#include <EEPROM.h>
#include <IRremote.h>

#define recordWaitTime 3 //in minutes
#define MAXMSGLEN 100
#define RECV_PIN 11
#define BUTTON_PIN 8
#define STATUS_PIN 13


#define DEBUG true

IRrecv irrecv(RECV_PIN);
IRsend irsend;

decode_results results;

char message[MAXMSGLEN];
char inChar = -1;
int index = 0;
char commandType;
String data;
int messageDestination;
int transceiverID = 0;

// Storage for the recorded code
int codeType = -1; // The type of code
unsigned long codeValue; // The code value if not raw
unsigned int rawCodes[RAWBUF]; // The durations if raw
int codeLen; // The length of the code
int toggle = 0; // The RC5/6 toggle state

void setup() {
    Serial.begin(9600);
    restoreID();
    irrecv.enableIRIn(); // Start the receiver
    pinMode(BUTTON_PIN, INPUT);
    pinMode(STATUS_PIN, OUTPUT);
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
    digitalWrite(STATUS_PIN, HIGH);
    dPrint(data);
    dPrint("\n");

    // Why doesn't this work?
    sendCode(0, codeValue);

    digitalWrite(STATUS_PIN, LOW);
}

void recordCommand() {
    dPrint("Record command\n");
    digitalWrite(STATUS_PIN, HIGH);
    irrecv.enableIRIn();
    // Eventually should add a timeout here
    while (!irrecv.decode(&results)) {}
    storeCode(&results);
    irrecv.resume(); // resume receiver
    Serial.println("Should send this back to the server here");
    digitalWrite(STATUS_PIN, LOW);
}

void assignID() {
    digitalWrite(STATUS_PIN, HIGH);
    EEPROM.write(0, atoi(&data[0]));
    transceiverID = atoi(&data[0]);
    dPrint("Assigned ID to transceiver: ");
    dPrint(transceiverID);
    dPrint("\n");
    digitalWrite(STATUS_PIN, LOW);
}

void dPrint(String str) {
    if (DEBUG) {
        Serial.print(str);
    }
}

void dPrintHEX(unsigned long in) {
    if (DEBUG) {
        Serial.print(in, HEX);
    }
}

void dPrintDEC(unsigned int in) {
    if (DEBUG) {
        Serial.print(in, DEC);
    }
}

// Stores the code for later playback
// Most of this code is just logging
void storeCode(decode_results *results) {
    codeType = results->decode_type;
    int count = results->rawlen;
    if (codeType == UNKNOWN) {
        dPrint("Received unknown code, saving as raw\n");
        codeLen = results->rawlen - 1;
        // To store raw codes:
        // Drop first value (gap)
        // Convert from ticks to microseconds
        // Tweak marks shorter, and spaces longer to cancel out IR receiver distortion
        for (int i = 1; i <= codeLen; i++) {
            if (i % 2) {
                // Mark
                rawCodes[i - 1] = results->rawbuf[i]*USECPERTICK - MARK_EXCESS;
                dPrint(" m");
            } 
            else {
                // Space
                rawCodes[i - 1] = results->rawbuf[i]*USECPERTICK + MARK_EXCESS;
                dPrint(" s");
            }
            dPrintDEC(rawCodes[i - 1]);
        }
        dPrint("\n");
    }
    else {
        if (codeType == NEC) {
            dPrint("Received NEC: ");
            if (results->value == REPEAT) {
                // Don't record a NEC repeat value as that's useless.
                dPrint("repeat; ignoring.");
            return;
        }
    } 
    else if (codeType == SONY) {
        dPrint("Received SONY: ");
    } 
    else if (codeType == RC5) {
        dPrint("Received RC5: ");
    } 
    else if (codeType == RC6) {
        dPrint("Received RC6: ");
    } 
    else {
        dPrint("Unexpected codeType ");
        dPrintDEC(codeType);
    dPrint(" ");
    }
    dPrintHEX(results->value);
    dPrint("\n");
    codeValue = results->value;
    codeLen = results->bits;
  }
}

void sendCode(int repeat, long int new_code) {
    if (codeType == NEC) {
        codeValue = new_code;
        if (repeat) {
            irsend.sendNEC(REPEAT, codeLen);
            dPrint("Sent NEC repeat");
        } 
        else {
            irsend.sendNEC(codeValue, codeLen);
            dPrint("Sent NEC ");
            dPrintHEX(codeValue);
            dPrint("\n");
        }
    }
    else if (codeType == SONY) {
        irsend.sendSony(codeValue, codeLen);
        dPrint("Sent Sony ");
        dPrintHEX(codeValue);
        dPrint("\n");
    } 
    else if (codeType == RC5 || codeType == RC6) {
        if (!repeat) {
            // Flip the toggle bit for a new button press
            toggle = 1 - toggle;
        }
        // Put the toggle bit into the code to send
        codeValue = codeValue & ~(1 << (codeLen - 1));
        codeValue = codeValue | (toggle << (codeLen - 1));
        if (codeType == RC5) {
            irsend.sendRC5(codeValue, codeLen);
            dPrint("Sent RC5 ");
            dPrintHEX(codeValue);
            dPrint("\n");
        } 
        else {
            irsend.sendRC6(codeValue, codeLen);
            dPrint("Sent RC6 ");
            dPrintHEX(codeValue);
            dPrint("\n");
        }
    }
    else if (codeType == UNKNOWN /* i.e. raw */) {
        // Assume 38 KHz
        irsend.sendRaw(rawCodes, codeLen, 38);
        dPrint("Sent raw\n");
    }
}
