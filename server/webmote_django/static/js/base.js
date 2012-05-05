$(document).ready(function() {

    // Included for POSTS with jquery - DO NOT MODIFY (https://docs.djangoproject.com/en/dev/ref/contrib/csrf/)
    jQuery(document).ajaxSend(function(event, xhr, settings) {
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function sameOrigin(url) {
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    });



    $('a').attr('rel','external');

    $('.on_off_light').change(function() {
        var el = $(this).children('select');
        var deviceID = el.attr('id').split('-')[1];
        var state = el.attr('value') == "on" ? 1:0;
        $.ajax({
            url : '/setstate/' + deviceID + '/' + state,
        });
    });

    $('.dimmable_light').change(function() {
        var el = $(this).children('input');
        var deviceID = el.attr('id').split('-')[1];
        var state = el.attr('value');
        $.ajax({
            url : '/setstate/' + deviceID + '/' + state,
        });
    });

    $('#selectDeviceType').change(function() {
        var divID = 'div.deviceForm#' +$(this).val();
        $('div.deviceForm').each(function() {
            $(this).css("display", "none");
        });
        $(divID).css("display", "inline");
    });

    $('#user-0, #device-0').change(function () {
        $('input[id^=' + this.id.split('-')[0] + ']').attr('checked',this.checked).checkboxradio('refresh');
    });

    $('[id^=user-]').change(function () {
        if (this.id.split('-')[1] > 0) {
            // Determine howmany others are checked
            var numChecked = 0;
            var checkedID = 0;
            $('[id^=user-]').each(function(index) {
                if (this.id.split('-')[1] > 0 && this.checked) {
                    numChecked++;
                    checkedID = this.id.split('-')[1];
                }
            });
            if (numChecked == 1) {
                // Get information about user's current permissions
                $.getJSON('/user_permissions_info/' + checkedID + '/', function(data) {
                    for (i = 0; i < data.length; i++) {
                        $('#device-' + data[i]).attr('checked',true).checkboxradio('refresh');
                    }
                });
            }
            if (numChecked == 2 || numChecked== 0) {
                // Clear 
                $('[id^=device-]').attr('checked', false).checkboxradio('refresh');
            }
        }
    });

    $('#actionType').change(function() {
        $('#selectDeviceProfileMacro').fadeOut();
        $('#selectDeviceCommand').fadeOut();
        $('#newActionSave').fadeOut();
        var serverInfo = [$('#macroName').text() ,$(this).find("option:selected").val()];
        var options = getActionInfo(serverInfo);
        var htmlOptions = '<option value="----">----</option>';
        for (i = 0; i < options.length; i++) {
            htmlOptions += '<option value="' + options[i] + '">' + options[i] + '</options>';
        }
        $('select#deviceProfileMacro').html(htmlOptions).selectmenu('refresh', true);
        if (serverInfo[1] != '----') {
            $('#selectDeviceProfileMacro').fadeIn();
        }
    });

    $('select#deviceProfileMacro').change(function() {
        $('#selectDeviceCommand').fadeOut();
        if ($('#actionType').find("option:selected").val() == 'device') {
            var serverInfo = [$('#macroName').text() , 'commands', $('select#deviceProfileMacro').find("option:selected").val()];
            var options = getActionInfo(serverInfo);
            var htmlOptions = '<option value="----">----</option>';
            for (i = 0; i < options.length; i++) {
                htmlOptions += '<option value="' + options[i] + '">' + options[i] + '</options>';
            }
            $('select#deviceCommand').html(htmlOptions).selectmenu('refresh', true);
            $('#selectDeviceCommand').fadeIn();
            $('#newActionSave').fadeOut();
        } else {
            if ($('#deviceProfileMacro').find("option:selected").val() != '----') {
                $('#newActionSave').fadeIn();
            } else {
                $('#newActionSave').fadeOut();
            }
        }
    });

    $('select#deviceCommand').change(function() {
        if ($('#deviceCommand').find("option:selected").val() == '----') {
            $('#newActionSave').fadeOut();
        } else {
            $('#newActionSave').fadeIn();
        }
    });
});

function saveNewAction() {
    $.mobile.loadingMessage = 'Updating Macro';
    $.mobile.showPageLoadingMsg();
    // Post this actionType
    var data = [$('#macroName').text(), 
                $('#actionType').find("option:selected").val(), 
                $('#deviceProfileMacro').find("option:selected").val(),
                $('#deviceCommand').find("option:selected").val()];
    
    // Post this data to backend
    $.ajax({
        url: '/macro/',
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(data),
        dataType: 'text',
        success: function(result) {
            $.mobile.hidePageLoadingMsg();
        }
    });
    alert('not finished implemented saveNewAction()');
}

function getSelectedProfile() {
    return $('#selectProfile option:selected')[0].value;
}

function runCommand(url) {
    $.ajax({
        url : url,
    });
}

function getActionInfo(data) {
    return $.parseJSON( 
                $.ajax({
                    url: '/get_action_info/',
                    async: false,
                    type: 'POST',
                    contentType: 'application/json; charset=utf-8',
                    data: JSON.stringify(data),
                    dataType: 'text',
                    success: function(returned) {}
                }).responseText);
}

function savePermissions() {
    $.mobile.loadingMessage = 'Saving Permissions';
    $.mobile.showPageLoadingMsg();
    var permissions = {};
    $('[id^=user-]').each(function(index) {
        var userID = this.id.split('-')[1];
        if (userID > 0 && this.checked) {
            // Clear a users existing permissions
            permissions[userID] = [];
            $('[id^=device-]').each(function(index) {
                var deviceId = this.id.split('-')[1];
                if (deviceId > 0 && this.checked) {
                    permissions[userID].push(deviceId);
                }
            });
        }
    });
    // Post this data to backend
    $.ajax({
        url: '/user_permissions/',
        type: 'POST',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify(permissions),
        dataType: 'text',
        success: function(result) {
            $.mobile.hidePageLoadingMsg();
        }
    });
}

function recordCommand(deviceID) {
    $.mobile.loadingMessage = 'Aim remote at transceiver and press the button you want to record!';
    $.mobile.showPageLoadingMsg();

    // Get new commands's name (check that it isn't missing)
    var commandName = $('#recordCommandName').val();
    if (commandName == '') {
        $.mobile.hidePageLoadingMsg();
        alert('Please enter a name for the command.')
    } else {
        // POST request with the deviceID, the command's name
        $.ajax({
            url: '/record_command/',
            type: 'POST',
            contentType: 'application/json; charset=utf-8',
            data: JSON.stringify([deviceID, commandName]),
            dataType: 'text',
            success: function(result) {
                $.mobile.hidePageLoadingMsg();
                location.reload(true);
            }
        });
    }
}


function searchForTransceiver() {
    $.mobile.loadingMessage = 'Searching for a new transciever!';
    $.mobile.showPageLoadingMsg();
    //First make a request to read in all serial commands and look for ID_REQUEST
    $.ajax({
        url: '/transceiver_search/',
        timeout : 10000,
        async: true,
        type: 'GET',
        contentType: 'application/json; charset=utf-8',
        dataType: 'text',
        success: function(returned) {
            $.mobile.hidePageLoadingMsg();
            alert($.parseJSON(returned).deviceType);
            //Present From

        }
    });


}
