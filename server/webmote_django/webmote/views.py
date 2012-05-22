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
import serial, sys, os, signal
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

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def index(request):
    return render_to_response('index.html', context_instance=RequestContext(request))

@login_required
def help(request):
    return render_to_response('help.html', context_instance=RequestContext(request))

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
def bookmarkActions(request):
    context = {}
    context['devices'] = []
    for device in getAllowedDevices(request.user.id):
        device.commands = device.commands_set.all()
        context['devices'].append(device)
    context['macros'] = []
    macroNames = []
    for macro in Macros.objects.filter(user=request.user):
        if not macro.macroName in macroNames:
            context['macros'].append(macro)
            macroNames.append(macro.macroName)
    context['profiles'] = []
    profileNames = []
    for profile in Profiles.objects.filter(user=request.user):
        if not profile.profileName in profileNames:
            context['profiles'].append(profile)
            profileNames.append(profile.profileName)
    return render_to_response('bookmark_actions.html', context, context_instance=RequestContext(request))

@login_required
def bookmark(request, actionType, deviceID, commandID):
    context = {}
    context['name'] = performAction(request.user, actionType, deviceID, commandID)
    return render_to_response('bookmark.html', context, context_instance=RequestContext(request))

@login_required
def runCommandView(request, deviceNum="1", command="0"):
    # should be a permissions check here if it isn't already in the runcommand...
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
            return redirect('/macro/' + str(newMacro.id) + '/')
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
                profile = Profiles(user=request.user, profileName=request.POST['profileName'], device=device)
                if hasattr(device, 'state'):
                    profile.deviceState = device.state
                    profile.save()
                if hasattr(device, 'lastCommand'):
                    profile.lastCommand = device.lastCommand
                    profile.save()
        if 'deleteProfile' in request.POST:
            profileName = Profiles.objects.filter(id=request.POST['deleteProfile'])[0].profileName
            Profiles.objects.filter(profileName=profileName, user=request.user).delete()
        if 'loadProfile' in request.POST:
            profileName = Profiles.objects.filter(id=request.POST['loadProfile'])[0].profileName
            loadProfile(profileName)
    unique = []
    uniqueNames = []
    for profile in Profiles.objects.filter(user=request.user):
        if not profile.profileName in uniqueNames:
            unique.append(profile)
            uniqueNames.append(profile.profileName)
    context['profiles'] = unique
    return render_to_response('profiles.html', context, context_instance=RequestContext(request))

@login_required
def remote(request, remoteID):
    context = {}
    context['edit'] = True
    remote = Remote.objects.filter(id=remoteID)[0]
    buttons = []
    assignedButtons = Button.objects.filter(remote=remote)
    for row in range(0, remote.rows):
        buttons.append({})
    for button in assignedButtons:
        buttons[button.y][str(button.x)] = button
    if not len(assignedButtons):
        context['no_assigned_buttons'] = True
    remote.buttons = buttons
    context['remote'] = remote
    return render_to_response('remote.html', context, context_instance=RequestContext(request))
    
@login_required
def deviceRemote(request, deviceID):
    context = {}
    buttons = []
    context['edit'] = False
    device = Devices.objects.filter(id=deviceID)[0]
    commands = Commands.objects.filter(device=device)
    remote = Remote(name=device.name, style=1, user=request.user)
    numCommands = len(commands)
    print numCommands
    remote.rows = numCommands / 3
    if numCommands % 3:
        remote.rows += 1
    for row in range(0, remote.rows):
        buttons.append({})
        for col in range(0, 3):
            if row * 3 + col < numCommands:
                command = commands[row * 3 + col]
                buttons[row][col] = Button(name=command.name, icon='star', command=command, id='command/' + str(command.id))
    remote.buttons = buttons
    context['remote'] = remote
    return render_to_response('remote.html', context, context_instance=RequestContext(request))

