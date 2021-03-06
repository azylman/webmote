from django.db import models
from django.forms import ModelForm
from django import forms
from django.forms.widgets import *
from django.contrib.auth.models import User

import serial, sys, os, glob, time
import struct

################
# Webmote Device
################

class Devices(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=100)

    def getSubclassInstance(self):
        for deviceType in Devices.__subclasses__():
            device = deviceType.objects.filter(name=self.name)
            if len(device):
                return device[0]
        return False

    def getDeviceForm(self):
        device = self
        if self.getSubclassInstance():
            device = self.getSubclassInstance()
        deviceType = type(device)
        for devicesFormType in DevicesForm.__subclasses__():
            typeName = devicesFormType.__name__.replace('_DevicesForm', '')
            if typeName in type(device).__name__.replace('_Devices', ''):
                return devicesFormType
        return False    

    def getCorrespondingCommandType(self):
        for commandsType in Commands.__subclasses__():
            typeName = commandsType.__name__.replace('_Commands', '')
            if typeName in type(self.getSubclassInstance()).__name__.replace('_Devices', ''):
                return commandsType
        return False

    def getEmptyCommandsForm(self):
        for commandsFormType in CommandsForm.__subclasses__():
            typeName = commandsFormType.__name__.replace('_CommandsForm', '')
            if typeName in type(self.getSubclassInstance()).__name__.replace('_Devices', ''):
                return commandsFormType
        return False

    def runCommand(self, command):
        return self.getSubclassInstance().runCommand(command)

class DevicesForm(ModelForm):
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Kitchen, Den, etc.'}))
    class Meta:
        model = Devices

def getDeviceTypeTuples():
    deviceTypes = []
    for deviceType in Devices.__subclasses__():
        deviceTypes.append((deviceType.__name__.replace('_Devices', ''), deviceType.__name__.replace('_Devices', '')))
    return deviceTypes

DEVICE_TYPES = getDeviceTypeTuples()

#################
# Webmote Command
#################

class Commands(models.Model):
    name = models.CharField(max_length=100)
    device = models.ForeignKey(Devices)

    def getSubclassInstance(self):
        for commandType in Commands.__subclasses__():
            command = commandType.objects.filter(name=self.name, device=self.device)
            if len(command):
                return command[0]
        return False

class CommandsForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. On, Off, etc.'}))
    class Meta:
        model = Commands

################
# Profiles
################    

class Profiles(models.Model):
    profileName = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    device = models.ForeignKey(Devices)
    deviceState = models.CharField(max_length=100)
    lastCommand = models.IntegerField(null=True)

################
# Macros
################

class Macros(models.Model):
    macroName = models.CharField(max_length=100)
    command = models.ForeignKey(Commands, null=True)
    macro = models.ForeignKey('self', null=True)
    profile = models.ForeignKey(Profiles, null=True)
    user = models.ForeignKey(User)
    def runnable(self):
        return self.command or self.macro or self.profile
    def getActionName(self):
        if self.runnable:
            if self.command:
                return self.command.device.name + ' - ' + self.command.name
            if self.macro:
                return self.macro.macroName
            if self.profile:
                return self.profile.profileName

################
# Transcievers
################

class Transceivers(models.Model):
    type = models.CharField(max_length=100, choices=getDeviceTypeTuples())
    location = models.CharField(max_length=100)
    def assignID(self, reset = False):
        try:
            ser = serial.Serial('/dev/ttyUSB0', 9600)
            if reset:
#                ser.write(chr(self.id) + 'a' + str(0))
                ser.write(str(self.id) + 'a' + str(0))
                print chr(self.id)
            else:
#                ser.write(str(0) + 'a' + chr(self.id))
                ser.write(str(0) + 'a' + str(self.id))
#            response = ser.readline()
            print 'assigned tranceiver id: ' + str(self.id)
        except Exception, exc:
            print str(exc)
        
    def delete(self, *args, **kwargs):
        self.assignID(True)
        print 'resetting transceiver'
        super(Transceivers, self).delete(*args, **kwargs)

class TransceiversForm(ModelForm):
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'e.g. Kitchen, Den, etc.'}))
    type = forms.CharField(widget=forms.TextInput(attrs={'readonly' : True}))
    class Meta:
        model = Transceivers
        exclude = ('trans_id',)


################
# Remotes
################

