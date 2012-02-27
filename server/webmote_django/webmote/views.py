from django import forms
from django.template import RequestContext
from django.http import HttpResponse
from django.forms.models import modelformset_factory
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.decorators import login_required
from webmote_django.webmote.models import *

@login_required
def index(request):
    return render_to_response('index.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def setState(request, num="1", state="0"):
    device = Devices.objects.filter(id=int(num))[0]
    device.state = int(state)
    device.save()
    # Dispatch command to appropriate device
    return render_to_response('index.html')

@login_required
def devices(request):
    context = {}
    context['devices_onoff'] = Devices.objects.filter(type='On-Off Light')
    context['devices_dimmable'] = Devices.objects.filter(type='Dimmable Light')
    if request.method == 'POST':
        if 'saveProfile' in request.POST:
            Profiles.objects.filter(profileName=request.POST['profileName']).delete()
            for device in Devices.objects.all():
                profile = Profiles(profileName=request.POST['profileName'], deviceID=device.id, deviceState=device.state)
                profile.save()
        if 'deleteProfile' in request.POST:
            Profiles.objects.filter(profileName=request.POST['deleteProfile']).delete()
        if 'loadProfile' in request.POST:
            if request.POST['loadProfile'] == "All On":
                Devices.objects.all().update(state=100)
            if request.POST['loadProfile'] == "All Off":
                Devices.objects.all().update(state=0)
            else:
                for profile in Profiles.objects.filter(profileName=request.POST['loadProfile']):
                    device = Devices.objects.filter(id=profile.deviceID)[0]
                    device.state = profile.deviceState
                    device.save()
    unique = []
    for profile in Profiles.objects.all():
        if not profile.profileName in unique:
            unique.append(profile.profileName)
    context['profiles'] = unique
    return render_to_response('devices.html', context, context_instance=RequestContext(request))

@login_required
def setup(request):
    context = {}
    context['form'] = DeviceForm()
    context['devices'] = Devices.objects.all()
    if request.method == 'POST':
        if 'newDevice' in request.POST:
            form = DeviceForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
            else:
                context['error'] = str('House must be a character, Unit must be a number, and all other fields must be filled in.')
        elif 'deleteDevice' in request.POST:
            Devices.objects.filter(id=request.POST['deleteDevice']).delete()
    return render_to_response('setup.html', context, context_instance=RequestContext(request))

@login_required
def device(request, num="1"):
    context = {}
    context['device'] = Devices.objects.filter(id=int(num))[0]
    if request.method == 'POST':
        if 'updateDevice' in request.POST:
            form = DeviceForm(request.POST, instance=context['device'])
            if form.is_valid():
                form.save()
            else:
                context['error'] = str('House must be a character, Unit must be a number, and all other fields must be filled in.')
        elif 'addCommand' in request.POST:
            # Seems like there should be a cleaner way of doing this...
            form = PartialCommandForm(request.POST)
            command = Commands(modelNumber=context['device'], name=request.POST['name'], value=request.POST['value'])
            if form.is_valid():
                command.save()
    #            form.save()
            else:
                context['error'] = str('Name should be a short name for the command, Value is the integer representation of the x10 command')
        elif 'deleteCommand' in request.POST:
            Commands.objects.filter(id=request.POST['deleteCommand']).delete()
    context['device_form'] = DeviceForm(instance=context['device'])
    context['command_form'] = PartialCommandForm()
    context['commands'] = Commands.objects.filter(modelNumber=context['device'])
    return render_to_response('device.html', context, context_instance=RequestContext(request))

@login_required
def ir(request):
    context = {}
    testMessage = "Testing 123 Testing 123"
    if IRSend(testMessage):
        context['command'] = "Testing 123 Testing 123"
    return render_to_response('ir.html', context, context_instance=RequestContext(request))

# This could be seperated from the views eventually because it really isn't related to generating a web page.
def x10Send():
    return "command not sent"

def IRSend(command):
    try:
        import serial, sys, os
        ser = serial.Serial('/dev/ttyUSB0', 9600) # this should pull the location of the xbee from the db
        ser.write(command)
        return 1
    except:
        determineIRPort()
        return False


# This should get called on setup or if there are communication problems. maybe set the value in the db?
def determineIRPort():
    return '/dev/ttyUSB0'



