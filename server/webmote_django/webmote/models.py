from django.db import models
from django.forms import ModelForm

DEVICE_TYPES = (
    ('X10 Device', 'X10 Device'),
    ('IR Device', 'IR Device'),
    ('Zigbee Device', 'Zigbee Device'),
)

################
# Webmote Device
################
# https://docs.djangoproject.com/en/dev/topics/db/models/#differences-between-proxy-inheritance-and-unmanaged-models --need to read up on this


class Devices(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)


# need to make the location a drop down of existing locations with an option to create a new one
class DeviceForm(ModelForm):
    class Meta:
        model = Devices

################
# X10
################

X10_DEVICE_TYPES = (
    ('On-Off Light', 'On-Off Light'),
    ('Dimmable Light', 'Dimmable Light'),
)

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
    def get_fields(self):
        return [(field.name.capitalize(), field.value_to_string(self)) for field in Devices._meta.fields]            

    def __unicode__(self):
        return self.house + str(self.unit) + '\n' + self.name + '\n' + self.modelNumber

class X10_Form(ModelForm):
    class Meta:
        model = X10_Devices
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
        model = X10_Commands

class X10_PartialCommandForm(ModelForm):
    class Meta:
		model = X10_Commands
		fields = ('name','value')

class X10_Profiles(models.Model):
    profileName = models.CharField(max_length=100)
    deviceID = models.IntegerField()
    deviceState = models.IntegerField()

################
# IR
################
class IR_Devices(Devices):
    model = models.CharField(max_length=100)
    #model = models.IR_Device_Database()



################
# IR Database (Alex Z)
################
