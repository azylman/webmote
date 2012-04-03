from django.db import models
from django.forms import ModelForm
from django import forms
from django.forms.widgets import TextInput, PasswordInput
from django.contrib.auth.models import User


class UserForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ('username','email','password', 'first_name', 'last_name')

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

    def runCommand(self, command):
        print "called run command on X10"
        if True:
            return True
        else:
            return False

class X10_DevicesForm(DevicesForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. Fan, Lamp, etc.'}))
    house = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Any letter A-P'}))
    unit = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Any number 1-16'}))
    class Meta:
        model = X10_Devices
        exclude = ('state',)

class X10_Commands(Commands):
   # modelNumber = models.ForeignKey(X10_Devices)
    code = models.IntegerField()

class X10_CommandsForm(CommandsForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. 1110211'}))
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

    def runCommand(self, command):
        print "called run command on IR"
        if True:
            return True
        else:
            return False

class IR_DevicesForm(DevicesForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. TV, Stereo, etc.'}))
    modelNumber = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. abc123'}))
    class Meta:
        model = IR_Devices

class IR_Commands(Commands):
    code = models.IntegerField()

class IR_CommandsForm(CommandsForm):
    code = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'e.g. 1110211'}))
    class Meta:
        model = IR_Commands
        exclude = ('device',)

################
# IR Database (Alex Z)
################
    