@login_required
def remotes(request):
    context = {}
    if request.method == 'POST':
        if 'saveRemote' in request.POST:
            r = Remote(user=request.user)
            newRemote = RemoteForm(request.POST, instance=r)
            if newRemote.is_valid():
                newRemote.save()
        if 'deleteRemote' in request.POST:
            Remote.objects.filter(id=request.POST['deleteRemote']).delete()
            # delete related buttons here if nec.
    context['remotes'] = Remote.objects.filter(user=request.user)
    context['remoteForm'] = RemoteForm()
    return render_to_response('remotes.html', context, context_instance=RequestContext(request))

@login_required
def editButton(request, buttonID):
    context = {}
    if request.method == 'POST':
        if 'clearButton' in request.POST:
            b = Button.objects.filter(id=buttonID)[0]
            remoteID = b.remote.id
            b.delete()
            return redirect('/remote/' + str(remoteID) + '/')
    return render_to_response('button.html', context, context_instance=RequestContext(request))

@login_required
def newButton(request, remoteID, y, x):
    context = {}
    context['newButton'] = True
    if request.method == 'POST':
        data = simplejson.loads(request.raw_post_data)
        print data
        name = data[4]
        icon = data[5]
        remote = Remote.objects.filter(id=remoteID)[0]
        if data[1] == 'device':
            device = Devices.objects.filter(name=data[2])[0]
            command = Commands.objects.filter(name=data[3], device=device)[0]
            newButton = Button(name=name, x=x, y=y, command=command, icon=icon, remote=remote)
            newButton.save()
        if data[1] == 'profile':
            profile = Profiles.objects.filter(profileName=data[2])[0]
            newButton = Button(name=name, x=x, y=y, profile=profile, icon=icon, remote=remote)
            newButton.save()
        if data[1] == 'macro':
            macro = Macros.objects.filter(macroName=data[2])[0]
            newButton = Button(name=name, x=x, y=y, macro=macro, icon=icon, remote=remote)
            newButton.save()
        return redirect('/remote/' + str(remoteID) + '/')
    context['buttonForm'] = ButtonForm()
    return render_to_response('button.html', context, context_instance=RequestContext(request))

@login_required
def runButton(request, buttonID):
    b = Button.objects.filter(id=buttonID)[0]
    if b.macro:
       runMacro(b.macro.macroName, request.user)
    if b.profile:
        loadProfile(b.profile.profileName)
    if b.command:
        runCommand(b.command.device.id, b.command.id)
    return HttpResponse(simplejson.dumps(''), mimetype='application/javascript')

@login_required
def commandButton(request, commandID):
    command = Commands.objects.filter(id=commandID)[0]
    device = command.device
    runCommand(device.id, command.id)
    return HttpResponse(simplejson.dumps(''), mimetype='application/javascript')

@login_required
def autocomplete(request, fieldType):
    if 'location' in fieldType:
        locations = []
        q = request.GET[u'term']
        for d in Devices.objects.filter(location__icontains=q):
            if not d.location in locations:
                 locations.append(d.location)
        for t in Transceivers.objects.filter(location__icontains=q):
            if not t.location in locations:
                 locations.append(t.location)
        print q, locations
        return HttpResponse(simplejson.dumps(locations), mimetype='application/json')

################
# Admin Views
################

@login_required
def recordCommand(request):
    if request.user.is_superuser:
        if request.method == 'POST':
            newCommandInfo = simplejson.loads(request.raw_post_data)
            device = Devices.objects.filter(id=int(newCommandInfo[0]))[0]
            commandType = device.getCorrespondingCommandType()
            command = commandType(device=device, name=newCommandInfo[1])
            if command.recordCommand(device.id):
                command.save()
            print 'returned'
        return HttpResponse(simplejson.dumps(''), mimetype='application/javascript')
            
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
        commandType = device.getCorrespondingCommandType()
        command = commandType()
        if hasattr(command, 'recordCommand'):
            context['recordable'] = True
        return render_to_response('device.html', context, context_instance=RequestContext(request))
		
