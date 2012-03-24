from django.db import models
from django.forms import ModelForm

DEVICE_TYPES = (
    ('X10 Device', 'X10 Device'),
    ('IR Device', 'IR Device'),
    ('Zigbee Device', 'Zigbee Device'),
)

X10_TYPES = (
    ('On-Off Light', 'On-Off Light'),
    ('Dimmable Light', 'Dimmable Light'),
)


################
# Webmote Device
################
class Devices(models.Model):
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

################
# X10
################
class X10_Devices(models.webmote.Devices):
    house = models.CharField(max_length=1)
    unit = models.IntegerField()
    type = models.CharField(max_length=100, choices=DEVICE_TYPES)
    modelNumber = models.
    state = models.IntegerField(default=0)
    def get_fields(self):
        return [(field.name.capitalize(), field.value_to_string(self)) for field in Devices._meta.fields]            

    def __unicode__(self):
        return self.house + str(self.unit) + '\n' + self.name + '\n' + self.modelNumber

class X10_Form(ModelForm):
    class Meta:
        model = Devices
        exclude = ('state',)

class X10_Commands(models.Model):
    modelNumber = models.ForeignKey(Devices)
    name = models.CharField(max_length=100)
    value = models.IntegerField()
    def get_fields(self):
        return [(field.name.capitalize(), field.value_to_string(self)) for field in Commands._meta.fields] 

    def __unicode__(self):
        return str(self.command)

class X10_CommandForm(ModelForm):
    class Meta:
        model = Commands

class X10_PartialCommandForm(ModelForm):
    class Meta:
		model = Commands
		fields = ('name','value')

class X10_Profiles(models.Model):
    profileName = models.CharField(max_length=100)
    deviceID = models.IntegerField()
    deviceState = models.IntegerField()

################
# IR
################
class IR_Devices(models.webmote.Devices):
    model = models.IR_Device_Database()



################
# IR Database (Alex Z)
################
