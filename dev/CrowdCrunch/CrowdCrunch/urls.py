from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from cruncher.views import *
from cruncher.jobs.views import TwilioView
from django.views.generic import TemplateView

from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CrowdCrunch.views.home', name='home'),
    # url(r'^/', include('cruncher.urls')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/?logged_out=true'}),

    url(r'^$', LandingView.as_view()),
    url(r'^dashboard$', login_required(DashboardView.as_view())),

    url(r'^jobs/new/$', login_required(CreateJobView.as_view())),
    url(r'^jobs/(?P<pk>\d+)$',  login_required(ViewJob.as_view()), name='job-view'),

    url(r'^profile/credit/$', login_required(CreditAccountView.as_view())),
    url(r'^profile/verify/$', login_required(VerifyPhoneView.as_view())),
    url(r'^profile/current$', login_required(CurrentJobView.as_view())),
    
    url(r'^receive-message/$', TwilioView.as_view()),

    url(r'^admin/', include(admin.site.urls)),
)
