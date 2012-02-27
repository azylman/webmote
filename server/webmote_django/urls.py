from django.conf.urls.defaults import patterns, include, url

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

    url(
        r'^accounts/login/$','django.contrib.auth.views.login',
        dict(
            template_name = 'jqm/login.html',
        ),
        name='login',
    ),
    url(
        r'^accounts/logout/$','django.contrib.auth.views.logout',
        dict(
            template_name = 'jqm/logout.html',
        ),
        name='logout',
    ),

    # Pages
    url(r'^setstate/(?P<num>\d+)/(?P<state>\d+)/$', 'webmote_django.webmote.views.setState'),
    url(r'^devices/$', 'webmote_django.webmote.views.devices'),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^controller/$', 'webmote_django.webmote.views.index'),
    url(r'^setup/$', 'webmote_django.webmote.views.setup'),
    url(r'^device/(?P<num>\d+)/$', 'webmote_django.webmote.views.device'),
    url(r'^logout/$', 'webmote_django.webmote.views.logout_view'),



)
