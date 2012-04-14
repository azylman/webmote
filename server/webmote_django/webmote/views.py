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
def getActionInfo(request):
    data = simplejson.loads(request.raw_post_data)
    if data[1] == 'device':
        deviceNames = []
        for device in getAllowedDevices(request.user.id):
            deviceNames.append(device.name)
        return HttpResponse(simplejson.dumps(deviceNames), mimetype='application/javascript')
    if data[1] == 'commands':
        commandNames = []
        device = Devices.objects.filter(name=data[2])[0]
        for command in Commands.objects.filter(device=device):
            commandNames.append(command.name)
        return HttpResponse(simplejson.dumps(commandNames), mimetype='application/javascript')
    if data[1] == 'profile':
        profileNames = []
        profileNames.append('All On')
        profileNames.append('All Off')
        for profile in Profiles.objects.filter(user=request.user):
            if not profile.profileName in profileNames:
                profileNames.append(profile.profileName)
        return HttpResponse(simplejson.dumps(profileNames), mimetype='application/javascript')
    if data[1] == 'macro':
        macroNames = []
        for macro in Macros.objects.filter(user=request.user):
            if not macro.macroName in macroNames and not macro.macroName in data[0]:
                macroNames.append(macro.macroName)
        return HttpResponse(simplejson.dumps(macroNames), mimetype='application/javascript')
    return HttpResponse(simplejson.dumps(''), mimetype='application/javascript')


@login_required
def runCommandView(request, deviceNum="1", command="0"):
    context = runCommand(deviceNum, command)
    return render_to_response('index.html', context, context_instance=RequestContext(request))

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

@login_required
def macro(request, macroID="0"):
    context = {}
    context['macroName'] = ''
    if request.method == 'POST':
        data = simplejson.loads(request.raw_post_data)
        data[0] = data[0].replace('\n', '')
        context['macroName'] = data[0]
        if data[1] == 'device':
            device = Devices.objects.filter(name=data[2])[0]
            command = Commands.objects.filter(name=data[3], device=device)[0]
            newMacroAction = Macros(macroName=data[0], command=command, user=request.user)
            newMacroAction.save()
        if data[1] == 'profile':
            if data[2] == 'All On' or data[2] == 'All Off':
                print "This is not figure out yet!!!!!!!!!!!!!!!!!!!!!"
            else:
                profile = Profiles.objects.filter(profileName=data[2])[0]
                newMacroAction = Macros(macroName=data[0], profile=profile, user=request.user)
                newMacroAction.save()
        if data[1] == 'macro':
            macro = Macros.objects.filter(macroName=data[2])[0]
            newMacroAction = Macros(macroName=data[0], macro=macro, user=request.user)
            newMacroAction.save()
    else:
        context['macroName'] = Macros.objects.filter(id=macroID)[0].macroName
    context['macros'] = Macros.objects.filter(macroName=context['macroName']).order_by('id')
    return render_to_response('macro.html', context, context_instance=RequestContext(request))

@login_required
def macros(request):
    context = {}
    if request.method == 'POST':
        if 'saveMacro' in request.POST:
            newMacro = Macros(macroName=request.POST['macroName'], user=request.user)
            newMacro.save()
            #return redirect('/macro/' + str(newMacro.id) + '/')
            # this redirection behavior would be great but jqm cant handle it :-(
        if 'deleteMacro' in request.POST:
            Macros.objects.filter(macroName=request.POST['deleteMacro'], user=request.user).delete()
        if 'runMacro' in request.POST:
            runMacro(request.POST['runMacro'], request.user)
    unique = []
    uniqueNames = []
    for macro in Macros.objects.filter(user=request.user):
        if not macro.macroName in uniqueNames:
            unique.append(macro)
            uniqueNames.append(macro.macroName)
    context['macros'] = unique
    return render_to_response('macros.html', context, context_instance=RequestContext(request))

@login_required
def profiles(request):
    context = {}
    if request.method == 'POST':
        if 'saveProfile' in request.POST:
            for abstractDevice in getAllowedDevices(request.user.id):
                device = abstractDevice.getSubclassInstance()
                if hasattr(device, 'state'):
                    profile = Profiles(user=request.user, profileName=request.POST['profileName'], device=device, deviceState=device.state)
                    profile.save()
        if 'deleteProfile' in request.POST:
            Profiles.objects.filter(profileName=request.POST['deleteProfile'], user=request.user).delete()
        if 'loadProfile' in request.POST:
            loadProfile(request.user.id, request.POST['loadProfile'], request)

    unique = []
    uniqueNames = []
    for profile in Profiles.objects.filter(user=request.user):
        if not profile.profileName in uniqueNames:
            unique.append(profile)
            uniqueNames.append(profile.profileName)
    context['profiles'] = unique
    return render_to_response('profiles.html', context, context_instance=RequestContext(request))

################
# Admin Views
################

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
def db_admin(request, userID = "0"):
    if request.user.is_superuser:
        context = {}
        context['uploadDbForm'] = UploadDatabaseForm()
        if request.method == 'POST':
            print >>sys.stderr, 'Page contains post data'
            if 'uploadDb' in request.POST:
                print >>sys.stderr, 'Page contains uploadDb form submission'
                form = UploadDatabaseForm(request.POST, request.FILES)
                print >>sys.stderr, 'Form is valid:', form.is_valid()
                if form.is_valid():
                    print >>sys.stderr, 'Page contains valid form'
                    file = request.FILES['file']
                    for line in file:
                        newEntry = IR_Database_Entry()
                        newEntry.parseFromLine(line)
                        newEntry.save()
        return render_to_response('db_admin.html', context, context_instance=RequestContext(request))

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

def runCommand(deviceNum, commandNum):
    context = {}
    devices = Devices.objects.filter(id=int(deviceNum))
    command = Commands.objects.filter(id=int(commandNum))[0]
    if devices:
        device = devices[0].getSubclassInstance()
        if not device.runCommand(command):
            context['error'] = "Command Failed to run"
        if 'error' not in context and hasattr(device, 'state'):
            #device.state = getState()
            device.state = 1
            device.save()
    else:
        context['error'] = "Command Failed to run"
    return context

def runMacro(macroName, user):
    for macro in Macros.objects.filter(user=user, macroName=macroName).order_by('id'):
        if macro.runnable():
            if macro.macro:
                runMacro(macro.macro.macroName, user)
            else:
                runCommand(macro.command.device.id, macro.command.id)


def loadProfile(userID, profileName, request):
    for abstractDevice in getAllowedDevices(userID):
        device = abstractDevice.getSubclassInstance()
        if hasattr(device, 'state'):
            if profileName == "All On":
                print "All On"
                runCommand(device.id, 100)
            if profileName == "All Off":
                print "All Off"
                runCommand(device.id, 0)
            else:
                profile = Profiles.objects.filter(profileName=profileName, device=abstractDevice)
                if profile:
                    runCommand(device.id, profile[0].deviceState)