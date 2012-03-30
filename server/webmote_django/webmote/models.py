from django.db import models
from django.forms import ModelForm
from django import forms

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

    def getEmptyCommandsForm(self):
        for commandsFormType in CommandsForm.__subclasses__():
            typeName = commandsFormType.__name__.replace('_CommandsForm', '')
            if typeName in type(self.getSubclassInstance()).__name__.replace('_Devices', ''):
                return commandsFormType
        return False
        
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
    class Meta:
        model = Commands
    
################
# X10
################

X10_DEVICE_TYPES = (
    ('On-Off Light', 'On-Off Light'),
    ('Dimmable Light', 'Dimmable Light'),
)

# Will probably put some popular models in
X10_KNOWN_MODELS = (
    ('Socket Rocket', 'abc123'),
    ('Socket Rocket Dimmer', '123abc'),
)

class X10_Devices(Devices):
    house = models.CharField(max_length=1)
    unit = models.IntegerField()
    type = models.CharField(max_length=100, choices=X10_DEVICE_TYPES)
    modelNumber = models.CharField(max_length=100, choices=X10_KNOWN_MODELS)
    state = models.IntegerField(default=0)

class X10_Commands(Commands):
   # modelNumber = models.ForeignKey(X10_Devices)
    code = models.IntegerField()

class X10_CommandsForm(CommandsForm):
    class Meta:
        model = X10_Commands
        exclude = ('state', 'device')

class X10_Profiles(models.Model):
    profileName = models.CharField(max_length=100)
    deviceID = models.IntegerField()
    deviceState = models.IntegerField()

################
# IR
################
class IR_Devices(Devices):
    modelNumber = models.CharField(max_length=100)

class IR_Commands(Commands):
    code = models.IntegerField()

class IR_CommandsForm(CommandsForm):
    class Meta:
        model = IR_Commands
        exclude = ('device',)

################
# IR Database (Alex Z)
################
    