STYLES = (
    (1, 'Grid'),
    (2, 'List (not implemented)'),
    (3, 'Custom (not implemented)'),
)

class Remote(models.Model):
    name = models.CharField(max_length=100)
    style = models.IntegerField(choices=STYLES)
    user = models.ForeignKey(User)
    rows = models.IntegerField()

class RemoteForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'e.g. Watch TV, Lights, etc.'}))
    style = forms.ChoiceField(choices=STYLES)
    rows = forms.IntegerField(min_value=1, max_value=20, widget=forms.TextInput(attrs={'placeholder' : 'a number between 1 and 20'}))
    class Meta:
        model = Remote
        exclude = ('user',)

################
# Buttons
################
ICONS = (
    ('arrow-l', 'Left Arrow'),
    ('arrow-r', 'Right Arrow'),
    ('arrow-u', 'Up Arrow'),
    ('arrow-d', 'Down Arrow'),
    ('delete', 'Delete'),
    ('plus', 'Plus'),
    ('minus', 'Minus'),
    ('check', 'Check'),
    ('gear', 'Gear'),
    ('refresh', 'Refresh'),
    ('forward', 'Forward'),
    ('back', 'Back'),
    ('grid', 'Grid'),
    ('star', 'Star'),
    ('alert', 'Alert'),
    ('info', 'Info'),
    ('home', 'Home'),
    ('search', 'Search'),
)

class Button(models.Model):
    name = models.CharField(max_length=100, null=True)
    x = models.IntegerField()
    y = models.IntegerField()
    icon = models.CharField(max_length=50, choices=ICONS)
    command = models.ForeignKey(Commands, null=True)
    macro = models.ForeignKey(Macros, null=True)
    profile = models.ForeignKey(Profiles, null=True)
    url = models.CharField(max_length=1000, null=True)
    remote = models.ForeignKey(Remote)