@login_required
def db_admin(request, userID = "0"):
    if request.user.is_superuser:
        context = {}
        context['uploadDbForm'] = UploadDatabaseForm()
        if request.method == 'POST':
            if 'uploadDb' in request.POST:
                form = UploadDatabaseForm(request.POST, request.FILES)
                if form.is_valid():
                    file = request.FILES['file']
                    for line in file:
                        newEntry = IR_Database_Entry()
                        newEntry.parseFromLine(line)
                        newEntry.save()
        return render_to_response('db_admin.html', context, context_instance=RequestContext(request))

@login_required
def transceivers(request):
    if request.user.is_superuser:
        context = {}
        if request.method == 'POST':
            if 'addTransceiver' in request.POST:
                newTForm = TransceiversForm(request.POST)
                if newTForm.is_valid():
                    newTran = newTForm.save()
                    newTran.assignID()
                else:
                    context['error'] = "Transciever was invalid."
            elif 'deleteTransceiver' in request.POST:
                Transceivers.objects.filter(id=request.POST['deleteTransceiver'])[0].delete()
            elif 'resetTransceivers' in request.POST:
                resetAllTransceivers()
        context['transceivers'] = Transceivers.objects.all()
        context['transceiversForm'] = TransceiversForm()
        return render_to_response('transceiver.html', context, context_instance=RequestContext(request))


@login_required
def transceiverSearch(request):
    if request.user.is_superuser:
        return searchForTransceiver()

##################
# Helper Functions 
##################

def searchForTransceiver():
    msg = False
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        msg = str(ser.readline())
    except Exception, exc:
        print str(exc)
    return HttpResponse(simplejson.dumps({'deviceType' : msg.split('_')[0] }), mimetype='application/javascript')

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

def performAction(user, actionType, deviceID, commandID):
    if 'command' in actionType:
        runCommand(deviceID, commandID)
        actionName = Devices.objects.filter(id=deviceID)[0].name + ' - '
        actionName += Commands.objects.filter(id=commandID)[0].name
        return actionName
    if 'macro' in actionType:
        actionName = Macros.objects.filter(id=deviceID)[0].macroName
        runMacro(actionName, user)
        return actionName
    if 'profile' in actionType:
        actionName = Profiles.objects.filter(id=deviceID)[0].profileName
        loadProfile(actionName)
        return actionName

def runCommand(deviceNum, commandNum):
    context = {}
    device = Devices.objects.filter(id=int(deviceNum))
    command = Commands.objects.filter(id=int(commandNum))
    if device and command:
        device = device[0].getSubclassInstance()
        if not device.runCommand(command[0]):
            context['error'] = "Command Failed to run"
        if 'error' not in context and hasattr(device, 'state'):
            device.state = device.getState()
            device.save()
        if 'error' not in context and hasattr(device, 'lastCommand'):
            device.lastCommand = commandNum
            device.save()
    else:
        context['error'] = "Command Failed to run"
    return context

def runMacro(macroName, user):
    for macro in Macros.objects.filter(user=user, macroName=macroName).order_by('id'):
        if macro.runnable():
            if macro.macro:
                runMacro(macro.macro.macroName, user)
            if macro.profile:
                loadProfile(macro.profile.profileName)
            if macro.command:
                runCommand(macro.command.device.id, macro.command.id)

def loadProfile(profileName):
    for profile in Profiles.objects.filter(profileName=profileName):
        runCommand(profile.device.id, profile.lastCommand)

def resetAllTransceivers():
    Transceivers.objects.all().delete()
    try:
#        ser = serial.Serial('/dev/ttyACM0', 9600)
        ser = serial.Serial('/dev/ttyUSB0', 9600)
        ser.write('reset')
    except Exception, exc:
        print str(exc)
    
