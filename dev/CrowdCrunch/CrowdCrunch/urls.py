from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from cruncher.views import *
from django.views.generic import TemplateView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CrowdCrunch.views.home', name='home'),
    # url(r'^/', include('cruncher.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/?logged_out=true'}),

    url(r'^$', LandingView.as_view()),
    url(r'^/users/new', TemplateView.as_view(template_name="home.html")),

    url(r'^admin/', include(admin.site.urls)),
)
