from django.db import models
from django.forms import ModelForm

DEVICE_TYPES = (
    ('On-Off Light', 'On-Off Light'),
    ('Dimmable Light', 'Dimmable Light'),
)

class Devices(models.Model):
    house = models.CharField(max_length=1)
    unit = models.IntegerField()
    type = models.CharField(max_length=100, choices=DEVICE_TYPES)
    location = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    modelNumber = models.CharField(max_length=30)
    state = models.IntegerField(default=0)
    def get_fields(self):
        return [(field.name.capitalize(), field.value_to_string(self)) for field in Devices._meta.fields]            

    def __unicode__(self):
        return self.house + str(self.unit) + '\n' + self.name + '\n' + self.modelNumber

class DeviceForm(ModelForm):
    class Meta:
        model = Devices
        exclude = ('state',)

class Profiles(models.Model):
    profileName = models.CharField(max_length=100)
    deviceID = models.IntegerField()
    deviceState = models.IntegerField()

class Commands(models.Model):
    modelNumber = models.ForeignKey(Devices)
    name = models.CharField(max_length=100)
    value = models.IntegerField()
    def get_fields(self):
        return [(field.name.capitalize(), field.value_to_string(self)) for field in Commands._meta.fields] 

    def __unicode__(self):
        return str(self.command)

class CommandForm(ModelForm):
    class Meta:
        model = Commands

class PartialCommandForm(ModelForm):
    class Meta:
		model = Commands
		fields = ('name','value')
