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
        });

        function getSelectedProfile() {
            return $('#selectProfile option:selected')[0].value;
        }

        function runCommand(url) {
            $.ajax({
                url : url,
            });
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

	    $(document).live("mobileinit", function(){
	      $.mobile.ajaxFormsEnabled = false;
	    });

	    $(document).live("mobileinit", function(){
	      $.mobile.ajaxLinksEnabled = false;
	    });