class ButtonForm(ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder' : 'e.g. Volume Up, Light On, etc.'}))
    icon = forms.ChoiceField(choices=ICONS)
    class Meta:
        model = Button
        exclude = ('x', 'y', 'command', 'macro', 'profile', 'url', 'remote',)

################
# X10
################

X10_DEVICE_TYPES = (
    ('On-Off Light', 'On-Off Light'),
    ('Dimmable Light', 'Dimmable Light'),
)

# Will probably put some popular models in
X10_KNOWN_MODELS = (
    ('LM15A', 'Socket Rocket (LM15A)'),
    ('123abc', 'Socket Rocket Dimmer (123abc)'),
)

X10_DEFAULT_USER_COMMANDS = {}
X10_DEFAULT_USER_COMMANDS['LM15A'] = ['On', 'Off']

# These values are directly from the x10constants.h file from the arduino x10 library.
HOUSE_CODES = {'A': 'B0110', 'B': 'B1110', 'C': 'B0010','D': 'B1010','E': 'B0001','F': 'B1001','G': 'B0101','H': 'B1101','I': 'B0111','J': 'B1111','K': 'B0011','L': 'B1011','M': 'B0000','N': 'B1000','O': 'B0100','P': 'B1100'}

UNIT_CODES = {'1': 'B01100','2': 'B11100','3': 'B00100','4': 'B10100','5': 'B00010','6': 'B10010','7': 'B01010','8': 'B11010','9': 'B01110','10': 'B11110','11':'B00110','12': 'B10110','13': 'B00000','14': 'B10000','15': 'B01000','16': 'B11000'}

COMMAND_CODES = {'ALL_UNITS_OFF': 'B00001','ALL_LIGHTS_ON': 'B00011','ON': 'B00101','OFF': 'B00111','DIM': 'B01001','BRIGHT': 'B01011','ALL_LIGHTS_OFF': 'B01101','EXTENDED_CODE': 'B01111','HAIL_REQUEST': 'B10001','HAIL_ACKNOWLEDGE': 'B10011','PRE_SET_DIM': 'B10101','EXTENDED_DATA': 'B11001','STATUS_ON': 'B11011','STATUS_OFF': 'B11101','STATUS_REQUEST': 'B11111'}


class X10_Devices(Devices):
    house = models.CharField(max_length=1)
    unit = models.IntegerField()
    type = models.CharField(max_length=100, choices=X10_DEVICE_TYPES)
    modelNumber = models.CharField(max_length=100, choices=X10_KNOWN_MODELS)
    state = models.IntegerField(default=0)
    lastCommand = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        super(X10_Devices, self).save(*args, **kwargs)
        for modelNumber in X10_DEFAULT_USER_COMMANDS.keys():
            if self.modelNumber in modelNumber:
                for command in X10_DEFAULT_USER_COMMANDS[modelNumber]:
                    if not len(X10_Commands.objects.filter(device=self, name=command)):
                        newCommand = X10_Commands(name=command, device=self, code=123)
                        newCommand.save()

    def runCommand(self, command):
        try:
            dev = findX10Modem()
            ser = serial.Serial(dev, 9600)
            message = chr(int(HOUSE_CODES[self.house].replace('B', '0b0000'), 2))
            message += chr(int(UNIT_CODES[str(self.unit)].replace('B', '0b000'), 2))
            message += chr(int(COMMAND_CODES[command.name.upper()].replace('B', '0b000'), 2))
            ser.write(message)
            print 'Ran \'' + command.name + '\' on \'' + command.device.name + '\' (X10)'
            return True
        except:
            print 'FAILED to run \'' + command.name + '\' on \'' + command.device.name + '\' (X10)'
            return False

    def getState(self):
        return 1

class X10_DevicesForm(DevicesForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Fan, Lamp, etc.'}))
    house = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Any letter A-P'}))
    unit = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Any number 1-16'}))
    class Meta:
        model = X10_Devices
        exclude = ('state', 'lastCommand')

class X10_Commands(Commands):
   # modelNumber = models.ForeignKey(X10_Devices)
    code = models.IntegerField(null=True)

class X10_CommandsForm(CommandsForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. 1110211'}))
    class Meta:
        model = X10_Commands
        exclude = ('state', 'device', 'code', 'lastCommand')

def findX10Modem():
    for port in glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'):
        ser = serial.Serial(port, 9600)
        if ser.isOpen():
            ser.write('Who')
            if 'X10 Transceiver' in ser.readline():
                return port

################
# IR
################

class IR_Devices(Devices):
    modelNumber = models.CharField(max_length=100)

    def runCommand(self, command):
        print "called run command on IR"
        try:
            ser = serial.Serial(getIRDongle(), 9600)
            actualCommand = command.getSubclassInstance()
            print actualCommand.code
            ser.write(actualCommand.code)
            #response = str(ser.readline())
            #print response
            print 'Played Command Succesfully'
            return True
        except:
            print 'Failed to play'
            return False

class IR_DevicesForm(DevicesForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. TV, Stereo, etc.'}))
    modelNumber = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. abc123'}))
    class Meta:
        model = IR_Devices

class IR_Commands(Commands):
    code = models.CharField(max_length=200)
    
    def getTransceiverID(self):
        transceiver = Transceivers.objects.filter(location=self.device.location)
        if transceiver:
            return transceiver[0].id
        else:
            return False

    def recordCommand(self, deviceID):
        transceiverID = self.getTransceiverID()
        if transceiverID:
            command = str(transceiverID) + 'rrr'
            try:
                ser = serial.Serial(getIRDongle(), 9600)
#                ser.flush()                
#                ser.flushInput()
#                ser.flushOutput()
                ser.write(command)
                print 'Recording...'
                self.code = str(ser.readline())
                print self.code
                print 'Recorded Command Succesfully'
                return True
            except:
                print 'Failed to record'
                return False
        else:
            print 'Couldn\'t find transceiver for device'
            return False

class IR_CommandsForm(CommandsForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. 1110211'}))
    class Meta:
        model = IR_Commands
        exclude = ('device',)

# This should get called on setup or if there are communication problems. maybe set the value in the db?
def getIRDongle():
#    return '/dev/tty.usbmodem1a21'
    return '/dev/ttyUSB0'



################
# IR Database (Alex Z)
################

class IR_Database_Entry(models.Model):
    manufacturer = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    command = models.CharField(max_length=100)
    normalized_command = models.CharField(max_length=100)
    code = models.CharField(max_length=1000)
    
    def parseFromLine(self, line):
        values = line.strip().split(',')
        self.manufacturer = values[0]
        self.model = values[1]
        self.command = values[2]
        self.normalized_command = values[3]
        self.code = values[4]

################
# Misc.
################

class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')
		
class UploadDatabaseForm(forms.Form):
    file = forms.FileField()

class UserPermissions(models.Model):
    user = models.ForeignKey(User)
    device = models.ForeignKey(Devices)

