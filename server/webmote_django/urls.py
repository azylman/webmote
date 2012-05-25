from django.conf.urls.defaults import patterns, include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     #url(r'^$', 'webmote.views.home', name='home'),
    url(r'^$', 'webmote_django.webmote.views.index'),
    # url(r'^webmote/', include('webmote_django.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Pages
    url(r'^accounts/login$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$','webmote_django.webmote.views.logout_view'),
    url(r'^run_command/(?P<deviceNum>\d+)/(?P<command>\d+)/$', 'webmote_django.webmote.views.runCommandView'),
    url(r'^bookmark/(?P<actionType>[\w|\W]+)/(?P<deviceID>\d+)/(?P<commandID>\d+)/$', 'webmote_django.webmote.views.bookmark'),
    url(r'^bookmark_actions/$', 'webmote_django.webmote.views.bookmarkActions'),
    url(r'^record_command/$', 'webmote_django.webmote.views.recordCommand'),
    url(r'^rooms/$', 'webmote_django.webmote.views.rooms'),
    url(r'^help/$', 'webmote_django.webmote.views.help'),
    url(r'^profiles/$', 'webmote_django.webmote.views.profiles'),
    url(r'^macros/$', 'webmote_django.webmote.views.macros'),
    url(r'^macro/(?P<macroID>\d+)/$', 'webmote_django.webmote.views.macro'),
    url(r'^macro/$', 'webmote_django.webmote.views.macro'),
    url(r'^devices/(?P<room>[\w|\W]+)$', 'webmote_django.webmote.views.devices'),
    url(r'^device/(?P<num>\d+)/$', 'webmote_django.webmote.views.device'),
    url(r'^users/$', 'webmote_django.webmote.views.users'),
    url(r'^user_permissions_info/(?P<userID>\d+)/$', 'webmote_django.webmote.views.userPermissionsInfo'),
    url(r'^get_action_info/$', 'webmote_django.webmote.views.getActionInfo'),
    url(r'^user_permissions/$', 'webmote_django.webmote.views.userPermissions'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^controller/$', 'webmote_django.webmote.views.index'),
    url(r'^setup/$', 'webmote_django.webmote.views.setup'),
    url(r'^user_setup/$', 'webmote_django.webmote.views.setup'),
    url(r'^logout/$', 'webmote_django.webmote.views.logout_view'),
    url(r'^identification/$', 'webmote_django.webmote.views.identification'),
	url(r'^db_admin/$', 'webmote_django.webmote.views.db_admin'),
   	url(r'^transceivers/$', 'webmote_django.webmote.views.transceivers'),
   	url(r'^transceiver_search/$', 'webmote_django.webmote.views.transceiverSearch'),
    url(r'^autocomplete/(?P<fieldType>[\w|\W]+)/$', 'webmote_django.webmote.views.autocomplete'),
    url(r'^button/(?P<remoteID>\d+)/(?P<y>\d+)/(?P<x>\d+)/$', 'webmote_django.webmote.views.newButton'),
    url(r'^button/(?P<buttonID>\d+)/$', 'webmote_django.webmote.views.editButton'),
    url(r'^run_button/command/(?P<commandID>\d+)/$', 'webmote_django.webmote.views.commandButton'),
    url(r'^run_button/(?P<buttonID>\d+)/$', 'webmote_django.webmote.views.runButton'),
    url(r'^remote/(?P<remoteID>\d+)/$', 'webmote_django.webmote.views.remote'),
    url(r'^device_remote/(?P<deviceID>\d+)/$', 'webmote_django.webmote.views.deviceRemote'),
    url(r'^remotes/$', 'webmote_django.webmote.views.remotes'),
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += staticfiles_urlpatterns()
