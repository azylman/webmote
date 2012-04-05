from pprint import pprint
from django import forms
from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.http import HttpResponse
from django.forms.models import modelformset_factory
from django.core.context_processors import csrf
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import logout_then_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from webmote_django.webmote.models import *
import serial, sys, os
from django.utils import simplejson

# This allows the javascript locater to find the server
def identification(request):
    if request.method == 'GET':
        response = HttpResponse('webmote model #' + '12345')
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response['Access-Control-Max-Age'] = 1000
        response['Access-Control-Allow-Headers'] = '*'
        return response
    else:
        return render_to_response('fail.html')

@login_required
def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def runCommand(request, deviceNum="1", command="0"):
    device = Devices.objects.filter(id=int(deviceNum))[0].getSubclassInstance()
    context = {}    
    if not device.runCommand(command):
        context['error'] = "Command Failed to run"
    if 'error' not in context and hasattr(device, 'state'):
        device.state = int(command)
        device.save()
    return render_to_response('index.html')

@login_required
def userPermissions(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            permissions = simplejson.loads(request.raw_post_data)
            setUserPermissions(permissions)
        context = {}
        context['devices'] = Devices.objects.all()
        context['users'] = User.objects.all()
        return render_to_response('userPermissions.html', context, context_instance=RequestContext(request))

@login_required
def userPermissionsInfo(request, userID = "0"):
    if request.user.is_superuser:
        user = User.objects.filter(id=int(userID))[0]
        permissions = []
        for perm in UserPermissions.objects.filter(user=user):
            permissions.append(perm.device.id)
        return HttpResponse(simplejson.dumps(permissions), mimetype='application/javascript')

@login_required
def users(request, userID = "0"):
    if request.user.is_superuser:
        context = {}
        context['users'] = User.objects.all()
        context['newUserForm'] = UserForm()
        if request.method == 'POST':
            if 'addUser' in request.POST:
                form = UserForm(request.POST)
                if form.is_valid():
                    user = User.objects.create_user(form.instance.username, form.instance.email, form.instance.password)
                    user.first_name = form.instance.first_name
                    user.last_name = form.instance.last_name
                    user.save()
            if 'deleteUser' in request.POST:
                User.objects.filter(id=request.POST['deleteUser']).delete()
        return render_to_response('users.html', context, context_instance=RequestContext(request))

@login_required
def devices(request, room="all"):
    context = {}
    context['room'] = room
    if room == "all":
        context['devices'] = getAllowedDevices(request.user.id)
    else:
        context['devices'] = []
        for device in getAllowedDevices(request.user.id):
            if device.location == room:
                context['devices'].append(device)
    return render_to_response('devices_new.html', context, context_instance=RequestContext(request))

    
@login_required
def setup(request):
    if request.user.is_superuser:
        context = {}
        context['deviceTypes'] = []
        context['addDeviceForms'] = []
        for deviceType in Devices.__subclasses__():
            typeName = deviceType.__name__.replace('_Devices', '')
            context['addDeviceForms'].append([deviceType().getDeviceForm(), typeName])
            context['deviceTypes'].append(typeName)
            if request.method == 'POST':
                if 'new_' + typeName in request.POST:
                    deviceForm = deviceType().getDeviceForm()
                    newDevice = deviceForm(request.POST)
                    if newDevice.is_valid():
                        newDevice.save()
                elif 'deleteDevice' in request.POST:
                    Devices.objects.filter(id=request.POST['deleteDevice']).delete()
        context['devices'] = Devices.objects.all()
        return render_to_response('setup.html', context, context_instance=RequestContext(request))

@login_required
def device(request, num="1"):
    if request.user.is_superuser:
        context = {}
        device = Devices.objects.filter(id=int(num))[0]
        deviceForm = device.getDeviceForm()
        commandForm = device.getEmptyCommandsForm()
        if request.method == 'POST':
            if 'updateDevice' in request.POST:
                updatedDevice = deviceForm(request.POST, instance=device.getSubclassInstance())
                if updatedDevice.is_valid():
                    updatedDevice.save()
                else:
                    context['error'] = "New value(s) was invalid."
            elif 'addCommand' in request.POST:
                commandType = device.getCorrespondingCommandType()
                command = commandType(device=device)
                newCommand = commandForm(request.POST, instance=command)
                if newCommand.is_valid():
                    newCommand.save()
                else:
                    context['error'] = "Command was invalid."
            elif 'deleteCommand' in request.POST:
                Commands.objects.filter(id=request.POST['deleteCommand']).delete()
        device = Devices.objects.filter(id=int(num))[0]
        context['device'] = device
        context['deviceForm'] = deviceForm(instance=device.getSubclassInstance())
        context['commands'] = device.commands_set.all()
        context['commandForm'] = commandForm
        return render_to_response('device.html', context, context_instance=RequestContext(request))

@login_required
def rooms(request):
    context = {}
    context['rooms'] = []
    for device in getAllowedDevices(request.user.id):
        if not device.location in context['rooms']:
            context['rooms'].append(device.location)
    return render_to_response('rooms.html', context, context_instance=RequestContext(request))

@login_required
def custom_screen(request, screen_name = "default"):
    context = {}
    context['commands'] = Commands.objects.filter(id = Custom_Screens.objects.filter(name = screen_name))
    return render_to_response('custom_screen.html', context, context_instance=RequestContext(request))


##################
# Helper Functions 
##################

def getAllowedDevices(userID):
    if User.objects.filter(id=int(userID))[0].is_superuser:
        return Devices.objects.all()
    else:
        devices = []
        for perm in UserPermissions.objects.filter(user=int(userID)):
            devices.append(Devices.objects.filter(id=perm.device.id)[0])
        return devices

def setUserPermissions(permissions):
    for userID in permissions.keys():
        for permission in UserPermissions.objects.filter(user=int(userID)):
            permission.delete()
        for device in permissions[userID]:
            device = Devices.objects.filter(id=int(device))[0]
            user = User.objects.filter(id=int(userID))[0]
            UserPermissions(user=user, device=device).save()
    return True


#@login_required
#def devices(request):
#    context = {}
#    for deviceType in DEVICE_TYPES:
#        context[deviceType[0]] = Devices.objects.filter(type = deviceType[0])
##    context['devices_onoff'] = Devices.objects.filter(type = 'On-Off Light')
##    context['devices_dimmable'] = Devices.objects.filter(type = 'Dimmable Light')
#    if request.method == 'POST':
#        if 'saveProfile' in request.POST:
#            Profiles.objects.filter(profileName=request.POST['profileName']).delete()
#            for device in Devices.objects.all():
#                profile = Profiles(profileName=request.POST['profileName'], deviceID=device.id, deviceState=device.state)
#                profile.save()
#        if 'deleteProfile' in request.POST:
#            Profiles.objects.filter(profileName=request.POST['deleteProfile']).delete()
#        if 'loadProfile' in request.POST:
#            if request.POST['loadProfile'] == "All On":
#                Devices.objects.all().update(state=100)
#            if request.POST['loadProfile'] == "All Off":
#                Devices.objects.all().update(state=0)
#            else:
#                for profile in Profiles.objects.filter(profileName=request.POST['loadProfile']):
#                    device = Devices.objects.filter(id=profile.deviceID)[0]
#                    device.state = profile.deviceState
#                    device.save()
#    unique = []
#    for profile in Profiles.objects.all():
#        if not profile.profileName in unique:
#            unique.append(profile.profileName)
#    context['profiles'] = unique
#    return render_to_response('devices.html', context, context_instance=RequestContext(request))

