#include <EEPROM.h>
#include <x10.h>
#include <x10constants.h>

#define zcPin 12
#define dataPin 13
#define MAXMSGLEN 100
#define button 6

char msg[MAXMSGLEN];
char inChar = -1;
int index = 0;
x10 myHouse = x10(zcPin, dataPin);

void setup() {
    Serial.begin(9600);
}


void loop()
{
    if (Serial.available() > 2) {
        while (Serial.available()) {
            if (index < MAXMSGLEN - 1) {
                inChar = Serial.read();
                msg[index++] = inChar;
                msg[index] = '\0';
            }
        }
        myHouse.write(msg[0], msg[1], 1);
        myHouse.write(msg[0], msg[2], 1);
        //Serial.println(msg[0], BIN);
        //Serial.println(msg[1], BIN);
        //Serial.println(msg[2], BIN);
        //Serial.println("endmsg");
        index = 0;
    }

    if (digitalRead(button)) {
        myHouse.write(A, UNIT_1, 1);
        myHouse.write(A, ON, 1);
        myHouse.write(A, UNIT_2, 1);
        myHouse.write(A, ON, 1);
        myHouse.write(A, UNIT_3, 1);
        myHouse.write(A, ON, 1);
    }

    //Programming a socket Rocket

    //myHouse.write(A, UNIT_2, 1);
    //myHouse.write(A, ON, 1);
    //delay(500);
}
